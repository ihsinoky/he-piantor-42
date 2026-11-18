# Issue #287 — bench proof procedure (Unifying device emulation)

**Goal.** Prove, on the bench and before any project board exists,
that a device built on **the same silicon family as the product MCU
(nRF52840 module class — product chip decided as nRF52840, D-052)**
can pair with a real Logitech Unifying receiver as a keyboard and
deliver keystrokes, and resolve the 10 open items of
`.issue280-runtime/unifying-spec.md` §6 by capture and experiment.
The PCA10059 dongle running LOGITacker is the device emulator: it is
an nRF52840, i.e. the product MCU's own silicon, so pairing/crypto/RF
behaviour measured here carries over to the product design.

Steps that cannot be confirmed without the hardware in hand are
marked **TO VERIFY ON ARRIVAL** — do not treat them as facts; check
them in order and amend this file.

## 0. Prerequisites

- Hardware from `purchase-list.md`: 1× PCA10059, 2× sacrificial
  Unifying receivers (one per class where possible), 1× genuine
  Unifying keyboard (borrowed is fine), 1× receiver kept as the
  **pristine reference** (one of the two sacrificial units starts
  pristine; never run experiments against the reference role — if
  only two receivers exist, the C-U0007-class unit is the reference
  first, the target-class unit is the experiment unit; swap roles
  only by re-baselining per §2).
- Host: a Linux PC (Solaar is Linux-native). A Windows/macOS machine
  with Logitech Unifying Software / Options+ is the vendor-reference
  path for item 8; optional but planned.
- Labels + a notebook file per receiver (firmware, class, slot state
  before/after every session).

## 1. LOGITacker on the PCA10059

Upstream repo: **https://github.com/RoganDawes/LOGITacker**

### 1.1 Get the firmware (two routes)

Route A — prebuilt image shipped in the repo (fastest):

```
git clone https://github.com/RoganDawes/LOGITacker
# repo file: build/logitacker_pca10059.hex
```

Route B — build from source (the repo's own Dockerfile documents the
exact toolchain; reproduce it natively or in Docker):

- Toolchain: `gcc-arm-none-eabi`, `make`, git, wget, unzip.
- SDK: **nRF5 SDK 15.3.0** (`nRF5SDK153059ac345.zip` from Nordic).
- Patch the SDK makefile to the local toolchain
  (`components/toolchain/gcc/Makefile.posix`: `GNU_INSTALL_ROOT`),
  set `SDK_ROOT` in `LOGITacker/pca10059/blank/armgcc/Makefile` to
  the SDK path, then `make` in that directory.
- Output: `pca10059/blank/armgcc/_build/logitacker_pca10059.hex`.

Record which route and which commit produced the flashed image.

### 1.2 Flash via the dongle's USB bootloader

(Per the LOGITacker README, §2.1.)

1. Install **nRF Connect for Desktop** and its **Programmer** app.
2. Insert the PCA10059; press the button labelled **RESET** — the
   red LED starts "soft-blinking": the dongle is in its bootloader.
3. In Programmer: select the dongle, add `logitacker_pca10059.hex`,
   **Write**.
4. Re-insert the dongle. It now enumerates **four** USB interfaces:
   CDC ACM serial (the CLI), USB mouse, USB keyboard, USB HID raw
   (pass-through interfaces).

### 1.3 CLI smoke test

```
screen /dev/ttyACM0 115200
```

(README's own example; the exact tty name is **TO VERIFY ON
ARRIVAL** — the dongle may not land on ttyACM0. With `screen`, use
Ctrl+H for backspace.) Pass observation: a `LOGITacker (discover) $`
prompt answers, and `help` lists the mode commands (`discover`,
`passive-enum`, `active-enum`, `inject`, `pair`, `devices`,
`options`, `script`). Set the CLI log to a file from here on — every
session below is evidence.

## 2. Host setup and receiver baselining

1. **Solaar**: install from the distro package or the project's
   documented route; apply Solaar's udev rules so the receiver is
   accessible without root (**TO VERIFY ON ARRIVAL**: exact package
   and rule file on the bench host's distro).
2. For **each** receiver, before any test:
   - Plug it in alone. `solaar show` — record: model/firmware
     (**RQR12 ⇒ C-U0007 class, RQR24 ⇒ C-U0008 class**), receiver
     WPID, serial, current pairings/slots.
   - Stick a physical label on it: class + role
     (`REF` / `SACRIFICIAL`) + firmware version.
   - This readout is also how open item 4's "target firmware" becomes
     a named version instead of a class guess.
3. **Logitech Unifying Software / Options+** (Windows/macOS):
   install only; used as the vendor-reference pairing path and for
   item 8 comparison. No steps here depend on it.
4. **Wireshark**: install Wireshark on the host. LOGITacker's raw
   pass-through (USB HID raw interface) plus the repo's companion
   tooling (`companion2.py` in the repo root) is the capture path
   into host-side analysis; LOGITacker also logs frames on the CLI.
   **TO VERIFY ON ARRIVAL**: the exact companion invocation and
   whether captures are saved as pcap for Wireshark dissectors, or
   analysed from CLI logs — settle this in the first session and
   amend this section. Save every capture with the naming
   `YYYYMMDD_item<N>_<receiver-class>_<short-desc>`.

## 3. Baseline: genuine-device captures (do first)

1. Pair the genuine keyboard to the **reference** receiver using
   Solaar (`solaar pair`, power-cycle the keyboard when prompted).
2. LOGITacker in `discover`, then `passive-enum` on the keyboard's
   address: record idle traffic (keep-alives), typing traffic, and a
   sleep→keypress wake.
3. These captures are the ground truth items 1, 3, 7, 10 compare
   against. Nothing in this section writes to any receiver except
   the one genuine pairing (which stays in place as the reference
   configuration).

## 4. Pairing run — emulated device (the core proof)

Target profile (spec §4, LOGITacker's known-working profile): device
type **keyboard (0x01)**, encryption capability **set**, **no HID++
report types declared**.

1. Insert the **sacrificial** receiver. In Solaar, open its pairing
   lock (start a pairing window).
2. On LOGITacker, enter pairing: mode `pair`, submode `pair device`
   (README §3.1). Exact option spellings for device type / name /
   serial are **TO VERIFY ON ARRIVAL** via the CLI's inline help —
   set type keyboard, a bench-only name and serial, and persist the
   resulting device with `devices storage save <address>` (LOGITacker
   stores serial, key, RF address, WPIDs persistently).
3. Pass observations, in order:
   - The receiver completes pairing; Solaar lists the emulated
     device in a slot.
   - LOGITacker's stored record contains the derived AES key and the
     receiver-assigned RF address (key is *derived*, never
     transmitted — spec method note).
   - The full pairing exchange is in the session log for comparison
     with spec §2's 8 steps.
4. If pairing fails: capture the failure verbatim, note the receiver
   firmware, and retry once with the lock freshly opened. Do **not**
   escalate to `pair sniff`/forced-pairing variants in this run —
   those belong to item 4's matrix, against the sacrificial unit
   only.

## 5. Key-send test

1. With the §4 pairing in place, focus a text field on the host (the
   sacrificial receiver is the input path — use a scratch document).
2. In LOGITacker `inject` mode for the paired device, send a known
   string (e.g. via a one-line `script`: `script string "unifying
   poc 123"` then execute in inject mode; exact execution command
   **TO VERIFY ON ARRIVAL** from CLI help). Keys go out encrypted
   with the §4 key — plaintext fallback is not acceptable evidence
   (spec §5.3).
3. Pass observation: the exact string appears in the host document,
   including shifted characters; repeat after a dongle power-cycle
   (stored device reloads from flash) and after a receiver
   re-insertion. All three runs logged.

## 6. Test matrix — the 10 open items (spec §6)

Run after §§3–5 pass. "Pass observation" = the evidence that closes
the item; record negative results with the same care.

| # | Item | Concrete step | Pass observation |
|---|---|---|---|
| 1 | Keep-alive semantics | From §3 captures: read the genuine keyboard's REQ1 interval byte and every receiver→device 0x0F frame verbatim. Then, with the emulated device paired, stop its keep-alives and time how long until Solaar shows it offline. | Interval byte value + units consistent across captures; 0x0F contents transcribed; measured silence→offline timeout recorded per receiver class. |
| 2 | Counter acceptance window | LOGITacker device mode vs sacrificial receiver: send encrypted keyboard frames at counter offsets (last+1, +10, +1000, last−1, and reset to 0 — the battery-swap case). One variable at a time; log accept/reject per offset. (Simultaneous sniffing is easier with the optional 2nd dongle; without it, the host document + receiver behaviour is the oracle.) | Accept/reject table per offset, per frame class (keyboard vs HID++ long if exercised). |
| 3 | Channel behaviour / re-acquisition | Long `passive-enum` captures of the genuine keyboard (§3): extract hop sequence and dwell. Then measure wake latency: keyboard asleep → keypress → character on host, 10 trials. | Hop pattern/dwell stated from capture; wake-latency distribution recorded. |
| 4 | Target-firmware enforcement set | Against the **sacrificial target-class** receiver (firmware recorded in §2): (a) attempt `pair device` with the Solaar lock *closed*; (b) pair with encryption, then send a plaintext keyboard frame; (c) pair as a non-keyboard device type and send character keys. Repeat the matrix on the other class. | Pass/fail per cell, per class+firmware — this decides which spec §5 items the product firmware must honour. |
| 5 | REQ1 bytes 12 / 15 | In `pair device` runs vs the sacrificial receiver, vary byte 12 over {0x00, 0x02} and byte 15 over plausible values (one at a time); compare acceptance against the genuine pairing capture from §3. Exact byte-editing mechanism in the CLI is **TO VERIFY ON ARRIVAL**; if the CLI cannot vary them, record that and fall back to comparing genuine captures across device kinds. | Acceptance pattern per value; "not validated by this firmware" is a valid closing result if shown. |
| 6 | Address-assignment policy | Cycle on the sacrificial receiver: pair (emulated, serial S) → read slot registers via Solaar → unpair → re-pair same serial S. 3 cycles; also pair a second serial and diff. | Assigned address + slot per cycle; stated policy (derived vs random; same-serial restore or not) with the register readouts as evidence. |
| 7 | LED frame (0x0E) payload | Genuine keyboard paired (§3); toggle Caps/Num/Scroll Lock on the host through all 8 combinations while capturing. | 0x0E payload transcribed per combination; whether any device→receiver response follows is visible in the same capture. |
| 8 | Host-stack expectations (HID++-silent device) | Leave the §4 emulated device (no HID++ declared) paired and in normal use for several days, under Solaar *and* under Logitech Options+/Unifying Software on the second host. Log "inactive"/offline displays, any removal or power-management surprises; typing must keep working throughout. | Behaviour log per host stack; "typing unaffected for N days, displayed offline only" closes the item. |
| 9 | Slot count / TOO_MANY_DEVICES | On the sacrificial receiver, pair emulated devices with distinct serials until full; attempt one more pairing and capture the host-visible PairingError; unpair one and re-attempt. | Slot count for this receiver class; the exact error surfaced; whether the freed slot is reused. |
| 10 | Retransmission discipline | §3 genuine keyboard, induced loss (distance + shielding — e.g. keyboard in a metal box with a small opening, or maximum range): count ESB retries and inter-frame gaps in the capture; compare with LOGITacker's defaults (250 µs delay, count 3 — spec §1 / source notes). | Retry count + timing distribution of a real device, stated next to the values our firmware will use. |

## 7. Safety, scope, and end state

- **Own hardware only.** Every experiment runs against receivers and
  devices bought/borrowed for this bench (purchase-list.md). Never
  pair with, inject into, or fuzz a receiver that is in daily use or
  belongs to someone else; the item-4/5 attempts (lock-closed
  pairing, plaintext-after-encryption, type spoofing) run **only**
  against the unit labelled SACRIFICIAL.
- RF work happens in our own space at normal bench ranges; the
  induced-loss setup in item 10 is shielding/distance, not jamming
  or amplification.
- **No receiver firmware is modified** by this procedure (no fwupd
  flashing); firmware versions are read, never written.
- **End state of sacrificial receivers:** they may hold pairings of
  emulated bench devices in their slots and will have had their
  pairing lock opened/closed repeatedly. That is expected and is why
  they are sacrificial. On bench teardown (or before a unit changes
  role), restore a clean state: unpair every emulated device in
  Solaar, confirm `solaar show` lists no bench devices, and log the
  final slot state in the receiver's notebook file. The reference
  receiver keeps only its genuine-device pairing throughout.
- LOGITacker's flash will hold bench device records (serials, derived
  keys) for our own emulated devices — that is the tool's normal
  operation; `erase_flash` (README §3.2) clears it if the dongle is
  ever repurposed.
