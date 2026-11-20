# Issue #290 — Trackpad addition study (Piantor-style), wireless variant first

Study only. No board/case changes, no orders. Adoption is a PO gate.

## Inputs and method

- Case geometry measured from the audited body set of the low-deck
  production case: `fitlibF.bodies_at(17, -2.65)` (the #248 frontier set
  shifted to the D-042 deck, as used by the Issue #261 audit), plus the
  `hardware/case/issue-261-lowdeck-full/preview.step` solids (FPC sheets,
  ZIF envelopes, Wing/Main PCBs). Datum: tray floor 1.60 ribbed, Wing PCB
  underside B=4.70, Wing/Main PCB 4.70–5.90, plate top 10.90, keytop
  22.00 provisional (gate 6 open). Disc-fit tests use the project's own
  repaired volume audit (`repair18_lib.vol_pair`), with the two
  `Main-GH-*-DRAWING-BOUND` bodies excluded per the #261 convention.
  Scripts: `.issue290-runtime/measure1.py` … `measure4.py`.
- Carried design inputs: antenna must live in the un-plated central bay /
  south PETG zone (aluminium plate is opaque at 2.4 GHz); battery =
  NiMH AA ×4 under-case pod, 8.65 Wh delivered (D-048); runtime baseline
  0.533 Wh/day = 16.2 days (Issue #284, architecture B1); MCU nRF52840
  (D-052); Unifying mouse-report frames exist and a device pairs under
  one device type (Issue #280).
- Frame note: in the audit frame, +Y is the user side (thumb clusters at
  Y ≈ 33…71, Fly/USB at Y ≈ −46…−54, case south rim at Y ≈ 70.4 at the
  centre). "South-centre" below means the user-side centre rim.

## 1. Parts — Cirque GlidePoint circle pads

Two silicon generations are on the market. They are not interchangeable
in firmware or power.

### 1.1 Pinnacle generation (the keyboard-community standard)

Controller: Cirque Pinnacle 1CA027 (Gen2 SoC). One module design in
three diameters; I2C and SPI factory configurations of the same board
(-2023-xxx = I2C, -2024-xxx = SPI; the interface is selected by resistor
R1 — populated = SPI, unpopulated = I2C — so an SPI unit converts to
I2C by depopulating R1). 12-pin 0.5 mm FFC connector (module-side
connector class Molex 78127-1128); the pinout carries DR (data-ready
interrupt), BTN1/2/3 button inputs, SCL/SDA, VDD, GND.

| Figure | TM040040 | TM035035 | TM023023 |
|---|---|---|---|
| Module diameter | 40.0 mm | 35.0 mm | 23.20 ±0.25 mm |
| Sensing diameter | 38.00 mm | 31.00 mm | 21.60 mm |
| PCB thickness | 0.74 mm | 1.00 mm | 0.74 ±0.070 mm |
| PCB + overlay | 0.99 mm | 1.25 mm | — |
| PCB + overlay + components | **5.15 ±0.20 mm** | **5.40 ±0.20 mm** | not extracted (UNVERIFIED; same construction class) |
| Adhesive | 0.25 ±0.025 mm | (in the 5.40 figure class) | — |
| Supply | 2.5–3.6 V | 2.5–3.6 V | 2.5–3.6 V |
| Active (finger moving) | 2.9 mA | 2.9 mA | 2.9 mA |
| Idle (no finger) | 1.7 mA | 1.7 mA | 1.7 mA |
| Sleep (config-enabled) | 40 µA | 40 µA | 40 µA |
| Shutdown | 0.23 µA | 0.23 µA | 0.23 µA |

Sources: Cirque *TM040040 Trackpad Specification* v1.2 (Nov 2017),
General Specifications p.5 and Physical Specifications p.6;
*TM035035 Trackpad Specification* v1.2, same pages; *TM023023 Trackpad
Specification* v1.1 (Nov 2017), General/Physical Specifications.
Electricals measured by Cirque at 3.3 V. Sleep figure is for a 3 s
touch-sensing interval and sleep mode is **not active by default** — it
is enabled in the configuration register (spec p.5, notes). Overlay:
stock flat laminate Ø39.80 mm (p/n 50-000069-20); a concave curved ABS
overlay (p/n 50-000090-00) is the -303 variant. Conductive overlay
materials are forbidden and the overlay must be adhered with no air
gaps (spec p.13). Mounting is a clamshell/bezel clamp (spec p.12).
Mouser's catalogue "Height 4.1 mm" for these SKUs contradicts the
datasheet stack (5.15 ±0.20 + 0.25 adhesive) and is not used.

### 1.2 Gen6s generation (Cirque's current line) — rejected for this project

Cirque's current GlidePoint page lists only Gen6s "Timp" (6G06A3)
modules: TM040040-1-306I, TM035035-1-306I, TM023023-1-306I,
TM016016-1-306I — I2C only, 6-pin FFC, 1.8–3.3 V. The only published
electricals are for the 23 mm size: **active 11.6 mA, idle 1.9 mA,
sleep 870 µA**, thickness 5.05 mm incl. mylar overlay (cirque.com
GlidePoint Circle Trackpads page, observed 2026-11-19; 40/35 mm
electricals not published — UNVERIFIED for those sizes). The 870 µA
sleep alone would cost ≈2.4 runtime days (§3) and there is no QMK/ZMK
driver for Gen6s (§4) — Cirque's page says further documentation is
"coming soon". Rejected on power + firmware prior art; revisit only if
Cirque publishes larger-size electricals and an open driver lands.

### 1.3 Availability scan (observed 2026-11-19 unless dated otherwise)

| SKU / channel | Stock | Price (1 pc) | Note |
|---|---|---|---|
| TM040040-2024-300 (no overlay), Mouser 355-TM0400402024-300 | InStock (JSON-LD, mouser.cn crawl 2026-11-12); X-On aggregator: 203 | $9.63 | SPI config |
| TM040040-2024-301 (adhesive overlay), Mouser | InStock (ar.mouser.com crawl 2026-10-24); X-On: 32 | $11.56 (X-On) | SPI config |
| TM040040-2024-302 (flat overlay), Mouser 355-TM0400402024-302 | **InStock** (uy.mouser.com page read 2026-11-19) | ≈$11 class (445.5 UYU localised) | SPI config; the flat-overlay unit this study assumes |
| TM040040-2024-303 (curved overlay), Mouser | InStock (crawls 2026-11-14…18) | $13.95 AUD class | SPI config; curved overlay is the sloped-surface option |
| keycapsss kit KC10079_40-A (module + 50 mm FFC + I2C adapter PCB + header), EU | **0 — out of stock** (read 2026-11-19) | €21.90 | 40 mm flat |
| keycapsss KC10079_35-C (35 mm curved kit) | 3 (crawl 2026-11-17) | €21.90 | thin |
| holykeebs "Touchpad Module" (40 mm on adapter), IL | InStock per aggregator crawl 2026-11-17; shop page crawl is 258 days old | $30.00 | treat stock as UNVERIFIED |
| beekeeb | sells the Toucan keyboard (Cantor layout + this 40 mm pad + XIAO nRF52840); a bare-module listing was not found | — | kit channel only (UNVERIFIED as a parts channel) |
| DigiKey | **no Cirque GlidePoint listing found** (search 2026-11-19) | — | one community guide claims DigiKey availability; no product page surfaced |
| Cirque direct | Gen6s line + dev kit only | — | Pinnacle generation is a legacy/OEM line; Mouser is the authorised distributor |

Lifecycle: the Pinnacle modules are a 2017 design that Cirque has
superseded in its own catalogue by Gen6s, but they remain in authorised
distribution (Mouser, factory pack 75) and are the only generation
with keyboard-firmware support. Cost-priority consequence: the part is
≈$10 — buy the prototype unit plus spares in one order; do not design
around the assumption of a deep future channel. JPY indications at
≈¥155/$: module ≈¥1,500–1,800; keycapsss kit ≈¥3,700 at ≈¥170/€.

**Part verdict: TM040040, flat overlay (-302), Pinnacle generation.**
TM035035 is the drop-in fallback if the Ø40 bezel crowds the bay panel
(§2); its stack is 0.25 mm thicker. TM023023 (Pinnacle) is a
Ø21.6 mm sensing area — too small as the primary pointer.

## 2. Placement — fitted checks against the low-deck case

Module model for all tests: right cylinder of the module diameter,
height = datasheet stack (TM040040: 5.15 + 0.25 adhesive = 5.40 mm).

### 2.1 Candidate (a) — central bay, over Main

The bay is covered by the printed central shell (`shell-central`,
X −41.01…41.01, Y −53.66…69.70). Measured shell sections over the bay:
top 12.6 / bottom 10.6 at (0,48); top ≈13 at Y 32–60 for |X| ≤ 24.
The shell is **not flat** across a Ø40 disc at (0,48): top Z = 12.6
(centre), 12.55 at (±14,34), 12.6 at (−14,62), 10.9 at (14,62) and at
the north rim (0,68), 14.27 at the south rim (0,28) — a 3.4 mm spread.
A flat module therefore needs a locally flattened island (Ø44 class)
in the shell's bay panel — a bounded change to a printed part — or
the curved-overlay variant on a tilted mount.

Disc audit, Ø40 at (0,48), Z 7.30…12.70 (underside set 0.30 above the
tallest *low* Main component under the disc, U1 top 7.00; surface
0.1 below shell top at centre):

- `shell-central` 3,058 mm³ — the pocket itself (expected; it is the
  material the bezel pocket removes).
- **Main-study-C26/C27/C28: 30.9 mm³ each** — the three tall ceramics
  are modelled to Z 8.90 under the disc and pierce its underside.
  L1: 22.4 mm³. Rim grazes ≤2.3 mm³: U4, C14, C23, C24. Tray joint
  graze 1.39 mm³ per half.
- `Fly-170mm` 255 mm³ — the stored EZmate cable's service loop rises
  to Z 10.30 under the bay. **Wired configuration only**: the loop
  would need re-dressing. The wireless variant has no Fly and no loop.
- FPC sheets (preview.step solids, Z ≤ 7.15) clear the module
  underside (7.30) by ≥0.15 mm at bbox level; the ZIF service sweep in
  the bay stays below the module.

Disposition: with the **wireless Main (a new layout, D-050/D-052) the
Ø40 keep-out under the bay costs nothing** — no tall part is placed
there. Against the inherited wired Main study set, the same pad would
either move C26/C27/C28/L1 (a Main respin item) or sit with its
surface at 14.60, i.e. +2.0 mm proud of the shell — not accepted.
Centre choice matters: at (0,32) the disc additionally sits over J4
(top 8.00, the USB EZmate header) and its plug — (0,48) avoids J4
entirely.

Conflicts carried by (a):
- **Antenna**: the bay is the antenna's first home. The module (a
  ground-poured PCB + FFC tail) takes the bay centre, so the antenna
  design must move to the south PETG zone (under the south shell
  slope, X ±41 / Y −53…0 — empty in the wireless configuration, where
  the Fly is deleted). One antenna home is consumed; the other
  remains. Co-location of the 2.4 GHz radio with the capacitive
  sensor is not created — it is removed — but the pad's FFC tail
  crosses the bay edge; RF/sensor coexistence at the new antenna site
  is a bench item, not a blocker (datasheet rates the module's EMI
  susceptibility low).
- **Service**: the pad rides in the removable shell; lifting the
  shell for FPC service gains one FFC disconnect (ZIF class, ~20-cycle
  rating — the same class already accepted for the Wing link).
- Height: **no height raise**. Surface 12.70 = plate +1.80, keytop
  −9.30 — a recessed pad between the key fields, reachable by either
  thumb without leaving the home position area.

### 2.2 Candidate (b) — thumb cluster of one Wing (left, Ø40 at (−55,52))

Disc audit, Z 5.50…10.90 (surface flush with the plate):

- `switch-envelope-L_T1` 1,165.7 mm³ and `switch-envelope-L_T2`
  1,166.8 mm³ — two of the three thumb keys are displaced outright.
- `switch-envelope-L_R2_C5` 175.1 mm³ — the disc also clips the
  innermost bottom-row key's envelope: a third key is encroached.
- `plate-left` 1,233.2 mm³ — a Ø40 hole through the 1.5 mm aluminium
  plate, and the plate's H3 fixing sits inside the disc
  (`plate-screw-left-H3` 10.9 mm³, `POM-left-H3` 26.2 mm³,
  `post-left-R4` 13.1 mm³): a plate support point must relocate.
- `wing_left` 447.4 mm³ — the module sinks 0.40 mm into the Wing PCB
  band (underside 5.50 < PCB top 5.90): the Wing needs a circular
  cutout where its sensor routing lives.
- `tray-left` 651.8 mm³ — a tray pocket under the Wing at the site.

Structural conflicts beyond the audit: the pad's data must cross the
Wing/Main seam. The formed FPC channel is 11.4 mm wide and already
carries the 10.2 mm Wing sheet — a second sheet does not fit; the
alternatives are reassigning lanes of the wireless Wing link (couples
the pad to the Wing respin and kills the pad whenever that Wing is
removed) or a second seam crossing that breaks the defined
Wing-removal service procedure (a #261 invariant). The layout also
drops from 42 keys — "42 keys" is a functional invariant of the
programme (#261 Stage 0), so this candidate changes the product
definition, not just the case. One-sided (left only) pointing is a
further ergonomic asymmetry. A Ø35 disc reduces the C5 graze class
but removes none of the structural items (not separately audited).

### 2.3 Candidate (c) — south-centre, user-side rim

Measured: tray outline max Y at |X| ≤ 12 is **70.40** (rim top
13.55); Main's south edge is at Y 67.90. **Usable centre shelf depth
= 2.50 mm.** The smallest module of either generation is Ø23.20 —
short by ≈20.7 mm before any bezel. Disc audits at (0,74) confirm
the position is mostly outside the case (Ø23: tray grazes of only
8.0/4.1 mm³ — the cylinder hangs in air). Even the case's deepest
shelf anywhere (16.80 mm, pinky band, D-037) is under the Wing key
field and still < 23.20 mm. The D-048 battery pod occupies the
under-case centre directly below this rim, and the rim is the
palm-heel approach line — both moot given the plan failure.

**Rejected on plan geometry: 2.50 mm available vs Ø23.20 mm minimum
module.**

## 3. Power — added to the Issue #284 model

Baseline (B1, D-048 pack): 0.533 Wh/day battery-side, 8.65 Wh
delivered → 16.2 days. Trackpad figures at the 3.3 V rail (datasheet,
§1.1); battery-side at η = 0.85 (the conversion assumption of the
AA-sizing study lineage). Day profile as in #284: typing 2 h,
desk-idle 6 h, away 16 h.

Stated usage assumption: **10 min/day of active tracking** (finger
moving) inside the typing window; idle for the remaining 110 min of
that window; sleep mode enabled by firmware (configuration register)
for the other 22 h.

| State | Rail power | Time/day | Rail energy |
|---|---|---|---|
| Active 2.9 mA | 9.57 mW | 0.167 h | 1.60 mWh |
| Idle 1.7 mA | 5.61 mW | 1.833 h | 10.29 mWh |
| Sleep 40 µA | 0.132 mW | 22 h | 2.90 mWh |
| **Total** | | | **14.79 mWh/day → 17.4 mWh battery-side** |

New daily total: 0.533 + 0.017 = **0.550 Wh/day → 8.65 / 0.550 =
15.7 days. Runtime cost of the trackpad: −0.5 day (16.2 → 15.7).**

Bounds: with shutdown (0.23 µA) instead of sleep during the 16 away
hours, −0.4 day. If sleep mode is never enabled and the pad idles at
1.7 mA through all 8 awake hours, +53.5 mWh/day battery-side →
14.7 days (**−1.5 days**) — the firmware configuration is worth a
full day; enabling sleep is a requirement, not an option.
Gen6s for contrast (§1.2, 23 mm figures): sleep 870 µA alone is
63 mWh/day rail; total ≈ +95 mWh/day battery-side → ≈13.8 days
(−2.4 days) even before its firmware gap.

Polling/wake behaviour: the host need not poll. The module's DR pin
(data-ready, pin 4 of the FFC) asserts when touch data is pending;
wired to an nRF52840 GPIO sense input it is a genuine wake source —
a finger touch can wake the whole keyboard from its away state.
Caveat: in sleep mode the pad senses at the configured interval
(3 s at the quoted 40 µA, datasheet note), so wake-from-touch
latency can reach that interval; shortening the interval raises the
sleep current. This is a firmware tuning trade to settle on the
bench, inside the −0.4…−1.5 day envelope above.

## 4. Protocol and firmware

### 4.1 Pointing over the Unifying link

Pairing carries exactly **one device-type byte** (pairing request 1,
byte 13 — LOGITacker, `logitacker/logitacker_pairing_parser.h`,
`LOGITACKER_UNIFYING_PAIRING_REQ1_OFFSET_DEVICE_TYPE 13`) and,
separately, a **32-bit device-report-types declaration** (request 2,
bytes 11–14 LE — same header,
`..._REQ2_OFFSET_DEVICE_REPORT_TYPES_LE 11`; parsed in
`logitacker_pairing_parser.c`). The type vocabulary (Solaar,
`lib/logitech_receiver/hidpp10_constants.py`, `DEVICE_KIND`):
keyboard 0x01, mouse 0x02, numpad 0x03, presenter 0x04, remote 0x07,
trackball 0x08, touchpad 0x09, …

Logitech's own combo products are the existence proof: the Wireless
Touch Keyboard K400 (WPID 400E/4024), K400 Plus (404D) and the
Illuminated Living-Room Keyboard K830 (4032) are single paired
devices — one `_D(...)` entry each in Solaar
`lib/logitech_receiver/descriptors.py` — whose kind resolves to
**keyboard** (the `_D` kind inference in the same file), while their
built-in touchpads deliver pointer reports under that same pairing.
Standalone touchpads (T650, WPID 4101) pair as kind touchpad 0x09
instead. The type byte names the product's primary function; the
report-types declaration is what licenses the second frame class.

Consequence for this design: **pair once as keyboard (0x01)** —
already mandatory, since the latest receiver firmwares block
character keys from non-keyboard types (Issue #280) — **declare
keyboard + mouse report types, and send mouse frames under the same
pairing.** No second receiver slot is consumed, and the trackpad
inherits the keyboard pairing's persistence.

New open items added to the Issue #287 bench proof (they extend,
not replace, its existing ten):
- **N1.** With the target receiver (the M575/M575SP-bundled unit;
  its generation is still to be confirmed), pair LOGITacker as a
  keyboard, declare keyboard + mouse report types, and verify both:
  encrypted keyboard frames produce characters **and** mouse frames
  move the host pointer, under the single pairing.
- **N2.** Is the REQ2 report-types field actually enforced by that
  firmware — i.e. are mouse frames dropped if the field declares
  keyboard only? (Determines whether the declaration is load-bearing
  or decorative.)
- **N3.** Do mouse frames share the keyboard frames' AES counter
  stream, or run an independent counter? (Ground truth: capture a
  real combo device if one can be borrowed; otherwise infer from
  receiver acceptance during N1.)

### 4.2 Firmware prior art (nRF52840 host side)

- **QMK — mature mainline.** `POINTING_DEVICE_DRIVER =
  cirque_pinnacle_i2c` / `cirque_pinnacle_spi` (docs.qmk.fm,
  *Pointing Device*, read 2026-11-19): "supports the Cirque Pinnacle
  1CA027 Touch Controller, which is used in the TM040040, TM035035
  and the TM023023 trackpads", with `CIRQUE_PINNACLE_DIAMETER_MM`,
  I2C address 0x2A, DR-driven reads and tap/gesture handling.
- **ZMK — documented mainline, not beta.** ZMK's pointing support
  builds on the Zephyr input API; its hardware-integration docs
  (zmk.dev/docs/hardware-integration/pointing, read 2026-11-19) show
  a `cirque,pinnacle` devicetree node with `dr-gpios` and a `sleep`
  property, listeners that emit HID mouse reports, and split-
  peripheral input support. The beekeeb Toucan — this study's
  layout cousin (Cantor/Piantor + TM040040 + XIAO nRF52840) — ships
  on exactly this stack.
- For this project the firmware is a custom nRF52840 stack
  (D-050/D-052), so the prior art's value is that the Pinnacle
  register protocol is fully understood and two independent open
  implementations exist to crib from (QMK's driver, Zephyr's
  `input_pinnacle`). Budget the driver as a port, not a research
  task. SPI vs I2C is a free choice on the nRF52840; the stocked
  Mouser SKUs are SPI-configured, ZMK's documented example is SPI,
  QMK supports both — SPI avoids the R1 rework.
- Gen6s: no QMK/ZMK driver exists; Cirque points to a Gen6s
  resource page and says more documentation is coming. A Gen6s
  choice today means writing the host driver from Cirque's
  developer interface alone.

## 5. Verdict — ranked by PO priorities (cost, low rework, freedom, speed)

| Rank | Candidate | Verdict |
|---|---|---|
| 1 | **(a) Central bay, TM040040-302 (Pinnacle, flat overlay), centre (0,48)** | **Adopt as the design input** |
| 2 | (b) Thumb cluster, one Wing | Rejected |
| 3 | (c) South-centre rim | Rejected |

**(a) wins on every priority axis.** Cost: the part is $9.63–11.56
(Mouser, in stock) — the cheapest candidate to realise, and the only
one needing no machined-metal change. Low rework: the case work is a
locally flattened Ø44 island + bezel pocket in the printed shell's
bay panel; the wireless Main absorbs the Ø40 component keep-out for
free in its new layout; no key, switch or sensor moves. Freedom: all
42 keys survive, both Wings stay removable by the existing procedure
(one added FFC disconnect when the shell is lifted), and the option
remains reversible — a bay panel printed without the pocket restores
the current case. Its accepted costs, stated plainly: the antenna
design moves to the south PETG zone (one of its two homes is
consumed); runtime −0.5 day (16.2 → 15.7); the wired configuration
would additionally need the Fly service loop re-dressed (255 mm³
conflict) and the tall Main ceramics moved — the wireless-first
scope carries neither.

**(b) rejected — binding constraints:** it deletes 2 of 42 keys
(T1/T2 envelopes, 1,165.7 + 1,166.8 mm³) and grazes a third
(R2_C5, 175.1 mm³) against the programme's 42-key invariant; the
plate's H3 fixing sits inside the disc (screw 10.9 + POM post
26.2 mm³) and the module sinks 0.40 mm into the Wing PCB band
(447.4 mm³) over live sensor routing; and its data cannot cross the
Wing/Main seam inside the 11.4 mm formed channel (already filled by
the 10.2 mm Wing sheet), so it either couples to the Wing link
redesign or breaks the Wing-removal service invariant.

**(c) rejected — binding constraint:** centre shelf depth **2.50 mm**
(tray outline Y 70.40 at |X| ≤ 12 vs Main south edge 67.90) against
a minimum module diameter of **Ø23.20 mm** — short ≈20.7 mm before
any bezel; the D-048 pod below the same rim and the palm-heel line
are secondary.

**Part-level verdicts:** Pinnacle TM040040-302 adopted as the study
recommendation (TM035035 = fallback, +0.25 mm stack, Ø35 bezel);
Gen6s generation rejected today (sleep 870 µA → −2.4 days class; no
QMK/ZMK driver); TM023023 Pinnacle rejected as the primary pointer
(Ø21.60 mm sensing).

## 6. Open items this study hands forward

1. Issue #287 bench proof gains open items N1–N3 (§4.1).
2. Wireless case work: design the antenna into the south PETG zone
   (the bay is no longer available to it); verify pad/antenna
   coexistence on the bench.
3. Wireless Main layout: Ø40 keep-out under the bay centre (0,48),
   12-pin FFC connector site for the pad on Main's top side, DR line
   to a wake-capable GPIO.
4. Firmware: Pinnacle sleep-mode configuration is a hard requirement
   (§3 — worth ≈1.0 day of runtime vs idle); sleep sensing interval
   vs wake latency is a bench tuning item.
5. Order-time stock re-verification for TM040040-2024-302 (project
   standing rule); buy spares with the prototype order.
