#!/bin/bash
set -eu
E=hardware/kicad/qualification/issue-250-df52
RUN="$E/run.sh"
bash "$RUN" python3 hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py "$E/main/main.kicad_pcb" "$E/main/snapshot.json"
python3 - <<'PY'
from pathlib import Path
import json
E=Path('hardware/kicad/qualification/issue-250-df52');w=E/'main';d=json.loads((w/'qualification.json').read_text())
(w/'assessment.json').write_text(json.dumps(dict(pass_acceptance=d['routing_pass'],metrics=dict(required_unconnected=d['independent_unconnected'],wrong_net_contacts=d['wrong_net_contacts'],material_violations=d['native_drc_violations'],unexplained_transfer_changes=len(d['invariant_errors'])),status='Diagnostic extraction; board full gate status remains failed'),indent=2)+'\n')
(w/'connectivity.json').write_text(json.dumps(dict(nets_checked=d['nets_checked'],required_unconnected=d['independent_unconnected'],wrong_net_contacts=d['wrong_net_contacts']),indent=2)+'\n')
PY
bash "$RUN" python3 "$E/extract-power.py" final
bash "$RUN" python3 "$E/extract-ground.py" final
bash "$RUN" python3 "$E/summarize-resistance.py"
bash "$RUN" python3 "$E/verify-ground-model.py"
