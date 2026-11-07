# Wing Rev.3 case inputs (Issue #200)

`python3 hardware/case/issue-200-rev3/generate.py` regenerates the four sets of
keys, locator/mounting holes and complete Stage 1b shoulder/stepped profiles.
Wing local X right/Y north; KiCad = (100+x, 100-y). Angles are top-view CCW.
Use the unchanged transforms in `../issue-200-stage1/geometry.json` for assembly.
H1 left / H3 right use the Stage 1 mounting candidates, not the old south holes.
These are mechanical interface data, not a generated case (Issue #198 owns it).
