"""Create a local study environment and run practice on Windows or macOS/Linux.

Only an already installed Python 3.11+ and its standard library are used.
This script never downloads packages or removes an existing environment.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).absolute().parents[1]
MINIMUM_VERSION = (3, 11)


def environment_python(root):
    directory = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return root / ".venv-study" / directory / executable


def recovery_message(root):
    return ("Existing .venv-study was kept. Rename that folder to a backup name "
            "and run this command again with an installed Python 3.11+. "
            "Do not copy a virtual environment between computers. Folder: "
            + str(root / ".venv-study"))


def prepare_environment(root):
    if sys.version_info < MINIMUM_VERSION:
        raise RuntimeError("Run scripts/study.py with an installed Python 3.11 or newer.")
    python = environment_python(root)
    environment = root / ".venv-study"
    if environment.exists() and not python.is_file():
        raise RuntimeError(recovery_message(root))
    if not environment.exists():
        created = subprocess.run(
            [sys.executable, "-m", "venv", str(environment), "--without-pip"],
            cwd=str(root), check=False,
        )
        if created.returncode != 0 or not python.is_file():
            raise RuntimeError("Study environment creation failed. " + recovery_message(root))
    try:
        probe = subprocess.run(
            [str(python), "-c", "import json,sys; print(json.dumps(list(sys.version_info[:2])))"],
            cwd=str(root), capture_output=True, text=True, encoding="utf-8", check=False,
        )
        version = json.loads(probe.stdout) if probe.returncode == 0 else []
        supported = (isinstance(version, list) and len(version) == 2
                     and all(type(value) is int for value in version)
                     and tuple(version) >= MINIMUM_VERSION)
    except (OSError, ValueError):
        supported = False
    if not supported:
        raise RuntimeError(recovery_message(root))
    return python


def command_for(mode, python, case_id="RC02"):
    prefix = [str(python)]
    if mode == "check":
        return prefix + [str(ROOT / "scripts" / "verify.py")]
    if mode == "learn":
        return prefix + ["-m", "practice", "quiz", "--bank", "backend", "--count", "20"]
    if mode == "timed":
        return prefix + ["-m", "practice", "quiz", "--bank", "backend", "--count", "20",
                         "--exam", "--minutes", "30", "--seed", "18"]
    if mode == "case":
        return prefix + ["-m", "practice.readiness", "start", "--case", case_id]
    raise ValueError("Unknown study mode: " + mode)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline study setup; no pip, API key or model download.")
    parser.add_argument("--mode", choices=["check", "learn", "timed", "case"], default="check")
    parser.add_argument("--case", choices=["RC01", "RC02", "RC03"], default="RC02")
    args = parser.parse_args(argv)
    try:
        python = prepare_environment(ROOT)
        doctor = subprocess.run([str(python), "-m", "practice", "doctor"], cwd=str(ROOT), check=False)
        if doctor.returncode != 0:
            return doctor.returncode
        return subprocess.run(command_for(args.mode, python, args.case), cwd=str(ROOT), check=False).returncode
    except (OSError, RuntimeError, ValueError) as error:
        print("Study setup error: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
