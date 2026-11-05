"""Copy #138 read-only inputs for a self-contained, hash-pinned DC comparison."""
from common import *
import shutil
P=E.parent/'issue-138-wing-manufacturing-review-prep';dest=E/'baseline138';dest.mkdir(exist_ok=False)
names=['KRT-16-2L-0100-inventory.json','KRT-17-2L-0100-inventory.json','dc-drop-estimate.json','estimate-dc-drop.py']
for n in names:shutil.copyfile(P/n,dest/n);assert digest(P/n)==digest(dest/n)
save(dest/'provenance.json',dict(sources=[dict(path=str((P/n).relative_to(R)),sha256=digest(P/n)) for n in names],copies_byte_identical=True,source_files_unmodified=True))
