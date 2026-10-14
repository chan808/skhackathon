"""Export current public study files, without Git, credentials or environments.

Known public directories are exported; private records and installers stay separate.
The repo skill is also placed in its discoverable path inside the ZIP.
"""
import hashlib
import json
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
OUTPUT = ROOT / "output/laptop-kit"
ROOT_FILES = (
    ".gitignore", ".gitattributes", "AGENTS.md", "README.md", "START-HERE.md",
    "REPORT.md", "SUMMARY.md", "MINIMUM-KNOWLEDGE.md", "LEARNING-PATH.md",
    "PREPARATION-CHECK.md", "LAPTOP-PREPARATION.md", "TRAVEL-RUNBOOK.md",
)
PUBLIC_DIRECTORIES = ("practice", "examples", "research", "scripts", "tests", "templates", "data/synthetic", "output/pdf")
PUBLIC_REPORTS = (
    "agent-example.json", "agent-loop-offline.json", "lab-result.json", "local-status.md",
    "minimum-knowledge-check.json", "verification.json", "verification-2026-10-13.json",
)
EXTENSIONS = {".md", ".py", ".ps1", ".json", ".csv", ".sql", ".pdf", ".txt"}
SKILL_SOURCE = "templates/project-skills/hackathon-preflight/SKILL.md"
SKILL_INSTALLED = ".agents/skills/hackathon-preflight/SKILL.md"
REQUIRED = ("README.md", "TRAVEL-RUNBOOK.md", "scripts/study.py", "scripts/verify.py", "practice/quiz.json",
            "output/pdf/SK-hynix-minimum-AI-knowledge.pdf", SKILL_INSTALLED)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def select_public_files(root):
    root = root.resolve()
    candidates = [root / name for name in ROOT_FILES]
    candidates.extend(root / "reports" / name for name in PUBLIC_REPORTS)
    for name in PUBLIC_DIRECTORIES:
        directory = root / name
        if directory.is_dir():
            candidates.extend(directory.rglob("*"))
    selected = {}
    for path in candidates:
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS and relative not in ROOT_FILES:
            continue
        if any(part.startswith(".") or part in {"__pycache__", "private", "installers"}
               for part in path.relative_to(root).parts) and relative not in {".gitignore", ".gitattributes"}:
            continue
        # Reject junction/symlink escapes rather than following private files outside the root.
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Refusing linked public file: " + relative)
        selected[relative] = path
    skill = root / SKILL_SOURCE
    if SKILL_SOURCE in selected:
        selected[SKILL_INSTALLED] = skill
    for required in REQUIRED:
        if required not in selected:
            raise ValueError("Required public file missing: " + required)
    return dict(sorted(selected.items()))


def build_bundle(root=ROOT, output=OUTPUT):
    selected = select_public_files(root)
    output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d-%H%M%S-%f")
    archive = output / ("skhackathon-travel-" + stamp + ".zip")
    members = []
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, path in selected.items():
            # Hash exactly the bytes written, even if a file is edited during export.
            content = path.read_bytes()
            bundle.writestr("skhackathon/" + name, content)
            members.append({"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("Archive checksum failure")
        for item in members:
            if hashlib.sha256(bundle.read("skhackathon/" + item["path"])).hexdigest() != item["sha256"]:
                raise ValueError("Archive content mismatch")
    manifest = {
        "created_at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "archive": archive.name, "sha256": sha256(archive), "bytes": archive.stat().st_size,
        "file_count": len(members), "scope": "Current public directory snapshot, not a Git commit archive",
        "private_files_included": False, "installers_included": False,
        "members": members,
    }
    (output / "travel-bundle.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / (archive.name + ".sha256")).write_text(manifest["sha256"] + "  " + archive.name + "\n", encoding="ascii")
    (output / "TRAVEL-START-HERE.txt").write_text(
        "SK하이닉스 출국용 파일 — Windows x64\n\n"
        "이 폴더를 USB 등 별도 저장장치에도 보관하세요.\n"
        "1. travel-bundle.json의 archive ZIP을 새 위치에 풉니다.\n"
        "2. 설치된 Python 3.11 이상이 없다면 installers의 Python 전체 EXE로 설치합니다.\n"
        "   새 PowerShell을 열고 py -3 --version으로 실제 설치를 확인합니다.\n"
        "3. 압축을 푼 skhackathon 폴더에서 py -3 scripts/study.py --mode check를 실행합니다.\n"
        "   기존 .venv-study는 복사하지 않습니다. pip 패키지는 필요 없습니다.\n"
        "4. PDF와 TRAVEL-RUNBOOK.md는 인터넷 없이 읽을 수 있습니다.\n"
        "5. Codex에서는 프로젝트를 열고 $hackathon-preflight로 사전 점검합니다.\n"
        "   스킬과 자료 보관은 오프라인, 모델·시험·VPN 서비스는 온라인입니다.\n\n"
        "설치 파일의 보관은 설치·로그인·VPN 한국 서버 연결 완료를 뜻하지 않습니다.\n"
        "Proton VPN 후보의 한국 서버 선택에는 유료 계정과 시험 운영자의 허용 확인이 필요합니다.\n"
        "개인 일정·초대·운영자 답변은 원본 data/private를 별도 비공개 백업하세요. 공개 ZIP에는 없습니다.\n\n"
        "ZIP 확인: Get-FileHash -Algorithm SHA256 -LiteralPath 'ZIP 파일 경로'\n"
        "결과를 travel-bundle.json 또는 해당 .sha256 파일과 비교하세요.\n"
        "설치 파일 SHA256은 installers/manifest.json에 기록합니다.\n",
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    result = build_bundle()
    print(json.dumps({key: value for key, value in result.items() if key != "members"}, ensure_ascii=False, indent=2))
