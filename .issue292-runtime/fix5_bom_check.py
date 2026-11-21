#!/usr/bin/env python3
"""F5 check: per-reference BOM designator set vs board footprint references.
Result on the D-061 tree (2026-11-21): 55 board refs, 55 BOM rows, no
duplicates, sets exactly equal, exactly one JSWD row. The review's
duplicate-JSWD premise does NOT reproduce (also checked BOM at git
8eb9a23fa / d85ad9b57^ / d3c834d46: one JSWD row each). No BOM edit made -
removing the single JSWD row would break set equality."""
import pcbnew, csv, sys
from collections import Counter

D = "hardware/kicad/qualification/issue-292-wmain"
b = pcbnew.LoadBoard(f"{D}/wmain.kicad_pcb")
board_refs = sorted(fp.GetReference() for fp in b.GetFootprints())
rows = list(csv.DictReader(open(f"{D}/manufacturing/BOM-jlcpcb.csv")))
bom_refs = sorted(r["Designator"] for r in rows)
print("board refs:", len(board_refs), "bom rows:", len(bom_refs))
print("duplicates in BOM:", [k for k, v in Counter(bom_refs).items() if v > 1])
print("in BOM not on board:", sorted(set(bom_refs) - set(board_refs)))
print("on board not in BOM:", sorted(set(board_refs) - set(bom_refs)))
print("sets equal:", set(board_refs) == set(bom_refs)
      and len(bom_refs) == len(set(bom_refs)))
