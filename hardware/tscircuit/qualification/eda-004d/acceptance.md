# Frozen acceptance before repair/conversion

Authority: Issue #77 at baseline 6684821a00bc2ebe368dcc78495d013eb5dd47d9.
Start: 2026-10-08 19:57:18 UTC. Maximum issue allowance 3 engineer-hours;
experiment cutoff 22:27:18 UTC, with at least 30 minutes reserved for reporting,
validation and PR. Continuous session wall time is a conservative AI effort
estimate; human effort and fully unattended time are unknown. Add to the prior
known 1.036 h estimate; do not reset the original 16 h backend budget.

Use the unchanged EDA-004C corrected synthetic fixture, raw and locks. Historical
raw may be replayed with commit/path/SHA-256 provenance; it is not fresh generation.
No Main generation, conversion or route. No output-file repair, exclusions,
clearance relaxation, pad or local-copper deletion.

Pre-route gates, all required before any router launch:

1. Fixed converter 0.0.230 / Git 8dee5b926f5db28800292b46b66a712c71aba055;
   kicadts f3ea106bdc65ca901e9b23255ad3be0bd2a624ab; original sources,
   patch, build lock, commands and hashes retained. Source pin attributes must
   exist explicitly. Contradictory internal net assignments must fail explicitly.
2. Independent EDA-004C source manifest reconciles every physical identity:
   five electrical lands including both U_TX pin2 lands, one 0.65 mm NPTH,
   positions, rotations, sizes, oval drills, plating and layers. Preserve the
   single 2 mm top GND local bond with 0.20 mm width and source provenance;
   no global routes, vias or pours. Absolute numeric tolerance 0.000001 mm,
   representing measurement resolution only. 20 x 16 mm, two layers, 1.2 mm.
3. Unique schematic definitions and instance references; exact pin numbers,
   names and explicit OUT/output, IN/input, GND/passive semantics; actual
   schematic connectivity agrees with the source graph, including SIG and GND.
4. KiCad 9.0.9 real ERC and DRC, configured libraries, source/project effective
   width/clearance/via/hole/edge rules and schematic/PCB parity. No unresolved
   warnings credited PASS. Evaluate historical solder_mask_bridge and schematic
   endpoint/off-grid issues. Pre-route expected required unrouted is 2; those
   intentional unconnected nets are distinct from post-route acceptance.
   No shorting_items or project-required material violation is acceptable.
5. Real ERC detects an intentional output/output input mutation; independent
   checker fault tests detect net/geometry/pin/rule/copper loss. Full independent
   physical connectivity/short/clearance checker required for final acceptance.

STOP immediately on missing source semantics, a new conversion loss, broad
redesign need, unresolved pre-route mismatch, or budget exhaustion. Preserve
each process stdout/stderr, numeric exit, UTC times, artifacts and hashes before
judgment. After STOP only read-only verification, records, commit/push/PR.

Only after all pre-route gates PASS: freeze input/rules/tool hashes and routing
settings, then one KiCad -> DSN -> Freerouting -> SES -> KiCad synthetic run.
Launch failure/timeout/crash/partial output consumes that attempt. Only initial
all-conditions PASS permits one fresh recreated-environment confirmation.
No retry after either failure. For each final run require required unrouted=0,
wrong-net physical copper=0, project-required material DRC=0, exact source/rule
parity, qualified checker and fresh agreement. Unentered metrics are null with
NOT ENTERED status, never zero. CI SKIPPED is not qualification PASS.
