# Issue175 PCBA quotation handoff — no order / charge

Source: `../inspection/final/main.kicad_pcb`, SHA256 `acab039f3b5f5ea30500d2f8537e320e198f881c227a3c3042753fc021c30f1c`.
PCB qualification and CAM comparison pass. This is a quotation/review package; manufacturing acceptance and final price are outstanding.

- Quote five Main boards, 48 × 52 mm, four layers, finished thickness 1.2 mm, 0.10 mm signal width/clearance, 0.60/0.30 mm vias. Preserve D-019; do not substitute routing conditions.
- Use fabrication ZIP, BOM.csv and CPL.csv in this folder. Paste files are in paste/. CPL is relative to (76,122) with Y inverted; 58 assembled components per board, 62 electrical references including four bare testpads.
- C26/C27/C28: exact TDK C3225X7R1C226K250AC, 1210. R17: TNPW060354K9BEEA. Blank LCSC codes require exact procurement matching, not automatic substitution. Check stock/MOQ/attrition and NRND status for TDK.
- Economic PCBA with J1's twelve SMD contacts and four PTH shell legs in the same order/process. Obtain explicit eligibility/process acceptance; do not switch to Standard or omit the PTH legs.
- Epoxy-filled and copper-capped POFV. Supply ../all-vias.csv (all 113 vias), ../pofv-sites-final.csv (32 candidates) and ../pofv-reclassification-final.json. Obtain accepted fill scope, 0.60/0.30 mm compatibility and four-layer surcharge. Exclude J1 PTH legs and all NPTH holes from fill.
- Confirm actual copper/plating/stackup and any stencil/assembly process changes. Original paste was exported faithfully; vendor review is pending.
- Record quote ID/date/expiry, currency, PCB/POFV/stencil/components/assembly/J1 costs, attrition/MOQ, shipping/tax, total and acceptance notes against these exact source hashes. Do not reuse the prior smaller board/seed-a estimate.

Current total, quote ID and expiry: **null / unconfirmed**. No upload, cart, order, charge or support message was made. Access to the vendor quote workflow is required to complete this step.
