"""Manufacturing packages (DRAFT) for Wing Rev.6 x4 - Stage 2e regeneration (gerbers change with the notch outline; Main Rev.9 package from Stage 2b/2d stands unchanged).

Gerbers/drill/pos fresh from the new boards via kicad-cli; native
BOM.csv per the #263 method with the FH12 LCSC corrected to the real
JLCPCB code C5378715 (proven orderable in Issue #267); the JLCPCB
conversion files (BOM-jlcpcb.csv, BOM-jlcpcb-consolidated.csv,
CPL-jlcpcb-gerber-frame.csv) are carried over from the Issue #267
quote worktree — parts and footprint positions are unchanged by the
outline-only revision — and verified against the new boards
(designator sets, CPL coordinates — the #267 gerber-frame conversion
keeps the KiCad pos values verbatim, verified row-by-row).
FABRICATION.md and quote-handoff.md are written by hand alongside.
"""
import csv, subprocess, sys
from pathlib import Path
import pcbnew as p

MM = 1e6
CLI = "/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli"
ROOT = Path("/home/hatch/workspace/projects/he-piantor-wingnotch/hardware/kicad/qualification")
QUOTE = Path("/home/hatch/workspace/projects/he-piantor-quote/hardware/kicad/qualification/issue-263-implementation")

BOARDS = [
    (ROOT / "issue-270-wing-rev6" / f"wing-rev6-{v}", QUOTE / f"wing-rev5-{v}", f"wing-rev6-{v}")
    for v in ("17mm-left", "17mm-right", "16mm-left", "16mm-right")
]

def run(*args):
    subprocess.run([CLI, *args], check=True, capture_output=True)

for bdir, qdir, name in BOARDS:
    board = bdir / "main.kicad_pcb"
    out = bdir / "manufacturing"
    (out / "gerber").mkdir(parents=True, exist_ok=True)
    run("pcb", "export", "gerbers", "--output", str(out / "gerber"), str(board))
    run("pcb", "export", "drill", "--output", str(out / "gerber"), str(board))
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm",
        "--output", str(out / "CPL.csv"), str(board))
    # native BOM (#263 method; FH12 carries the real LCSC code)
    b = p.LoadBoard(str(board))
    rows = {}
    for f in b.GetFootprints():
        val = f.GetValue(); ref = f.GetReference()
        if ref in ("J2", "J3", "J_WING"):
            val = "FH12-14S-0.5SH(55)"
        key = (val, str(f.GetFPID().GetLibItemName()) if f.GetFPID() else "")
        rows.setdefault(key, []).append(ref)
    with (out / "BOM.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Quantity"])
        for (val, fp), refs in sorted(rows.items()):
            w.writerow([val, ",".join(sorted(refs)), fp,
                        "C5378715" if val.startswith("FH12") else "", len(refs)])
    # carry over the #267 JLCPCB conversions + verify
    for fn in ("BOM-jlcpcb.csv", "CPL-jlcpcb-gerber-frame.csv"):
        (out / fn).write_bytes((qdir / "manufacturing" / fn).read_bytes())
    # consolidated BOM: carried where #267 made one (17mm + Main); the
    # 16mm quotes were never taken, so derive it there by grouping the
    # per-designator BOM — derivation is asserted equal where both exist.
    def consolidate(rows):
        # #267 convention: group by (Comment, LCSC); Footprint column is
        # the first designator's footprint (the Rev4/Rev5 library item
        # names embed the designator but are the same physical footprint).
        groups = {}
        for r in rows:
            key = (r["Comment"], r["LCSC Part #"])
            for d in r["Designator"].split(","):
                groups.setdefault(key, []).append({"Designator": d.strip(), "Footprint": r["Footprint"]})
        out_rows = []
        for (comment, lcsc), rs in groups.items():
            rs = sorted(rs, key=lambda r: r["Designator"])
            out_rows.append({"Comment": comment,
                             "Designator": ",".join(r["Designator"] for r in rs),
                             "Footprint": rs[0]["Footprint"],
                             "LCSC Part #": lcsc, "Quantity": str(len(rs))})
        return sorted(out_rows, key=lambda r: r["Comment"])
    with (out / "BOM-jlcpcb.csv").open() as fh:
        derived = consolidate(list(csv.DictReader(fh)))
    qcons = qdir / "manufacturing" / "BOM-jlcpcb-consolidated.csv"
    if qcons.exists():
        with qcons.open() as fh:
            carried = list(csv.DictReader(fh))
        norm = lambda rows: sorted((r["Comment"], r["Designator"], r["Footprint"], r["LCSC Part #"], r["Quantity"]) for r in rows)
        assert norm(carried) == norm(derived), f"{name}: consolidated derivation mismatch"
        (out / "BOM-jlcpcb-consolidated.csv").write_bytes(qcons.read_bytes())
    else:
        with (out / "BOM-jlcpcb-consolidated.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #", "Quantity"])
            w.writeheader(); w.writerows(derived)
    # verify designator sets: JLCPCB BOM rows == board orderable designators
    with (out / "BOM-jlcpcb.csv").open() as fh:
        jlc = set()
        for r in csv.DictReader(fh):
            jlc.update(d.strip() for d in r["Designator"].split(","))
    board_refs = {f.GetReference() for f in b.GetFootprints()}
    excluded = board_refs - jlc
    assert jlc <= board_refs, f"{name}: JLCPCB BOM has unknown designators {jlc - board_refs}"
    # verify CPL conversion against the fresh native CPL (gerber frame: Y flipped)
    with (out / "CPL.csv").open() as fh:
        native = {r["Ref"]: r for r in csv.DictReader(fh)}
    with (out / "CPL-jlcpcb-gerber-frame.csv").open() as fh:
        conv = {r["Designator"]: r for r in csv.DictReader(fh)}
    assert set(conv) == set(native) - {r for r in native if r not in jlc} or set(conv) <= set(native)
    bad = []
    for ref, r in conv.items():
        n = native[ref]
        if abs(float(r["Mid X"][:-2]) - float(n["PosX"])) > 1e-6 or \
           abs(float(r["Mid Y"][:-2]) - float(n["PosY"])) > 1e-6:
            bad.append(ref)
    assert not bad, f"{name}: CPL mismatches {bad}"
    print(f"{name}: package ok; board refs {len(board_refs)}, JLCPCB BOM rows {len(jlc)}, "
          f"excluded {sorted(excluded)}, CPL rows {len(conv)} verified")
print("ALL PACKAGES DONE")
