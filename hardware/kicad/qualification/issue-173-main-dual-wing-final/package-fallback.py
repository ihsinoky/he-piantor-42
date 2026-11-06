"""Collect unchanged, already-qualified seed-a; never relabel it as 1210."""
from common import *
import shutil
old=R/'hardware/kicad/qualification/issue-169-main-dual-wing-followup';dest=E/'fallback-seed-a'
dest.mkdir(exist_ok=False);mapping={}
for folder in ['inspection/final','Stage169.pretty','manufacturing-seed-a-review','design-seed-a']:
 for src in (old/folder).rglob('*'):
  if not src.is_file():continue
  rel=src.relative_to(old);target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
  mapping[str(target.relative_to(E))]=dict(source=str(src.relative_to(R)),sha256=digest(src))
for name in ['main-bom-seed-a.csv','component-selection.json','circuit-check-final.json','cam-check.json','export-provenance.json','pofv-reclassification-seed-a.json','pofv-sites-seed-a.csv','power-extraction-seed-a.json','ground-extraction-seed-a.json','ground-model-verification.json','resistance-summary.json']:
 src=old/name;target=dest/name;shutil.copyfile(src,target);mapping[str(target.relative_to(E))]=dict(source=str(src.relative_to(R)),sha256=digest(src))
save(E/'fallback-provenance.json',dict(utc=now(),source_commit='c741ade9550157333443784b90e2fe66f95ca297',board_kind='Issue169 seed-a, paste-corrected, 0805 output capacitors',byte_identical_copies=mapping,copper_edits=0,routing=0,new_manufacturing_generation=False,new_resistance_extraction=False,new_POFV_classification=False,manufacturing_release=False,known_limitation='Output GRM21BC81C226ME44L x3 loses >50% capacitance near 5.35V on typical DC-bias curve; tolerance, temperature and ageing further reduce margin. No guaranteed effective output capacitance or transient performance.'))
print('Archived seed-a',len(mapping),'unchanged files; review-only CAM')
