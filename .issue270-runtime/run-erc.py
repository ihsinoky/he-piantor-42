import subprocess
CLI = "/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli"
r = subprocess.run([CLI, "sch", "erc", "--format", "json", "-o",
                    ".issue270-runtime/erc-main-2d.json",
                    "hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_sch"],
                   capture_output=True, text=True)
print(r.returncode, r.stdout[-200:], r.stderr[-200:])
