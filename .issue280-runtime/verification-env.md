# Issue #280 phase (d) — verification environment

What is needed to verify pairing/operation against a REAL Unifying
receiver and to resolve the spec's 10 open items
(`unifying-spec.md` §6). Prices are spot-check indications from web
search on **2026-11-18** (crawl dates noted); they are not live cart
quotes, per this project's rule that snippet stock/price figures are
not reservations.

## Shopping list

| Item | Role | Indicative price | Notes |
|---|---|---|---|
| **Nordic PCA10059** (nRF52840 USB dongle) | Runs **LOGITacker** — sniffer, pairing observer, and device-emulator in one. This is the single highest-value tool: most open items resolve with captures + emulated-device experiments *before any project hardware exists*. | **≈ $10** (DigiKey/Mouser, per 40percent.club, crawled 6 days before 2026-11-18; third-party listings $8–15) | LOGITacker's documented target hardware. Buy 1; a 2nd is convenient (one sniffing while one emulates) — optional +$10. |
| **Sacrificial Unifying receiver × 2** | The device under test's counterpart. Pairing/fuzzing experiments (lock-off pairing attempts, plaintext injection checks, slot exhaustion) can leave a receiver in odd states and consume slots; the reference receiver must stay pristine. | **≈ $9.77–14.35 each** (Amazon listings for C-U0007, prices as of Nov 2026 crawls) → **≈ $20–29 for two** | **A second receiver is advisable — recommended, not optional.** Buy one of the PO's target class once the model is confirmed (parallel task), plus one C-U0007-class (Nordic, 012.xxx fw) so both silicon generations in spec §5.1 are covered. Record each receiver's firmware version via Solaar before any test. |
| **Crazyradio 2.0** (Bitcraze, via Seeed) | Optional second sniffer platform (nRF52840). | **$40.00** (Seeed datasheet/listing updated 2026-11-11) | **The original Crazyradio PA is DISCONTINUED and Bitcraze's stock is exhausted** (Bitcraze blog, crawled 2026-11-17) — do not plan around it or pay scalper prices for the MouseJack-era dongle. Crazyradio 2.0 is *not* a LOGITacker target out of the box; treat as optional/skip unless a second capture radio is wanted. |
| Host tooling | **Solaar** (Linux, free): opens/closes the pairing lock, reads receiver firmware + slot registers, pings devices. Logitech Unifying Software (Windows/macOS, free) as the vendor-reference pairing path. Wireshark for LOGITacker capture files (free). | $0 | Solaar is also the *subject* of open item 8 (host-stack expectations) — test with both Solaar and Logitech's own software. |
| A real Logitech Unifying keyboard (any, borrowed or used) | Ground-truth traffic: what a genuine device's keep-alives, retries and LED handling look like. | $0 (borrow) – ~$15 used | Needed for items 1, 3, 7, 10 — captures of our own emulator alone cannot show genuine-device discipline. |

**Core total: ≈ $30–40** (1 dongle + 2 receivers). With the optional
second dongle and Crazyradio 2.0: ≈ $80–90. (≈ ¥4,800–6,400 /
¥12,700–14,300 at ¥159/$, the project's 2026-11-17 rate.)
No item needs JLCPCB, a board spin, or the project hardware.

## Open-item → capture/test mapping (spec §6 numbering)

| # | Open item | Resolving capture / test | Needs |
|---|---|---|---|
| 1 | Keep-alive semantics (interval units, 0x0F contents, silence timeout) | Sniff a **genuine keyboard** pairing + idling with LOGITacker; read the 0x0F frames verbatim. Then time a paired device's silence→"offline" transition in Solaar to get the enforced timeout. | dongle, genuine keyboard, sacrificial receiver, Solaar |
| 2 | AES counter acceptance window; counter-reset behaviour | LOGITacker in **device mode** against the sacrificial receiver: send encrypted frames at controlled counter offsets (ahead/behind/reset to 0) and record accept/reject. The reset case emulates a battery swap. | dongle (device mode), sacrificial receiver |
| 3 | Channel hop pattern/dwell; sleep re-acquisition | Long LOGITacker promiscuous captures of a genuine device in normal operation; then wake-timing measurement: genuine device sleeps → keypress → time-to-host-report, repeated. | dongle, genuine keyboard, receiver |
| 4 | Target-firmware enforcement set (lock required? encrypted-only? keyboard-type blacklist?) | Attempt matrix against the **sacrificial target-class receiver**, firmware version recorded first via Solaar: (a) pair with lock closed, (b) pair with encryption then send plaintext, (c) pair as non-keyboard type and send character keys. Each is pass/fail observable. This is why the sacrificial receiver must be the *target* class, not only C-U0007. | target-class sacrificial receiver, dongle |
| 5 | REQ1 bytes 12 / 15 semantics | Pairing fuzz: vary bytes 12/15 over plausible values in emulated REQ1 vs the sacrificial receiver; acceptance pattern is the answer. Cross-check against genuine-device pairing captures. | dongle (device mode), sacrificial receiver |
| 6 | Address-assignment policy; re-pair slot/address reuse | Pair → read receiver slot registers via Solaar (HID++ 1.0 info registers) → unpair → re-pair with the same serial, several cycles; diff assigned address/slot each time. | dongle or genuine device, receiver, Solaar |
| 7 | LED frame (0x0E) exact payload | Sniff while toggling Caps/Num/Scroll Lock on the host with a genuine keyboard paired; capture 0x0E payloads for each state combination. (Whether the *device* must react is settled by construction: our firmware just applies LED state — the capture defines the payload it will receive.) | dongle, genuine keyboard, receiver |
| 8 | Host-stack expectations for a HID++-silent device | Pair the LOGITacker keyboard profile (no HID++ declared, per spec §4) and use the machine normally for days under both Solaar and Logitech Options+/Unifying Software; log "inactive"/removal/power-management behaviour. Long-duration, zero extra hardware. | dongle (device mode), receiver, host software |
| 9 | Slot count / TOO_MANY_DEVICES / slot reuse | Fill all slots on the sacrificial receiver (emulated devices with distinct serials are enough), attempt one more pairing and capture the host-visible PairingError; unpair one and observe reuse. | dongle, sacrificial receiver, Solaar |
| 10 | Retransmission discipline of real devices | Capture a genuine keyboard under induced loss (distance + shielding), count ESB retries and inter-frame timing from the capture; compare with the values our implementation plans to use (spec §1 defaults). | dongle, genuine keyboard, receiver |

## Sequencing note

Items 1, 3, 7, 10 (genuine-device captures) and 4, 5, 6, 9
(sacrificial-receiver experiments) can all run **before** any radio
hardware is added to the keyboard — the dongle emulates the device
side. Item 2 and the end-to-end form of 8 are the only ones that
benefit from a second capture radio running simultaneously, which is
the sole reason a second PCA10059 appears above as a convenience.
