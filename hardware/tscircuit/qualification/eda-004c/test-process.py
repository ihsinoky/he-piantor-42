import json
from pathlib import Path
import sys
import tempfile
import process

original = process.EVIDENCE
with tempfile.TemporaryDirectory(prefix="eda004c-control-", dir="/tmp") as tmp:
    process.EVIDENCE = Path(tmp) / "evidence"
    raw = Path(tmp) / "partial.json"
    marker = Path(tmp) / "downstream"
    blocked = False
    try:
        process.run("failure", [sys.executable, "-c",
                    "from pathlib import Path; import sys; "
                    "Path(sys.argv[1]).write_text('{\\\"partial\\\":true}'); "
                    "print('raw captured'); print('injected failure',file=sys.stderr); sys.exit(7)",
                    str(raw)], tmp, artifacts=[("partial.json", raw)])
        process.run("downstream", [sys.executable, "-c",
                    "from pathlib import Path; import sys; Path(sys.argv[1]).touch()", str(marker)], tmp)
    except RuntimeError:
        blocked = True
    record = json.loads((process.EVIDENCE / "processes/failure/record.json").read_text())
    assert blocked and not marker.exists()
    assert not (process.EVIDENCE / "processes/downstream").exists()
    assert record["exit_code"] == 7 and record["start_utc"] and record["end_utc"]
    assert record["artifacts"][0]["sha256"] == process.digest(raw)
    # Deliberate content failure after successful process must also preserve raw.
    good = process.run("content-failure", [sys.executable, "-c", "print('invalid raw')"], tmp)
    assert good["exit_code"] == 0
    try:
        assert (process.EVIDENCE / "processes/content-failure/stdout").read_text() == "valid raw\n"
    except AssertionError:
        content_rejected = True
    assert content_rejected
    import shutil
    shutil.copytree(process.EVIDENCE, original / "control-fault-raw")
    process.save(original / "control-fault-tests.json", dict(status="PASS", tests=[
        "exit 7 stops downstream launch", "partial raw retained and hashed on failure",
        "stdout/stderr/timestamps/numeric exit retained", "raw retained before content rejection"],
        scope="process control only; no geometry qualification"))
print("process control fault injection PASS")
