"""Verify ZIP hashes and restore study tools to a new local folder without pip."""
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).absolute().parents[1]


def main():
    kit = ROOT / "output/laptop-kit"
    manifest = json.loads((kit / "travel-bundle.json").read_text(encoding="utf-8"))
    archive = kit / manifest["archive"]
    if archive.parent != kit or hashlib.sha256(archive.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("ZIP hash or path mismatch")
    scratch = ROOT / ".cache" / ("travel-restore-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    scratch.mkdir(parents=True)
    with zipfile.ZipFile(archive) as bundle:
        for name in bundle.namelist():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or not name.startswith("skhackathon/"):
                raise ValueError("Unsafe restore path")
        for member in manifest["members"]:
            if hashlib.sha256(bundle.read("skhackathon/" + member["path"])).hexdigest() != member["sha256"]:
                raise ValueError("Member hash mismatch")
        bundle.extractall(scratch)
    restored = scratch / "skhackathon"
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([sys.executable, "scripts/study.py", "--mode", "check"], cwd=restored,
                            env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    restored_check_path = restored / "reports/local-verification.json"
    restored_check = json.loads(restored_check_path.read_text(encoding="utf-8")) if restored_check_path.exists() else {}
    restored_python = restored / ".venv-study" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    pip_probe = subprocess.run([str(restored_python), "-c", "import importlib.util; print(importlib.util.find_spec('pip') is None)"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    report = {
        "checked_at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "archive": archive.name, "archive_sha256_matched": True, "member_hashes_matched": True,
        "fresh_folder_restore": True, "restored_folder": str(restored),
        "study_returncode": result.returncode, "restored_study_check_passed": restored_check.get("passed", False),
        "restored_test_count": restored_check.get("test_count"),
        "restored_environment_has_no_pip": pip_probe.returncode == 0 and pip_probe.stdout.strip() == "True",
        "skill_in_discoverable_path": (restored / ".agents/skills/hackathon-preflight/SKILL.md").is_file(),
        "installer_installation_tested": False, "exam_connection_tested": False,
        "network_scope": "No download command or service login; executed in network-restricted local sandbox",
        "output": result.stdout + result.stderr,
    }
    report["passed"] = result.returncode == 0 and report["restored_study_check_passed"] and report["restored_environment_has_no_pip"] and report["skill_in_discoverable_path"]
    (ROOT / "reports/travel-kit-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"output", "restored_folder"}}, ensure_ascii=False, indent=2))
    if not report["passed"]:
        print(report["output"][-4000:])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
