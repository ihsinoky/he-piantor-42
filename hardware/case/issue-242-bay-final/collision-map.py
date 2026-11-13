"""Measure existing rejected contacts; never change or search routing geometry."""
import importlib.util
import json
import sys
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("binding", HERE / "binding.py")
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)

def main(pitch):
    out = HERE / f"{pitch}mm"
    audit = json.loads((out / "audit.json").read_text())
    assert audit["all_exact_candidates_completed"] and not audit["boolean_errors"]
    cache = HERE.parents[2] / f".issue242-runtime/audit{pitch}"
    rows = []
    for hit in audit["unexpected_interferences"]:
        a = binding.load(cache / f"{hit['i']}.brep")
        b = binding.load(cache / f"{hit['j']}.brep")
        op = BRepAlgoAPI_Common(a.wrapped, b.wrapped)
        op.SetRunParallel(True)
        op.SetUseOBB(True)
        op.Build()
        assert op.IsDone() and not op.Shape().IsNull()
        common = binding.Shape.cast(op.Shape())
        props = GProp_GProps()
        BRepGProp.VolumeProperties_s(op.Shape(), props, True, False, False)
        assert abs(abs(props.Mass()) - hit["volume_mm3"]) < 1e-4
        bounds = common.bounding_box()
        rows.append(dict(**hit, remeasured_volume_mm3=abs(props.Mass()),
                         repeat_volume_tolerance_mm3=1e-4, overlap_bounds_mm=[
            [getattr(bounds.min, axis) for axis in "XYZ"],
            [getattr(bounds.max, axis) for axis in "XYZ"]]))
    (out / "collision-map.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(pitch, "mapped", len(rows), "existing rejected contacts", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]))
