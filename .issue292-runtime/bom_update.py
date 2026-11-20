#!/usr/bin/env python3
"""Issue #292 order-prep: assign verified LCSC codes in both JLCPCB BOMs.
Per-designator BOM gets code + note; consolidated BOM gets code (+comment fixes).
Fails loudly if any expected designator is missing."""
import csv, sys

BASE = "/home/hatch/workspace/projects/he-piantor-wmain/hardware/kicad/qualification/issue-292-wmain/manufacturing"

# designator -> (lcsc, note)
ASSIGN = {
    "CHIN":  ("C15849", "Samsung CL10A105KB8NNNC 1uF +/-10% 50V X5R 0603, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CHOUT": ("C15849", "Samsung CL10A105KB8NNNC 1uF +/-10% 50V X5R 0603, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CPOUT": ("C15849", "Samsung CL10A105KB8NNNC 1uF +/-10% 50V X5R 0603, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CVAUX": ("C15849", "Samsung CL10A105KB8NNNC 1uF +/-10% 50V X5R 0603, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CVCC1": ("C15849", "Samsung CL10A105KB8NNNC 1uF +/-10% 50V X5R 0603, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CIN1":  ("C45783", "Samsung CL21A226MAQNNNE 22uF +/-20% 25V X5R 0805, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CIN2":  ("C45783", "Samsung CL21A226MAQNNNE 22uF +/-20% 25V X5R 0805, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "COUT1": ("C45783", "Samsung CL21A226MAQNNNE 22uF +/-20% 25V X5R 0805, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "COUT2": ("C45783", "Samsung CL21A226MAQNNNE 22uF +/-20% 25V X5R 0805, JLCPCB Basic, InStock at JLCPCB (verified 2026-11-19)"),
    "CVS":   ("C1589",  "Samsung CL10B103KB8NNNC 10nF +/-10% 50V X7R 0603 (verified 2026-11-19)"),
    "D1":    ("C255588", "Nexperia PMEG4020ER,115: ER = SOD123W (CFP3) flat-lead variant of PMEG4020 (Nexperia suffix per AN10808: R=SOD123W, P=SOD128 - P does NOT fit); 40V 2A Vf max 490mV@2A; pin1=K pin2=A matches board; land-fit verified vs SOD-123 pads (toe overhang <=0.05mm at tolerance corner only). Second source: TECH PUBLIC PMEG4020ER C19268150 (quote-matched 2026-11-19)"),
    "D2":    ("C255588", "Nexperia PMEG4020ER,115: ER = SOD123W (CFP3) flat-lead variant of PMEG4020 (Nexperia suffix per AN10808: R=SOD123W, P=SOD128 - P does NOT fit); 40V 2A Vf max 490mV@2A; pin1=K pin2=A matches board; land-fit verified vs SOD-123 pads (toe overhang <=0.05mm at tolerance corner only). Second source: TECH PUBLIC PMEG4020ER C19268150 (quote-matched 2026-11-19)"),
    "DLED":  ("C12624", "KENTO KT-0603G emerald green 525nm 0603, LCSC InStock (verified 2026-11-19). POLARITY: board pad1 = anode (LED_A), pad2 = cathode (GND); confirm JLCPCB library pin1 = anode at quote, else set CPL rotation 180deg for DLED"),
    "JBATT": ("C161690", "JST GH top-entry 2P 1.25mm pitch 1A/50V. Board land measured: 2 SMD pads 0.6x1.7mm at 1.25mm pitch, outline 5.9x4.4mm - fits BM02B-GHS-TBT body (B=5.75mm wide, 4.25mm deep). NOTE: board land has no reinforcement-tab pads (JST recommended layout includes them) - retention is by the 2 signal solder joints only. LCSC InStock (verified 2026-11-19)"),
    "Q1":    ("C8545",  "JSCJ 2N7002 SOT-23 60V/115mA, JLCPCB Basic, LCSC InStock (verified 2026-11-19); pinout 1=G 2=S 3=D matches board"),
    "RFA":   ("C23212", "UNI-ROYAL 0603WAF6801T5E 6.8k 0603, JLCPCB Basic (verified 2026-11-19)"),
    "RFB":   ("C23212", "UNI-ROYAL 0603WAF6801T5E 6.8k 0603, JLCPCB Basic (verified 2026-11-19)"),
    "RFC":   ("C23212", "UNI-ROYAL 0603WAF6801T5E 6.8k 0603, JLCPCB Basic (verified 2026-11-19)"),
    "RFB1":  ("C23184", "UNI-ROYAL 0603WAF4992T5E 49.9k +/-1% 0603 (quote-verified 2026-11-19; the site auto-match was a through-hole resistor - do not accept it)"),
    "RFB2":  ("C4210",  "UNI-ROYAL 0603WAF1602T5E 16.0k +/-1% 0603 (quote-verified 2026-11-19; the site auto-match was a USD 327 relay - do not accept it)"),
    "RPU1":  ("C23162", "UNI-ROYAL 0603WAF4701T5E 4.7k 0603, JLCPCB Basic (verified 2026-11-19)"),
    "RPU2":  ("C23162", "UNI-ROYAL 0603WAF4701T5E 4.7k 0603, JLCPCB Basic (verified 2026-11-19)"),
    "RV1":   ("C22935", "UNI-ROYAL 0603WAF1004T5E 1M 0603, JLCPCB Basic (verified 2026-11-19)"),
    "RV2":   ("C22935", "UNI-ROYAL 0603WAF1004T5E 1M 0603, JLCPCB Basic (verified 2026-11-19)"),
    "SW1":   ("", "DO NOT PLACE at JLCPCB - hand-fit at bring-up. Generic 2-pad tact land (design provision, not a specific part): pads 1.2x1.8mm at +/-1.6mm (3.2mm pitch), outline 5.2x3.0mm. Intended class 3x4x2mm 2-pin turtle tact (e.g. YIZHI YZA-009 C49108621) but its terminal pitch is not published in the listing - verify against the physical part before any future placement"),
}
COMMENT_FIX = {"JBATT": "BM02B-GHS-TBT (JST GH 2P)", "SW1": "TACT (bring-up) - DNP hand-fit"}

def expand(cell):
    return [d.strip() for d in cell.split(",") if d.strip()]

# --- per-designator BOM ---
p1 = f"{BASE}/BOM-jlcpcb.csv"
rows = list(csv.DictReader(open(p1, newline="")))
seen = set()
for r in rows:
    d = r["Designator"].strip()
    if d in ASSIGN:
        code, note = ASSIGN[d]
        r["LCSC Part #"] = code
        r["Note"] = note
        seen.add(d)
    if d in COMMENT_FIX:
        r["Comment"] = COMMENT_FIX[d]
missing = set(ASSIGN) - seen
if missing:
    sys.exit(f"per-designator BOM missing designators: {missing}")
with open(p1, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #", "Note"])
    w.writeheader(); w.writerows(rows)

# --- consolidated BOM ---
p2 = f"{BASE}/BOM-jlcpcb-consolidated.csv"
rows2 = list(csv.DictReader(open(p2, newline="")))
seen2 = set()
for r in rows2:
    for d in expand(r["Designator"]):
        if d in ASSIGN:
            code = ASSIGN[d][0]
            if r["LCSC Part #"] and r["LCSC Part #"] != code:
                sys.exit(f"consolidated conflict {d}: {r['LCSC Part #']} vs {code}")
            r["LCSC Part #"] = code
            seen2.add(d)
        if d in COMMENT_FIX:
            r["Comment"] = COMMENT_FIX[d]
missing2 = set(ASSIGN) - seen2
if missing2:
    sys.exit(f"consolidated BOM missing designators: {missing2}")
with open(p2, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #", "Quantity"])
    w.writeheader(); w.writerows(rows2)
print(f"OK: {len(seen)} designators updated in per-designator BOM, {len(seen2)} in consolidated")
