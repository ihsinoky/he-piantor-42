# Issue #280 phase (c) — hardware implications of Unifying support

Study only. Protocol basis: `.issue280-runtime/unifying-spec.md`.
Project numbers are from repo records (docs/decisions.md D-009/D-010/
D-024/D-026/D-027; case tree issue-263-lowdeck-production) — see
plan-cd.md for the verified extract. Prices are distributor/marketplace
spot-checks from web search on **2026-11-18**, labelled as such; search
snippets are price *indications*, not live cart quotes.

## 1. Radio options

### (i) nRF24L01+ added to the existing RP2040 Main (SPI peripheral)

- **How:** the nRF24L01+ implements ESB, auto-ACK and **ACK payloads in
  hardware** — exactly the link features the spec (§1) requires. The
  RP2040 runs the pairing state machine, the Logitech checksum and the
  AES-128 frame crypto in software (no AES accelerator on RP2040; at
  keyboard frame rates a software AES-ECB block per frame is trivial).
  This is the MouseJack-era architecture transplanted onto our MCU.
- **Parts / cost:** bare module with PCB antenna ≈ **$0.30–1.50**
  (commodity marketplace class, 2026-11-18 search); genuine-silicon
  modules (Ebyte E01 series) ≈ **$1–3.60**. Chip-only (QFN20) needs an
  RF layout + antenna design — module first.
  **Clone risk (the option's trap):** a large share of cheap modules use
  clone silicon (XN297-class) whose ACK-payload / dynamic-payload
  behaviour deviates from Nordic's; Unifying pairing *depends* on ACK
  payloads. Budget for genuine Nordic or Ebyte-genuine modules and a
  per-batch sanity check.
- **Area / placement:** module ≈ 15×29 mm (pin-header class) or
  ~13×18 mm SMD class. Main Rev.10's outline is frozen and fully routed;
  a module means a Main respin or a mezzanine over the bay — a layout
  task, not a drop-in. Placement constraint is the antenna (§1.4).
- **Firmware scope:** smallest of the "real" options: SPI driver +
  spec §2 state machine + §3 crypto + keep-alive discipline. No second
  firmware codebase, no IPC protocol.

### (ii-a) nRF52 SoC as co-processor beside the RP2040

- **How:** an nRF52832/840 module runs the radio stack (Nordic ESB
  library — LOGITacker's `nrf_esb_illegalmod` is literally a fork of it,
  so this silicon family is the *proven* Unifying-device platform),
  the pairing state machine and the crypto (nRF52 ECB peripheral does
  AES-128 in hardware). The RP2040 keeps sensing/USB and passes key
  events over UART or SPI.
- **Parts / cost:** module class RayTac MDBT50Q (nRF52840, certified)
  ≈ **$7.95–14.30**; nRF52832 modules (MDBT42Q / SKB369 class)
  ≈ **$4–8.50** (2026-11-18 search). Certification of the module
  carries over (JP Teijin/TELEC variants exist in these families) —
  relevant if the board ever leaves the bench.
- **Area / placement:** module ≈ 10×16 mm (MDBT50Q) — smaller than a
  header nRF24 module, still a Main respin. Same antenna rules (§1.4).
- **Firmware scope:** largest of the add-on options: a second firmware
  (nRF Connect SDK / nRF5 SDK), an RP2040↔nRF52 event protocol, and
  two-sided power/state management (who owns sleep, pairing persistence
  — spec §2 requires the *device* to persist address/serial/nonces).

### (ii-b) nRF52 SoC as RP2040 replacement (single-chip Main)

- **How:** nRF52840 has USB device, a 12-bit SAADC and enough GPIO for
  the mux topology (3 ADC + 3 address + 3 enable + radio internal), so
  a single-chip Main is electrically plausible.
- **Why it ranks last anyway:** it discards the qualified Main design
  wholesale — new board, full firmware port (TinyUSB-on-nRF52 for the
  wired mode), and re-qualification of the analog chain: the
  6.8 kΩ/10 kΩ dividers + 1 nF ADC-node capacitors were settled against
  the RP2040 ADC's input behaviour; the SAADC's input impedance and
  acquisition model differ, so the 14-slot scan timing and the
  farthest-point/analog margins must be re-derived, not assumed.
  Highest rework by a wide margin (PO priority 2).

### (iii) Other credible routes

- **Donor-device harvest:** buy a used Unifying keyboard (K270/K360
  class, ≈ $10–25 used, 2026-11-18 search class), extract its
  controller — a finished, pairing-proven Unifying device — and inject
  our key events into its switch matrix. Zero protocol work, but the
  injection needs one switching element per donor matrix node driven
  from our scan results (parts count and per-donor variance explode),
  and the donor's identity/name/serial comes with it. Credible as a
  one-off bench hack; not a product architecture.
- **nRF24LU1+** (MouseJack's own platform, also the discontinued
  Crazyradio PA's chip): integrated USB + nRF24 in one 8051 SoC.
  Dismissed: legacy toolchain, NRND-class availability, and it still
  replaces the Main MCU (same rework class as ii-b with worse tooling).

### 1.4 Antenna placement (all options)

The switch plate is **aluminium** (opaque at 2.4 GHz) and covers the
Wing areas; the case is printed PETG (near-transparent at 2.4 GHz at
these wall thicknesses). The Main board sits in the central bay, which
in the adopted low-deck case is **not** covered by the aluminium plate.
Consequences: the antenna must live in the bay / south zone, on the
Main board's south edge or a module antenna zone clear of the plate
edges, the FFC and the USB/Fly metalwork. A module with its PCB
antenna under either Wing plate, or a chip antenna without a proper
keep-out, will not link reliably. (If the Δ+6 fallback case with its
aluminium bay cover were ever revived, an internal antenna would be
shadowed — the bay cover and an internal radio are mutually exclusive.)

## 2. Power architecture — the crux

### 2(a) Wired budget as recorded

- Hall array: **127 mA/Wing × 2 = 254 mA at the 5.2 V rail, continuous**
  (design load, D-026/D-027) = **1.32 W** for sensing alone.
- Total must fit the **configured USB allowance of 500 mA** including
  converter input current and all other Main loads (D-027) — i.e. the
  wired design already runs at roughly half the USB budget on sensors.
- Cross-check (invariant: distrust the first number): the current
  DRV5055 datasheet (SBAS640 Rev. C, Dec 2023) gives ICC = 3 typ /
  5 max mA at 5 V, so 42 sensors draw 126–210 mA at the sensor pins.
  The recorded 254 mA design load is therefore conservative (it was
  set against the older datasheet revision and includes margin) —
  battery math below uses the **recorded** load as the pessimistic
  basis and the datasheet-typical (~170 mA total) as the optimistic
  sensitivity. The conclusion does not change between them.
- Radio energy is a rounding error next to this: nRF24 TX/RX peaks are
  11–14 mA for sub-ms frames; nRF52 is lower. **The radio choice does
  not decide battery feasibility. The Hall array does.**

### 2(b) What battery operation would require

Stated target: **8 h/day × 5 days = 40 h** between charges.

| Scenario | Avg. system draw | Energy for 40 h | ≈ 1S Li-ion capacity |
|---|---|---|---|
| Continuous scan (as designed) | ~1.6 W (Hall 1.32 W + converter loss + RP2040/logic + radio) | ~64 Wh | **~17,000 mAh** |
| Duty-cycled sensing (§2c, mixed typing/idle) | ~0.5–0.7 W | ~20–28 Wh | **~5,500–7,500 mAh** |
| One 8 h day only, continuous | ~1.6 W | ~13 Wh | **~3,500 mAh** |

Physical fit: **no battery cavity exists in the case.** The low-deck
stack leaves ≈ 3.10 mm under the boards, and that space is already
spent (FPC channels, component hang-down to 0.60 mm above the tray
floor, the D-046 pocket). Even the smallest scenario above is a
phone-class pouch cell (a 3,500 mAh cell is ~5–10 mm thick before its
protection board and wiring). **Battery operation therefore requires
a case redesign (thicker deck or an external/under-desk pack) in
every scenario** — it is not a board-only change.

What *does* survive: the electrical architecture. The TPS63070-class
buck-boost's input range (2–16 V class, datasheet) covers a 1S Li-ion
cell (3.0–4.2 V) directly, so the 5.2 V rail and the 4.60 V
farthest-point guarantee logic carry over. The additions are a charge
path on the USB input (charger IC of the BQ24074 / MCP73831 class,
≈ $0.50–1.50), cell protection, and charge-vs-operate management —
board work, but incremental. The blocker is mechanical volume and
the sensing load, not the power tree.

### 2(c) The sensing problem — what "sleep" can even mean

- The DRV5055 sensors **are** the key switches. There is no separate
  wake switch, and the part has **no enable/sleep pin** (datasheet):
  the only power gate is the HALL_5V rail switch (TPS22919, GPIO7) —
  which already exists and is default-off (D-009). MUX bank enables do
  not reduce sensor current (D-026, explicit).
- LOGITacker-class devices never face this: they *emulate* a keyboard
  from a dongle that is awake anyway; nothing in the Unifying spec
  forces a sensing strategy. Sleep is entirely our problem.
- **Wake-on-keypress in the usual sense is impossible**: with the rail
  off, nothing observes the keys. The workable substitute is **burst
  scanning**: power the rail, wait for sensor power-on (DRV5055 tON =
  40 typ / 100 max µs at 5 V, Rev. C), run one full 14-slot scan
  (≈ 0.1–0.5 ms of ADC + mux settling; 1 ms burst window is a
  conservative planning figure), power down, repeat on an interval T.
  - Idle at T = 10 ms (100 Hz bursts, 1 ms window → 10% Hall duty):
    Hall average ≈ 25 mA → sensing ≈ 0.13 W. Worst-case added latency
    = T = 10 ms; a real keypress (≥ 30 ms) cannot be missed.
  - Deep idle at T = 50–100 ms saves little more (the burst window,
    not the interval, dominates below ~10% duty) and *can* miss or
    swallow a short first tap — the standard "first keypress wakes,
    doesn't type" behaviour of commercial wireless keyboards. Accept
    only after minutes of inactivity.
  - **Analog fidelity cost:** between bursts there is no travel data.
    Burst mode is an idle-detection mode only; any detected press
    must promote the scanner to continuous full-rate scanning, or
    rapid-trigger / analog behaviour silently degrades. Release
    detection has the same constraint in reverse (a release between
    bursts is seen late by ≤ T).
  - Keep-alive interplay (spec §4, Open Item 1): the receiver drops a
    silent device after its keep-alive window. Radio keep-alives are
    cheap and must continue on schedule while the Hall rail sleeps —
    the radio/MCU sleep state and the sensor sleep state are
    independent, and conflating them is the classic way to build a
    keyboard that disconnects when idle.

### 2(d) Hybrid: wireless link, still USB-powered

Coherent, and arguably the only near-term shape that is:

- **What it is:** option (i) or (ii-a) radio added; the keyboard still
  draws power over USB (cable or a USB power source); the Unifying
  link replaces the USB *data* path. Dual-mode by construction: USB
  data when enumerated, RF when not (mode story in §3).
- **What it proves:** the entire protocol risk — pairing against the
  real target receiver, encrypted operation, keep-alive discipline,
  host-software behaviour (spec §5/§6 items) — with zero battery/case
  work. This is where almost all of the unknown lives.
- **What it does not prove:** anything about battery life, sleep
  behaviour, or untethered ergonomics; and it must not be *sold*
  (even to ourselves) as "wireless keyboard, phase 1" — the battery
  step remains a case redesign (§2b), not a follow-on board spin.
- A dongle-side-only variant (LOGITacker-style: our firmware on a
  bench dongle pretending to be the keyboard) proves even less about
  the product but is the right *verification* vehicle — see part (d).

## 3. Interface to the existing design

- **Pin budget (Rev.10 schematic census):** functional nets account
  for 9 RP2040 GPIO (MUX_A0–A2, WING_EN/MUX_EN0, MUX_EN1,
  HALL_PWR_EN, ADC0–2 inputs) plus dedicated USB/QSPI/SWD. The RP2040
  offers 30 GPIO; an SPI bus + CE + IRQ for option (i) needs 6. **Pin
  budget is not a constraint** for (i) or for a UART/SPI link to
  (ii-a). The exact free-pin list is a layout-stage task on a respin.
- **EN / addressing interplay:** none at the protocol level. The Wing
  enables (GPIO5/6) and HALL_PWR_EN (GPIO7) are Main-internal; the
  radio never touches the Wing link, which stays FFC/ZIF in all
  options. One *system* interplay: HALL_PWR_EN becomes the burst-scan
  actuator in any future battery firmware (§2c) — its default-off,
  configured-permission behaviour (D-027) must be preserved.
- **Mode story per option:**
  - (i) and (ii-a): dual-mode is natural — RP2040 owns USB; RF is a
    second output path for the same key events. Sensible default:
    USB data when a host enumerates, RF otherwise; pairing state
    persists in flash (RP2040 side for (i), radio side for (ii-a) —
    decide once, spec §2 lists what must persist).
  - (ii-b): dual-mode also possible (nRF52 USB) but is a by-product of
    a full platform port, not a feature of the option.
  - Donor (iii): RF-only; the wired USB path would bypass the donor
    entirely (two independent output paths, no shared state).

## Feasibility shape (input to the PO report — not a recommendation)

Ranked by PO priorities (cost > low rework > freedom > speed):

1. **USB-powered dual-mode, nRF24L01+ on the RP2040 (option i).**
   Cheapest parts (~$1–4/keyboard), one firmware, proves the whole
   protocol against the real receiver, keeps every qualified board
   decision except a Main respin for the module.
   *Biggest risk:* clone-silicon ESB behaviour — mitigated by genuine
   modules, but it is a supply-chain discipline forever, and the
   nRF24 is a legacy part family.
2. **USB-powered dual-mode, nRF52 co-processor (option ii-a).**
   ~$4–14/keyboard more, a second firmware to own, but the radio
   platform is the one LOGITacker itself proves, modules carry radio
   certification, and the same module is the natural battery-era
   radio if a case redesign ever happens.
   *Biggest risk:* two-firmware system complexity (IPC, sleep/pairing
   state ownership) — the failure modes move from RF to integration.
3. **True battery wireless (any radio).** Not an end-state reachable
   from the current case: 40 h at the recorded sensing load needs
   ~17,000 mAh continuous / ~5,500+ mAh duty-cycled, and no cell of
   either class fits a 3.10 mm internal void. Requires a case
   redesign decision *before* any radio decision matters.
   *Biggest risk:* the sensing load, not the radio — a battery
   version is a different product (case + power + scan strategy),
   and under-scoping it is the easiest way to burn the budget.

Options (ii-b) and (iii) are excluded from the ranking: (ii-b) is
dominated on rework by (ii-a) with no compensating gain; (iii) is a
bench hack, not an architecture.
