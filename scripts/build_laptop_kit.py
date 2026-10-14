"""Make an offline study ZIP from committed public files, never the workspace."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).absolute().parents[1]
OUTPUT = ROOT / "output" / "laptop-kit"
EXCLUDED = (".venv/", ".venv-study/", ".cache/", ".codex-remote-attachments/", "tmp/", "data/private/", "output/laptop-kit/")
PRIVATE_REPORTS = {"reports/environment.json", "reports/windows-preflight.json", "reports/participant-status.json", "reports/agent-loop-live.json"}


def validate_members(names):
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise ValueError("Unsafe archive path")
        if not name.startswith("skhackathon/"):
            raise ValueError("Unexpected archive root")
        relative = name.removeprefix("skhackathon/")
        if (relative.startswith(EXCLUDED) or relative in PRIVATE_REPORTS
                or relative.startswith(("reports/quiz-", "reports/answer-", "reports/readiness-"))
                or path.name == ".env" or path.name.startswith(".env.") and path.name != ".env.example"):
            raise ValueError("Private file is tracked; fix the index before exporting")


def main():
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    changes = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    if changes:
        raise SystemExit("Commit public changes first. The kit exports HEAD, not uncommitted files.")
    committed_names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=ROOT, text=True).splitlines()
    validate_members(["skhackathon/" + name for name in committed_names])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    archive = OUTPUT / ("skhackathon-study-" + revision[:7] + ".zip")
    subprocess.run(["git", "archive", "--format=zip", "--prefix=skhackathon/", "--output=" + str(archive), "HEAD"], cwd=ROOT, check=True)
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        validate_members(names)
        if bundle.testzip() is not None:
            raise ValueError("Archive checksum failure")
        for required in ["README.md", "LAPTOP-PREPARATION.md", "scripts/study.py", "MINIMUM-KNOWLEDGE.md", "output/pdf/SK-hynix-minimum-AI-knowledge.pdf"]:
            if "skhackathon/" + required not in names:
                raise ValueError("Required study file is absent")
    manifest = {"commit": revision, "archive": archive.name, "bytes": archive.stat().st_size,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "file_count": sum(not name.endswith("/") for name in names),
                "privacy_path_check_passed": True,
                "scope": "Committed public study files only; no environments, installers, private invites or credentials."}
    (OUTPUT / "study-bundle.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
