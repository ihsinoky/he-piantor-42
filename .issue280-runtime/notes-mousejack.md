# Source notes: Bastille MouseJack (BastilleResearch/mousejack,
# BastilleResearch/nrf-research-firmware)

## Role in this study
MouseJack is an attack/discovery toolset, not a device implementation.
Its firmware is a host-configured generic nRF24 ESB radio; the
Unifying-specific protocol facts come from LOGITacker and Solaar.
What MouseJack independently confirms (nrf-research-firmware/src/radio.c):
- Device->dongle traffic uses ESB with auto-ACK on pipe 0 and the FEATURE
  bits EN_DPL | EN_ACK_PAY enabled for transmit (radio.c:420-421):
  dynamic payload lengths and ACK payloads are part of the link - the
  same mechanism LOGITacker's pairing relies on (responses ride ACKs).
- Address width is host-set via SETUP_AW = length-2 (radio.c:97),
  RX_ADDR_P0 written with the full address (radio.c:99) - consistent
  with the 5-byte addressing LOGITacker uses.
- The research firmware's promiscuous reception works because ESB
  frames on air are standard nRF24 ESB; nothing proprietary at the
  framing layer below the Logitech payload/checksum.

## Advisories (mousejack/doc/advisories/*.logitech.public.txt) - Q5 evidence
- bastille-1: forced pairing with a dongle NOT in pairing mode, no user
  interaction; tested on Unifying dongle USB 046d:c52b, fw 012.001.00019
  and 012.003.00025. (Behaviour is firmware-dependent; later firmware
  addressed pairing acceptance - a device must not rely on it, but a
  real receiver of unknown firmware may accept pairing frames outside
  the pairing window. Capture needed per receiver.)
- bastille-2: keystroke injection bypassing encryption on fw
  012.001.00019 / 012.003.00025 - receivers accepted unencrypted keyboard
  frames from addresses paired with encryption.
- bastille-3: device-type spoofing at pairing (presents as mouse,
  acts as keyboard) on the same firmwares.
- bastille-11: Logitech's fix firmwares - C-U0007 fw 012.005.00028 and
  C-U0008 fw 024.003.00027 (both USB 046d:c52b) - still failed to fully
  block plaintext keystroke injection. => Whether a receiver enforces
  "paired-with-encryption => encrypted frames only" is a per-generation,
  per-firmware property, NOT a constant of the protocol.
- bastille-12/-16 concern Lightspeed G900, out of Unifying scope.

## Dongle hardware generations (cross-ref LOGITacker pair_device.c)
- Dongle WPID 0x8802 => Nordic-based (C-U0007 class, fw 012.xxx);
  WPID 0x8808 => TI-based (C-U0008 class, fw 024.xxx). The device learns
  the dongle WPID in pairing RSP1, so an implementation can observe -
  but per sources need not act on - the generation at pairing time.
