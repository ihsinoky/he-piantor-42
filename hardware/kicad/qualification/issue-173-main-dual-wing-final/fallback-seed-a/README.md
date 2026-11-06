# seed-a — qualified routing, output-capacitance limitation

This package is an unchanged copy of Issue169's paste-corrected 0805 seed-a. Routing qualification was 44 nets / four metrics zero. The 1210 Issue173 candidate failed preflight and has no routing result.

Open `inspection/final/main.kicad_pcb` with its matching project and `Stage169.pretty` library. Its matching assembly files are `manufacturing-seed-a-review/BOM.csv` and `CPL.csv`; review CAM and ZIP are in the same directory. `design-seed-a/` contains the archived source circuit. Provenance is in `../fallback-provenance.json`.

**Known limitation:** C26–C28 are GRM21BC81C226ME44L 22µF/16V/X6S/0805, not the selected TDK1210 parts. More than half the nominal capacitance is lost around 5.35V on the typical DC-bias curve; tolerance, temperature and ageing further reduce margin. No guaranteed minimum effective output capacitance or transient performance has been established.

Review only; no manufacturing GO, confirmed PCBA quote, order or billing. PO decides how to proceed. Do not combine this CAM with the 1210 BOM. Old JSON source paths/timestamps are preserved as historical records. The circuit archive is a semantic re-export; its XML is not asserted to have the earlier circuit-check's export hash.
