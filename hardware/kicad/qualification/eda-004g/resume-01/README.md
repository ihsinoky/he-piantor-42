# EDA-004G PO-authorized resume 01 — terminal STOP

This separate evidence epoch preserves the initial STOP and read-only supplement.
Start `2026-10-14T02:48:37Z`, base `b3b6302a80799ccab2fcaed768199c5831a5d6ca`.
Experiments stopped at `2026-10-14T03:35:11.510027Z` on a frozen Main role-oracle
mismatch: AP2112K pin 4 expected `passive`, official/raw generated pin `no_connect`.
Do not fix the oracle after generation or run these scripts as authorization to
resume. Main initial/confirmation/transport routing attempts are **0/0/0**.

* `model-contract-v1.json`: independently transcribed four-part roles/numbers/NC
  and logical-to-physical correspondence, frozen before packaging.
* `main-contract-v1.json`: per-component/pin/physical-pad Main expectations,
  frozen before native capture and KiCad generation; **not accepted**. The AP2112K
  role-cache fallback defect is retained, not corrected.
* `library/Qualification.kicad_sym`: four bounded definitions. Official libraries
  are gzip archives; `evidence/library-evidence-archives.json` records exact
  expanded and archive hashes. Expand into a separate replay directory when
  inspecting with the recorded public cache/CLI. Do not modify old evidence.
* `evidence/processes/`: commands, environments, times, stdout/stderr, exit codes,
  and original inputs/outputs. Both failed and corrected pre-STOP generations
  remain. Successful-generation PCB has three distinct source USB bond segments;
  source's retraced 34 mm path has the same 17 mm material union. No historical
  routed copper was reused.
  Upstream Markdown with trailing whitespace is preserved byte-for-byte as gzip,
  rather than normalized; `raw-document-archives.json` records both hashes and
  original record paths. Integrity verification decompresses these raw artifacts.
* `evidence/stop-decision.json`, `post-stop-root-cause.json`: terminal decision
  and read-only diagnosis. A second checker deficiency (hardcoded NPTH enum) also
  prevents complete independent PCB acceptance. No repairs after STOP.

Authoring uses public kicad-sch-api and KiCad PCB objects. Public sexpdata only
packages library inputs and library registration, never generated Main files.
The two official symbols' editorial `private` annotation syntax was normalized
before regeneration, with original bytes/text retained. This is metadata format
compatibility, not an electrical/physical model substitution or private API.

These files are fixture-specific, unfinished evaluation code, not a converter,
production dependency or reusable accepted checker. Required four fault tests,
effective-rule injection, DSN/SES transfer, actual routed copper/spacing checks,
conditional confirmation and whole-environment rebuild remain unqualified or
not entered. See [the report](../../../../../docs/native-main-routing-qualification.md).
