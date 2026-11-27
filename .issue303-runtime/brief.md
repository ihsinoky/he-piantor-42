# Stage 1 brief — wireless power board CIRCUIT design (Issue #303)

## Scope

Circuit design ONLY: schematic, parts selection with availability scan,
contact-field geometry derived from the cell dimensions, and a design note.
**No board layout** — the outline/placement wait for the Wing redesign's
proven delta (Issue #299) and the case geometry (Issue #296). Do not create
a routed board; a schematic + an unrouted placement sketch of the contact
field (for geometry verification only, clearly marked NOT the layout) is
acceptable if it helps prove the series topology.

Worktree: `~/workspace/projects/he-piantor-pwr`, branch `issue-303-pwr`,
base origin/main `d9e64ef41`. Design tree:
`hardware/kicad/qualification/issue-303-pwr/` (follow the repo's existing
qualification-tree conventions; look at the issue-288/292 trees).

Background records to read first:
- Issue #303 (gh issue view 303) — purpose, inputs, pass conditions.
- The centre-arrangement study:
  `~/workspace/goals/he-piantor-42-keyboard-pmo/hidden_files/cell-arrangement-centre-2026-11-20.md`
  (3-cell geometry, floor-board wiring: 2 bridges + return pour, JBATT
  cable ≈100 mm, Fly relocation, thresholds).
- D-048 / D-059 / D-060 / D-062 in `docs/decisions.md` (cell choice,
  thin power-board construction, centre arrangement).
- The wireless Main tree (origin/main): JBATT = JST BM02B-GHS-TBT (GH
  1.25 mm 2P) at Main's south edge; VBAT_SENSE thresholds per D-062
  (pack 3.15 V / 2.85 V). This board is power-only.

## Design inputs (fixed)

- Cells: **3× AA NiMH** (eneloop-class BK-3MCD), axes N-S, side by side
  E-W; block envelope 48.5 (E-W) × 56 (N-S) mm; cells rest on this board.
- End contacts: Keystone 209-class leaf springs (or verified equivalent);
  the positive contact's recessed "location facility" mechanically keys
  reverse insertion. Contact positions derive from the AA cell dimensions
  (Ø14.5 × 50.5 mm class; state the exact cell datum you use and its
  source).
- Series topology: cell1+ → cell2−, cell2+ → cell3− via **2 bridges**;
  one **return pour** brings the far terminal back so both pack terminals
  exit on the same (south) side toward Main. A bridge error shorts a
  cell — prove the topology against the contact geometry explicitly
  (table or diagram: each contact, its cell terminal, its net).
- Protection: series PTC, Littelfuse 1206L050/24WR class (500 mA hold /
  ~1 A trip). No series diode.
- Switch: slide switch in series in the battery path (true 0-current
  OFF), SS-12D10 class, rated ≥0.5 A. C&K OS102011MA1QN1 (0.1 A) is
  undersized — do not use. Study board-mounted vs off-board (bay wall /
  cable) placement; recommend one with reasons (serviceability, case
  interface, current rating, availability).
- Output termination: 2-wire, ~100 mm cable to Main's JBATT (GH). Study
  GH connector on this board vs solder pads; recommend with reasons.
- Test points for pack voltage: include if free (state why/why not).

## Verification invariants

1. Reproduce/derive before asserting: the series topology check must be
   computed from the contact geometry, not drawn from memory.
2. Distrust the first passing check — ERC 0 alone does not prove the
   series path; the topology table is the evidence.
3. Continue until verification is complete and evidenced.

## Availability scan (mandatory, PO rule)

For every selected part (contacts, PTC, switch, connector/pads hardware):
source(s), stock observed with date, LCSC code if it could ever be PCBA,
and hand-fit vs PCBA disposition. Contacts and switch are expected to be
hand-fit/mechanical — say so explicitly where true.

## Deliverables

1. Schematic in the design tree (KiCad), ERC 0, committed + pushed.
2. `.issue303-runtime/design-note.md`: topology proof table, parts list
   with availability, switch + termination recommendations with reasons,
   cell datum used, and the exact list of inputs Stage 2 layout needs
   (bay inner dimensions, floor level, cable exit position, switch
   position if board-mounted).
3. Draft PR opened (title: Issue #303 power board Stage 1 — circuit
   design), comment on Issue #303 summarising Stage 1.
4. One line appended to
   `~/workspace/goals/he-piantor-42-keyboard-pmo/GOAL.md`.

Working style: short plan note first; checkpoint commits; scripts/logs in
`.issue303-runtime/`; keep response segments short.
