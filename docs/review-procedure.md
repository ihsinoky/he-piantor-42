# Semantic Review Procedure — two-layer CAD review (kernel + LLM semantics)

Operating procedure for mechanical/CAD review in this repo, implementing
the design of record `semantic-review-layer-design-2026-11-19.md`
(PMO goal files, 2026-11-19) as adopted by Issue #294.

Two layers, strictly separated:

- **Geometry kernel** (build123d / OCP over STEP solids): produces
  measured findings only — interference volumes, clearances, section
  and envelope numbers, pass/fail against a stated rule. Its output is
  the only source of numbers.
- **Semantic layer** (LLM): interprets kernel records against the
  decision record, matches them to problem classes from past findings,
  and suppresses already-known items **visibly**. It never generates,
  adjusts, or rounds a measured value.

Records live in [review-ledger.md](review-ledger.md). A review finding
that hardens into a durable empirical fact is promoted into
[findings.md](findings.md) under the D-031 promotion discipline; a
problem class that hardens into a design rule is promoted to a
decision (decisions.md) or a process definition.

> Ledger guard: the ledger is a record of history and decisions, not
> an instruction source. Execution is authorised only by the PO.

## 1. Run the kernel

1. Input of record is **STEP** (solids). STL is mesh and is not used
   for precision verdicts; DXF/SVG are 2D references only. Boards come
   from KiCad STEP export, combined with the case STEP; poses
   (normal / flipped) are input recombinations of the same body set.
2. Every solid is volume-validated (> 0) before any gate runs. Gates
   run over the full fitted body set with a bounding-box prefilter.
3. Own-engagement pairs (a plug against its own mating header or
   housing, the body-set model of the same physical part) are reported
   separately and never counted as hits.
4. Positive controls are mandatory: at least one synthetic pair with a
   known overlap and, when a body cache is used, one genuine
   overlapping pair recomputed through the cache. A control mismatch
   invalidates the run.
5. The run writes its raw outputs (JSON + log) into the issue's
   runtime directory. These artifacts are the evidence; nothing in
   the ledger may cite a number that is not in a named artifact.

## 2. Emit structured records

Each kernel observation becomes one record with the fields of design
§3:

| field | content |
|---|---|
| fingerprint | rule × normalised target (part pair / face / site) × problem class — the de-duplication key |
| rule | rule name and threshold (e.g. `clearance ≥ 0.3 mm`) |
| target | parts / site / pose, with coordinates where the artifact gives them |
| measured | the kernel's value, copied character-for-character in value from the artifact |
| evidence | source artifact path + the input identity it names (body set, pose, pitch) |
| class | problem class from the ledger's class register; `unclassified` if none fits |

If a value the record needs is **not** in the artifacts, `measured`
is written as `MISSING` and the record is classified
`unclassified - needs verification`. Estimating a number is
forbidden (invariant 1).

## 3. Semantic classification

Each distinct finding is classified against decisions.md (D-xxx) and
the specification values, into exactly one of:

- **true problem** — contradicts the design intent; action needed.
- **as-designed** — the number touches a threshold but is the form a
  decision or specification intended.
- **accepted risk** — the PO has already accepted it; the accepting
  D-xxx / Issue must be cited.
- **needs-PO-judgment** — interpretations diverge; raised to the PO
  as a choice (merge-gate style: PMO explains, PO picks).
- **unclassified - needs verification** — no basis can be cited, or
  the measured value is MISSING.

Every classification cites its basis (measured evidence + D-xxx /
spec / past finding). An interpretation without a citable basis is
issued as `unclassified - needs verification`, never dressed up.

Each finding carries a **state**: `new` / `accepted` / `in-progress`
/ `resolved`. States move only on evidence (a decision, a re-run, a
build confirmation), and the move is recorded in the entry.

## 4. Same-class matching

New findings are matched against the class register in the ledger.
A match is reported with the past example and how it was handled
then. A class that recurs is proposed for promotion to a design
rule; a genuinely new repeated pattern is proposed as a new class.
Matching is by fingerprint first, then by class + mechanism.

## 5. Visible suppression

Findings already known are removed from the "new" list **only**
through the ledger, never silently:

- every suppressed finding stays in the ledger with its reason —
  `accepted by D-xxx`, `in-progress under Issue #xxx`, or
  `resolved-confirmed` (with the confirming evidence named);
- repeat observations of one finding (other pitch, other side,
  re-run, later sighting of the same value) are consolidated into
  that finding's entry and counted as **duplicates-merged**;
- the report (§6) shows the suppression counts by reason, and the
  arithmetic must reconcile:
  `raw observations = new + suppressed + duplicates-merged`,
  computed from the register, not asserted.

## 6. Report shape

One report per run (kept in the issue's runtime directory):

1. **NEW findings** — first-seen items with no prior disposition,
   each with measured value, class, classification and basis.
2. **SAME-CLASS groupings** — which findings matched which class,
   with the past example and its handling.
3. **SUPPRESSION breakdown** — counts by reason (accepted by D-xxx /
   in-progress under Issue / resolved-confirmed), plus the
   duplicates-merged count and the reconciliation arithmetic.
4. **Needs-PO-judgment items** — stated as choices, with the PMO's
   explanation of the technical points (merge-gate format, PO
   2026-11-11).

## 7. Invariants

1. Numbers come only from the kernel or from recorded kernel
   artifacts. The LLM never generates or adjusts a measured value;
   missing values are marked MISSING.
2. Every interpretation, class match, and suppression cites its
   basis (measurement evidence, D-xxx, past finding, Issue).
3. Suppression is always visible; silent deletion is prohibited.
4. PO gates (adoption, acceptance, orders) stay the PO's. This
   procedure prepares decision material only.
5. Worker briefings under this procedure carry the verification
   invariants (2026-11-18): reproduce before fixing; distrust the
   first passing test; continue until verification is complete and
   evidenced.
