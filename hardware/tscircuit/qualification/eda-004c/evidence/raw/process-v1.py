"""Bounded process capture; durable registration and raw preservation precede checks."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(name, command, cwd, timeout=120, artifacts=(), env=None, route=None):
    directory = EVIDENCE / "processes" / name
    directory.mkdir(parents=True, exist_ok=False)
    effective = os.environ.copy()
    effective.pop("DISPLAY", None)
    effective.pop("WAYLAND_DISPLAY", None)
    effective.update(env or {})
    record = dict(command=command, cwd=str(cwd), start_utc=utc(), end_utc=None,
                  exit_code=None, timeout_seconds=timeout, timed_out=False,
                  env_overrides=env or {}, display_unset=True, artifacts=[])
    save(directory / "record.json", record)
    if route:
        ledger_path = EVIDENCE / "attempt-ledger.json"
        ledger = json.loads(ledger_path.read_text())
        assert route in ("initial", "confirmation")
        assert not any(x["kind"] == route for x in ledger["attempts"])
        if route == "confirmation":
            assert ledger["initial_all_conditions_pass"] is True
        ledger["attempts"].append(dict(kind=route, registered_utc=utc(), process=name))
        save(ledger_path, ledger)  # fsync before Popen, including failed launch
    start = time.monotonic()
    with (directory / "stdout").open("wb") as out, (directory / "stderr").open("wb") as err:
        try:
            p = subprocess.Popen(command, cwd=cwd, env=effective, stdout=out,
                                 stderr=err, start_new_session=True)
            try:
                record["exit_code"] = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                record["timed_out"] = True
                os.killpg(p.pid, signal.SIGTERM)
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.wait()
                record["exit_code"] = p.returncode
        except OSError as e:
            record["launch_error"] = repr(e)
        finally:
            out.flush(); os.fsync(out.fileno())
            err.flush(); os.fsync(err.fileno())
    record["end_utc"] = utc()
    record["elapsed_seconds"] = time.monotonic() - start
    for label, path in artifacts:
        path = Path(path)
        item = dict(label=label, original_path=str(path), present=path.is_file())
        if path.is_file():
            target = directory / label
            with target.open("wb") as f:
                f.write(path.read_bytes()); f.flush(); os.fsync(f.fileno())
            item.update(saved_path=str(target.relative_to(ROOT)), sha256=digest(target))
        record["artifacts"].append(item)
    record["stdout_sha256"] = digest(directory / "stdout")
    record["stderr_sha256"] = digest(directory / "stderr")
    save(directory / "record.json", record)
    # Only now evaluate process status. Content checks belong to caller.
    if record["exit_code"] != 0 or record["timed_out"]:
        raise RuntimeError(f"{name}: process failed; evidence preserved")
    return record
