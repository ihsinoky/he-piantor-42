# Logitech Unifying device compatibility — consolidated spec (Issue #280)

Study only. Every claim is derived from primary source code/documents and
cited as (repo: path). Where sources disagree or are silent, that is stated.
"Device" = a keyboard implementing the Unifying device side; "receiver" =
a Logitech Unifying USB receiver (C-U0007/C-U0008 class, USB 046d:c52b).

Source shorthand: LT = RoganDawes/LOGITacker; MJ = BastilleResearch/
mousejack (+ nrf-research-firmware); SOL = pwr-Solaar/Solaar;
LOPS = PixlOne/logiops.

---

## 1. RF layer (ESB)

| Parameter | Pairing | Normal operation |
|---|---|---|
| PHY / protocol | Nordic ESB with dynamic payload length (ESB_DPL), 2 Mbps, CRC-16, max payload 32 B (LT: esb_illegalmod/nrf_esb_illegalmod.h `NRF_ESB_DEFAULT_CONFIG`) | same |
| Address | Global pairing address `BB 0A DC A5 75` (LT: logitacker/logitacker_unifying.h:33), pipe 0 | Receiver-assigned 5-byte device address learned in pairing RSP1 |
| Address structure | 5 bytes: bytes 0–3 = base address, byte 4 = pipe prefix (LT: logitacker/helper.c `helper_addr_to_base_and_prefix`) | same |
| Channels | 11-channel pairing table (nRF24 channel numbers, f = 2400+n MHz): {62, 8, 35, 65, 14, 41, 71, 17, 44, 74, 5} (LT: esb_illegalmod/nrf_esb_illegalmod.c `nrf_esb_update_channel_frequency_table_unifying_pairing`) | 25-channel table {5, 8, 11, …, 77} step 3 (LT: ibid. `..._unifying`) |
| ACK / retransmission | Auto-ACK with ACK payloads — receiver responses are delivered as ACK payloads; the device clocks them out with short "pull" frames (LT: logitacker/logitacker_processor_pair_device.c). ESB retransmit count 1, delay 250 µs, and the sender cycles the frame over all pairing channels (2 loops) before giving up; pairing frames are spaced 8 ms; ~10 failed retransmits abort pairing (LT: ibid. init + `PAIR_DEVICE_RETRANSMIT_BEFORE_FAIL`). MJ's firmware independently enables EN_DPL \| EN_ACK_PAY for transmit (MJ: nrf-research-firmware/src/radio.c:420-421) | Auto-ACK on; generic ESB default retransmit count 3 / 250 µs (LT: esb_illegalmod default config). The receiver hops channels; a device finds it by cycling the channel table (the receiver listens across the table; exact hop timing is receiver-internal — see Open Items) |

Notes:
- Payload byte 0 is a per-device prefix/index byte; byte 1 is the report
  type (see §4). The last payload byte is the "Logitech checksum":
  two's complement of the sum of all preceding bytes, so the whole frame
  sums to 0 mod 256 (LT: logitacker/logitacker_unifying.c:12-34).
  LOGITacker's validator also accepts a checksum whose LSB is flipped —
  evidence that real traffic/receivers are not bit-strict on that bit.
- TX power is an implementation choice (LOGITacker uses +8 dBm); nothing
  in the sources makes it a compatibility parameter.

## 2. Pairing state machine

Precondition: the host opens the receiver's pairing lock (host→receiver
over USB, HID++ 1.0 register 0xB2 `RECEIVER_PAIRING`, action 0x01 open /
0x02 close / 0x03 unpair; SOL: lib/logitech_receiver/receiver.py
`set_lock`, hidpp10_constants.py `Registers`). Logitech host software
holds the lock open for a limited window; the receiver reports errors
back to the host, including DEVICE_TIMEOUT and SEQUENCE_TIMEOUT
(SOL: hidpp10_constants.py `PairingError`), so the exchange below is
time-boxed by the receiver.

The device is the ESB transmitter (PTX); every receiver answer arrives
as an ACK payload, pulled by a 5-byte keep-alive frame after each step
(LT: logitacker/logitacker_processor_pair_device.c). Payload byte 0 is a
phase marker: 0xE1 / 0xE2 / 0xE3 for phases 1 / 2 / 3.

1. **REQ1** (device→receiver, 22 B, on the pairing address):
   `[0]=0xE1, [1]=0x5F` (type 0x1F pairing | keep-alive bit),
   `[2]=0x01`, `[3..7]` = device's current (arbitrary/preliminary) RF
   address, `[8]=0x08` (keep-alive interval, semantics per code comment
   "likely"), `[9..10]` = device WPID, `[11]=0x04` (protocol = Unifying),
   `[12]=0x00` for keyboard/mouse (partly unknown semantics),
   `[13]` = device type (keyboard = 0x01; mouse 0x02, numpad 0x03,
   presenter 0x04, trackball 0x08, touchpad 0x09 — LT:
   logitacker/logitacker_devices.h), `[14]` = capabilities bitmask
   (bit0 0x01 = link encryption, bit2 0x04 = Unifying-compatible),
   `[21]` = checksum.
2. **RSP1** (receiver→device, 22 B, ACK payload): `[2]=0x01`,
   `[3..7]` = **the device RF address assigned by the receiver**,
   `[9..10]` = receiver ("dongle") WPID. The device additionally enables
   this address (pipe 1) while keeping the pairing address (pipe 0).
3. **Address-accepted notice** (device→receiver, 5 B, still on the
   pairing address): `[0]=0xE1, [1]=0x40, [2]=0x01, [3]` = first byte of
   the device's old address.
4. **REQ2** (22 B, on the assigned address): `[0]=0xE2, [2]=0x02`,
   `[3..6]` = **device nonce** (4 B; may be all-zero if the device does
   not use link encryption), `[7..10]` = **device serial** (4 B, unique
   per device — the receiver uses it to tell a new device from a
   re-pairing one), `[11..14]` = supported report-types bitfield (LE;
   keyboard bit = 1<<1, multimedia 1<<3, power keys 1<<4, keyboard LED
   1<<14, HID++ short 1<<16, HID++ long 1<<17), `[15]` = usability info
   (power-switch location).
5. **RSP2** (22 B): `[3..6]` = **receiver nonce** (4 B); the rest echoes
   REQ2. On receipt the device derives the link key (§3) if it declared
   the encryption capability.
6. **REQ3** (22 B): `[0]=0xE3, [2]=0x03, [3]=0x01` (name sent in one
   frame), `[4]` = device name length (≤16), `[5..]` = device name.
7. **RSP final** (receiver→device, 10 B): `[0]=0xE3, [1]=0x0F`
   (set-keep-alive type), bytes 2–4 expected `06 02 03`, `[5..6]` = last
   two bytes of the receiver nonce, `[7..8]` = first two bytes of the
   device serial — an echo-back consistency check.
8. **Final request** (device→receiver, 10 B): `[0]=0xE2, [1]=0x4F,
   [2]=0x06, [3]=0x01`. A successful (ACKed) transmission completes
   pairing.

Key origin/transfer: **the AES-128 key is never transmitted.** Both sides
derive it locally from values exchanged above (§3). (LT:
logitacker/logitacker_pairing_parser.c `logitacker_pairing_derive_key*`.)

The device must persist (LT: pair_device success path stores exactly
these): assigned RF address, device serial, device WPID, receiver WPID,
both nonces or equivalently the derived key + raw key material, caps,
report types, device name; plus the AES frame counter state (§3).

Re-pairing / receiver reset:
- Pairing state is stored **in the receiver** per slot (address, WPID,
  serial, kind, name — readable back via receiver info registers;
  SOL: hidpp10_constants.py `InfoSubRegisters` 0x2N/0x3N/0x4N).
  Unpairing is a host action on the receiver; the device is not
  notified — it simply stops being ACKed at its old address.
- A device that pairs again presents the same serial, which is how the
  receiver recognises a re-pair (LT: pair_device REQ2 comment). The
  receiver assigns the address in RSP1, so a re-pair may yield the same
  or a new address; the device must accept whatever RSP1 offers and
  re-derive the key from the fresh nonces.
- Known firmware caveat: Bastille's bastille-1 advisory documents
  receivers (fw 012.001.00019 / 012.003.00025) accepting pairing frames
  **without** the lock being open (MJ: doc/advisories/
  bastille-1.logitech.public.txt). A device implementation must not
  depend on this; whether a given target receiver requires the lock is
  a per-firmware property (see §5 and Open Items).

## 3. Crypto (link encryption)

Applies when the device sets caps bit0 in REQ1. Construction exactly as
implemented device-side in LT: logitacker/logitacker_unifying_crypto.c.

- **Key derivation** (no AES involved): raw key material (16 B) =
  `device_RF_address[0..3] ‖ device_WPID(2) ‖ receiver_WPID(2) ‖
  device_nonce(4) ‖ receiver_nonce(4)`. The AES-128 key is a fixed
  permutation of the raw material with three XOR masks:
  `key = [r7, r1^FF, r0, r3, r10, r2^FF, r9^55, r14, r8, r6, r12^FF,
  r5, r13, r15^55, r4, r11]` (indices into raw material; LT:
  logitacker_pairing_parser.c:57-76).
- **Frame keystream**: one AES-128-ECB block under the device key over a
  fixed 16-byte constant `04 14 1D 1F 27 28 0D DE AD BE EF 0A 0D 13 26
  0E` whose bytes 7–10 are replaced by the frame's 4-byte counter
  (`update_little_known_secret_counter`). The ciphertext is XORed with
  the first bytes of that block — a counter-mode-like construction
  built from ECB; there is no chaining and no MAC.
- **Encrypted keyboard frame** (RF type 0x13, 22 B total):
  `[0]` index, `[1]` = 0x13 | flags, `[2..9]` = 8-byte HID keyboard
  report XOR frame-key bytes 0–7, `[10..13]` = counter (big-endian byte
  order in Unifying mode), `[14..20]` = 0, `[21]` = checksum.
  Before encryption the plaintext report's last byte is forced to 0xC9 —
  a known-plaintext check byte for the receiver. Only the first 8 bytes
  of the AES block are used ("yes, only half of the key … is used",
  code comment).
- **Encrypted HID++ long frame** (RF type 0x1B, 30 B): 23 bytes
  (destination id + 18 payload bytes + 4×0xC9 padding) XORed with frame
  key of counter *n* (bytes 0–15) and of counter *n+1* (bytes 0–6);
  counter stored **little-endian** at offset 0x19. Note the endianness
  differs from the keyboard frame — an implementation must reproduce
  this asymmetry exactly.
- **Integrity**: no cryptographic integrity. Protection consists of the
  0xC9 known-plaintext byte(s), the Logitech checksum byte, ESB CRC-16
  on air, and counter monotonicity: LOGITacker tracks each device's
  `last_used_aes_ctr` and continues above observed counters when
  transmitting as that device (LT: logitacker/logitacker_devices.c,
  `logitacker_unifying_extract_counter_from_encrypted_keyboard_frame`),
  consistent with the receiver rejecting replayed/stale counters; the
  exact acceptance window is not in the sources (Open Items).
- If the device does **not** set the encryption capability, keyboard
  reports go in plaintext frames (type 0x01) and nonces may be zero.
  Whether a given receiver firmware *accepts* plaintext from a device
  is firmware-dependent (§5) — LOGITacker's own pairing profile sets
  the encryption capability "to account for MouseJack patched
  firmwares" (LT: logitacker/logitacker.c `logitacker_enter_mode_pair_device`).

## 4. Normal operation

**Over-air keyboard frame → USB report.** The RF payload is:
`[0]` device prefix/index, `[1]` report type | flags (bit 0x40 =
keep-alive, bit 0x80 = unspecified), `[2..]` report body, last byte =
Logitech checksum. For keyboards the body is the standard 8-byte boot
keyboard report (modifier, reserved, 6 keycodes) — plaintext in a
type-0x01 frame (10 B total) or encrypted in a type-0x13 frame (22 B,
§3). The receiver strips the RF header/checksum, decrypts if needed,
and emits the 8-byte report to the host as a USB HID keyboard report;
multimedia/power-key reports travel as types 0x03/0x04 declared in the
pairing report-types bitfield. Other RF frame types a keyboard will
see: 0x0E LED state from the receiver (10 B; Caps/Num/Scroll — must at
least be tolerated), 0x0F set-keep-alive, 0x10/0x11 HID++ short/long
(10 B / 22 B frames), 0x1B encrypted HID++ long (30 B).

**Keep-alive.** Any frame with bit 0x40 set doubles as a keep-alive; a
frame of type 0x00 with only that bit set is an empty keep-alive. The
device announces a keep-alive interval byte (0x08) in REQ1, and the
receiver can push set-keep-alive frames (type 0x0F) — the same type
used in the pairing-final messages. If the device goes silent beyond
the keep-alive window the receiver treats it as gone (host software
then shows it offline). The exact interval units/enforcement are not
pinned down in the sources (Open Items).

**Minimum HID++ behaviour.** Findings:
- The receiver itself speaks HID++ 1.0 **to the host** (registers,
  pairing info); that is not a device obligation.
- Nothing in the RF protocol requires the device to answer HID++
  before its keyboard reports are forwarded: LOGITacker's paired
  keyboard profile sends encrypted keyboard frames without implementing
  HID++ device responses, and its pairing report-types profile does not
  even declare the HID++ bits (LT: logitacker/logitacker.c pairing
  info — SHORT/LONG_HIDPP bits commented out). Host software (Solaar)
  pings devices over HID++ to decide "online" and to read name/battery;
  an unanswered ping makes the device *appear* offline in software and
  blocks feature configuration, but per the sources it does not stop
  keystroke forwarding (SOL: lib/logitech_receiver/device.py `ping`).
- If the device declares HID++ support, the exchanges it will meet are:
  protocol/version probing, feature discovery (HID++ 2.0: ROOT 0x0000,
  FEATURE_SET 0x0001, DEVICE_NAME 0x0005; battery via BATTERY_STATUS
  0x1000 / BATTERY_VOLTAGE 0x1001 — LOPS:
  src/logid/backend/hidpp20/feature_defs.h), or HID++ 1.0 register
  reads (e.g. battery status register 0x07, firmware 0xF1 — SOL:
  hidpp10_constants.py `Registers`). A minimal-risk profile is to pair
  as a keyboard with the encryption capability set and no HID++
  report-types declared, matching LOGITacker's known-working profile.
- Device type matters beyond pairing: LOGITacker pairs as device type
  keyboard (0x01) because "for latest receiver firmwares character keys
  [a-zA-Z] are blacklisted for non-keyboard devices" (LT:
  logitacker/logitacker.c:225 comment) — see §5.

## 5. Generation / firmware differences

Each item with its evidence:

1. **Receiver silicon/WPID generations**: receiver WPID 0x8802 =
   Nordic-based (C-U0007 class, firmware series 012.xxx); WPID 0x8808 =
   TI-based (C-U0008 class, firmware series 024.xxx). The device learns
   the WPID in RSP1 (LT: logitacker_processor_pair_device.c success
   path classification; MJ: bastille-11 advisory lists C-U0007 fw
   012.005.00028 and C-U0008 fw 024.003.00027, both USB 046d:c52b).
   No device-side behavioural branch on WPID is implemented in
   LOGITacker — the difference matters to the *study* (which receiver
   to verify against), not to the frame formats.
2. **Pairing without lock (forced pairing)**: accepted by fw
   012.001.00019 / 012.003.00025 (MJ: bastille-1); addressed by later
   firmware. Device impact: none required — but a verification plan
   cannot assume the lock state from these sources.
3. **Plaintext acceptance after encrypted pairing**: the MouseJack-era
   firmwares accepted unencrypted keyboard frames even for devices
   paired with encryption (MJ: bastille-2), and the first fix
   firmwares (012.005.00028 / 024.003.00027) still failed to fully
   block plaintext injection (MJ: bastille-11). Later firmware is
   stricter. Device impact: a device that pairs **with** the
   encryption capability must actually encrypt — plaintext fallback
   cannot be relied on with current firmware.
4. **Device-type enforcement**: latest receiver firmwares blacklist
   character keystrokes from devices not paired as keyboards
   (LT: logitacker/logitacker.c:225). Device impact: pair with device
   type 0x01 (keyboard) — bastille-3's mouse-spoofing no longer works
   on such firmware.
5. **Bolt is a different generation**: newer Logitech receivers (Bolt)
   use a different pairing protocol (discovery + passkey, registers
   0xC0/0xC1 — SOL: notifications.py Bolt handlers). Nothing in the
   Unifying exchange above applies to Bolt, and a Unifying-only device
   will not pair with a Bolt-only receiver. (The target receiver model
   confirmation in the parent task decides whether this matters.)

## 6. Open items — not settled by the sources (need a capture vs a real receiver)

1. **Keep-alive semantics**: units and exact value of the REQ1 interval
   byte (0x08), the contents the receiver puts in set-keep-alive
   frames, and the silence timeout after which the receiver drops the
   device. Sources: only LOGITacker code comments ("likely").
2. **Counter acceptance window**: how far ahead/behind the last counter
   the receiver accepts, behaviour on counter reset (e.g. device
   battery swap restarting at 0), and whether the window differs for
   keyboard vs HID++ frames.
3. **Channel behaviour in normal operation**: receiver hop pattern and
   dwell, and how a device that has been asleep re-acquires the
   receiver (full table scan vs remembered channel) — LOGITacker hops
   as a *sniffer*; the paired-device discipline is not in these sources.
4. **Whether the C-U0008-class target firmware requires the pairing
   lock**, enforces encrypted-only traffic for encryption-paired
   devices, and enforces the keyboard-type blacklist — i.e. which
   §5 items apply to the actual target receiver/firmware.
5. **REQ1 bytes 12 and 15 semantics** (byte 12 is 0x00 for
   keyboard/mouse, 0x02 for some mice/presenters in captures LOGITacker
   saw; byte 15 unknown) — whether any receiver firmware validates them.
6. **Address-assignment policy**: whether RSP1's offered address is
   derived from the receiver's own address/serial or random per slot,
   and whether a re-pair with the same serial restores the same address
   and slot.
7. **LED frame (0x0E) exact payload** and whether the receiver expects
   any acknowledgement/behaviour from the keyboard on LED changes.
8. **HID++ expectations of current host stacks**: whether current
   Logitech software (Options+/Solaar) treats a device that never
   answers HID++ as fully functional for typing over days of use
   (power-management disconnects, "inactive" removal), beyond the
   ping/offline display behaviour visible in Solaar.
9. **Maximum devices / slot behaviour**: PairingError TOO_MANY_DEVICES
   exists host-side; the per-receiver slot count and slot reuse after
   unpair are not stated in the device-side sources.
10. **Retransmission discipline expected by the receiver** in normal
    operation (how many ESB retries real devices use; LOGITacker's
    values are an attacker's working choice, not a captured device
    trace).

---

### Method note
Read from the repositories' code, not summaries. One disagreement worth
recording: secondary write-ups often describe the Unifying link key as
"exchanged during pairing"; the code shows it is *derived* on both sides
from exchanged nonces/addresses/WPIDs and never transmitted (LT:
logitacker_pairing_parser.c). Similarly, some write-ups put the
encrypted-keyboard counter little-endian; the Unifying-mode code writes
it big-endian (little-endian is the Lightspeed branch of the same
function) (LT: logitacker_unifying_crypto.c
`logitacker_unifying_crypto_encrypt_keyboard_frame`).
