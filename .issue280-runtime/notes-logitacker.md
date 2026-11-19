# Source notes: LOGITacker (RoganDawes/LOGITacker, master)

All paths relative to repo root. Code governs.

## Frame format (logitacker/logitacker_unifying.h, logitacker_unifying.c)
- RF payload byte 0 = device prefix/index byte; byte 1 = report type:
  low 5 bits (mask 0x1f) = type, bit 0x40 = keep-alive flag, bit 0x80 = "unknown".
- Report types: 0x01 plain keyboard, 0x02 plain mouse, 0x03 multimedia,
  0x04 system control, 0x0e LED (receiver->device), 0x0f set-keep-alive,
  0x10 HID++ short, 0x11 HID++ long, 0x13 encrypted keyboard,
  0x1b encrypted HID++ long, 0x1f pairing. Type 0x00 + keep-alive bit =
  empty keep-alive frame.
- Last payload byte = Logitech checksum: two's complement of the sum of all
  preceding bytes (sum over whole frame incl. checksum == 0 mod 256).
  Validation in the wild tolerates an LSB error (validate_checksum accepts
  chksum & 0xfe) - logitacker_unifying.c:12-34.
- Global pairing address (logitacker_unifying.h:33):
  {0xbb, 0x0a, 0xdc, 0xa5, 0x75} (5 bytes).
- Address split (logitacker/helper.c helper_addr_to_base_and_prefix):
  address bytes 0..3 = base (stored reversed in nRF regs), byte 4 = prefix
  (the ESB pipe prefix). Address length = 5 bytes.

## ESB / radio (esb_illegalmod/nrf_esb_illegalmod.h NRF_ESB_DEFAULT_CONFIG;
## logitacker_radio.c; processor_pair_device.c init)
- Protocol ESB_DPL (dynamic payload length), bitrate 2 Mbps, CRC 16-bit,
  max payload 32 bytes, auto-ACK on (selective_auto_ack=false).
- Default retransmit: delay 250 us, count 3. Pairing processor overrides:
  retransmit_count=1, delay 250 us, plus "all-channel TX failover" -
  retransmit the payload on every channel of the pairing table, 2 loops,
  before failing; TX delay between pairing frames 8 ms; up to 10 failed
  retransmits -> pairing aborted (PAIR_DEVICE_RETRANSMIT_BEFORE_FAIL).
- Channel tables (nrf_esb_illegalmod.c:2606-2640), values are nRF24 RF
  channel numbers (freq = 2400 + n MHz):
  - Unifying normal: 25 ch {5,8,11,...,77} (step 3).
  - Unifying pairing: 11 ch {62,8,35,65,14,41,71,17,44,74,5}.
  - (Lightspeed tables exist separately; out of scope.)
- During pairing LOGITacker stops channel hopping and works as PTX;
  responses from the receiver arrive as ACK payloads (device polls by
  sending "pull" frames - see state machine).

## Pairing state machine (logitacker_processor_pair_device.c)
Device = PTX. Receiver answers in ACK payloads; after each request the
device sends a 5-byte "pull" frame (type 0x40 keep-alive, byte2 = phase,
byte3 = address byte) to clock out the pending response.
Marker byte (payload byte 0): 0xe1 phase 1, 0xe2 phase 2, 0xe3 phase 3.

1. REQ1 (22 B, pipe 0 = pairing address): [0]=0xe1, [1]=0x5f (0x1f|0x40),
   [2]=0x01, [3..7]=device's current (pseudo) RF address,
   [8]=0x08 keep-alive interval (likely), [9..10]=device WPID,
   [11]=protocol 0x04 (Unifying), [12]=0x00 (kbd/mouse) - semantics partly
   unknown, [13]=device type, [14]=caps, [15]=?, [21]=checksum.
2. RSP1 (22 B, ACK payload): [0]=0xe1, [1]=0x1f, [2]=0x01,
   [3..7]=OFFERED device RF address (receiver-assigned), [9..10]=dongle
   WPID. Device adds the offered address as pipe 1, keeps pipe 0.
3. Address-accepted notice (5 B, still on pipe 0): [0]=0xe1, [1]=0x40,
   [2]=0x01, [3]=first byte of OLD address.
4. REQ2 (22 B, pipe 1 = offered address): [0]=0xe2, [1]=0x5f, [2]=0x02,
   [3..6]=device nonce (4 B; may be all zero if no link encryption),
   [7..10]=device serial (4 B, unique per device; receiver uses it to
   distinguish new device from re-paired device),
   [11..14]=supported report types bitfield, little endian,
   [15]=usability info (power-switch location).
5. RSP2 (22 B): [0]=0xe2, [1]=0x1f, [2]=0x02, [3..6]=dongle nonce (4 B),
   rest echoes REQ2. On receipt, if caps LINK_ENCRYPTION set: derive key.
6. REQ3 (22 B, pipe 1): [0]=0xe3, [1]=0x5f, [2]=0x03, [3]=0x01 (number of
   frames for full name), [4]=name length (<=16), [5..]=device name.
7. RSP final (10 B): [0]=0xe3, [1]=0x0f (set-keep-alive type), bytes 2..4
   expected 0x06,0x02,0x03 (not verified by LOGITacker), [5..6]=last two
   bytes of dongle nonce, [7..8]=first two bytes of device serial.
8. Final request (10 B, device->receiver): [0]=0xe2, [1]=0x4f
   (0x0f|0x40), [2]=0x06, [3]=0x01. TX success (ACK) => pairing SUCCEEDED.

Caps (logitacker_devices.h:58-59): bit0 (0x01) LINK_ENCRYPTION,
bit2 (0x04) UNIFYING_COMPATIBLE. Protocol ids: Unifying 0x04, Lightspeed
0x0C, G700 0x07. Report-types bitfield bits: keyboard 1<<1, mouse 1<<2,
multimedia 1<<3, power keys 1<<4, media center 1<<8, keyboard LED 1<<14,
short HID++ 1<<16, long HID++ 1<<17.

## Key derivation (logitacker_pairing_parser.c:44-76) - NO key transport
Raw key material (16 B) = device_rf_address[0..3] || device_WPID(2) ||
dongle_WPID(2) || device_nonce(4) || dongle_nonce(4).
AES key = fixed permutation of the raw material with XOR masks:
key[2]=raw[0]; key[1]=raw[1]^0xFF; key[5]=raw[2]^0xFF; key[3]=raw[3];
key[14]=raw[4]; key[11]=raw[5]; key[9]=raw[6]; key[0]=raw[7];
key[8]=raw[8]; key[6]=raw[9]^0x55; key[4]=raw[10]; key[15]=raw[11];
key[10]=raw[12]^0xFF; key[12]=raw[13]; key[7]=raw[14]; key[13]=raw[15]^0x55.
Both sides compute it locally from the exchanged values; the key itself is
never sent over the air. Derivation runs only when caps bit0
(LINK_ENCRYPTION) is set; otherwise nonces may be zero and traffic is plain.
Device must persist: assigned RF address, serial, WPIDs, nonces (or the
derived key directly), caps/report types. (LOGITacker stores exactly:
serial, name, key, raw key material, rf_address, wpid, caps, report_types
- pair_device.c success path.)

## Crypto (logitacker_unifying_crypto.c) - AES-128-ECB as keystream gen
- Frame key: AES-128-ECB encrypt, under the device key, of a fixed 16-byte
  constant "little known secret"
  {04 14 1d 1f 27 28 0d de ad be ef 0a 0d 13 26 0e} with bytes 7..10
  replaced by the 4-byte frame counter.
- Encrypted keyboard frame (type 0x13, total 22 B):
  [0]=index, [1]=0x13|flags (LOGITacker TX writes 0xd3),
  [2..9]=8 B ciphertext, [10..13]=counter (big-endian byte order in
  Unifying mode), [14..20]=0, [21]=checksum.
  Ciphertext = 8-byte plaintext HID keyboard report XOR frame_key[0..7]
  (only the first half of the AES output is used). Plaintext byte 7 (the
  last report byte, offset 9 in frame) is forced to 0xC9 before XOR -
  a known-plaintext marker the receiver can verify.
- Encrypted HID++ long frame (type 0x1b, total 30 B): two frame keys from
  counters n and n+1; 23 B plaintext (destination id + 18 B payload +
  4x0xC9 padding) XOR key1[0..15] then key2[0..6]; counter stored
  LITTLE-endian at offset 0x19..0x1c; [29]=checksum.
- No MAC/integrity beyond: the 0xC9 known-plaintext byte(s), the Logitech
  checksum byte, and ESB CRC16 on air. Counter extraction from a received
  encrypted keyboard frame: bytes 10..13 big-endian
  (logitacker_unifying.c extract_counter).
- Plain (unencrypted) keyboard report: RF frame type 0x01; the 8-byte HID
  report sits at frame bytes 2..9 (per encrypt path input layout).

## Keep-alive
- Any frame with bit 0x40 set doubles as keep-alive; type 0x00|0x40 =
  empty keep-alive. REQ1 byte 8 (0x08) is "likely default keep-alive
  interval" per code comment. Type 0x0f = set-keep-alive (receiver->device
  and pairing-final use). Exact interval semantics not pinned in this file.
