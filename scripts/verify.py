"""Record executed tests and local-document checks for this preparation kit."""
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT))

from practice.core import analyze, load_quiz
from examples.agent_loop import OfflineReplay, run
from practice.__main__ import load_bank


def main():
    completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                               cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    output = completed.stdout + completed.stderr
    markdown_files = [ROOT / "README.md", ROOT / "REPORT.md", ROOT / "START-HERE.md", ROOT / "LEARNING-PATH.md", ROOT / "SUMMARY.md"]
    for directory in ["research", "practice", "templates", "data/synthetic", "examples", "reports"]:
        markdown_files.extend((ROOT / directory).rglob("*.md"))
    missing = []
    local_links = 0
    for path in markdown_files:
        text = path.read_text(encoding="utf-8-sig")
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = link.split("#", 1)[0].strip("<>")
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            local_links += 1
            destination = (path.parent / target).absolute()
            # This invocation creates its own verification artifact after checks.
            is_this_report = destination == (ROOT / "reports" / "verification.json")
            if not destination.exists() and not is_this_report:
                missing.append({"file": str(path.relative_to(ROOT)), "target": target})
    quiz = load_quiz(ROOT / "practice" / "quiz.json")
    advanced = load_quiz(ROOT / "practice" / "advanced-quiz.json")
    backend = load_bank("backend")
    sources = json.loads((ROOT / "research" / "sources.json").read_text(encoding="utf-8"))
    recorded_lab = json.loads((ROOT / "reports" / "lab-result.json").read_text(encoding="utf-8"))
    lab = analyze(ROOT / "data" / "synthetic" / "lots.csv")
    lab_matches_record = lab == recorded_lab
    cases = json.loads((ROOT / "practice" / "readiness-cases.json").read_text(encoding="utf-8"))
    known_urls = {source["url"] for source in sources["sources"]}
    unregistered_quiz_sources = sorted({url for question in quiz["questions"] + advanced["questions"] for url in question["source_urls"]} - known_urls)
    loop = run(OfflineReplay())
    expected_tools = ["read_materials", "normalize_temperatures", "evaluate_streak"]
    offline_ok = (loop["mode"] == "offline_scripted_replay_no_llm" and loop["status"] == "contract_passed"
                  and [step["tool"] for step in loop["trace"]] == expected_tools
                  and all(step["success"] for step in loop["trace"]))
    example_check = subprocess.run([sys.executable, "-m", "practice.agent_check", "reports/agent-example.json"], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    result = {
        "checked_at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "test_returncode": completed.returncode,
        "test_count": len(re.findall(r"^test_.* \.\.\. ok$", output, re.MULTILINE)),
        "test_output": output,
        "markdown_files_checked": len(markdown_files), "local_links_checked": local_links,
        "missing_local_links": missing,
        "quiz_questions": len(quiz["questions"]),
        "advanced_quiz_questions": len(advanced["questions"]),
        "backend_selected_questions": len(backend["questions"]),
        "advanced_priorities": dict(Counter(question["priority"] for question in advanced["questions"])),
        "unregistered_quiz_source_urls": unregistered_quiz_sources,
        "readiness_cases": len(cases["cases"]),
        "readiness_assessment_mode": cases["assessment_mode"],
        "learner_readiness": "not_assessed",
        "agent_example_contract_passed": example_check.returncode == 0,
        "agent_loop_offline_tools_and_contract_passed": offline_ok,
        "agent_loop_live_api_tested": False,
        "lab_matches_saved_reference": lab_matches_record,
        "quiz_categories": dict(Counter(question["category"] for question in quiz["questions"])),
        "unique_source_urls": sources["unique_url_count"],
        "source_count_note": sources["count_note"],
        "lab": {key: lab[key] for key in ["raw_rows", "clean_rows", "rejected", "weighted_yield", "sqlite_weighted_yield"]},
        "limits": ["Quiz and missions are original study exercises, not official exam questions.",
                   "Answer structure validation does not establish factual truth.",
                   "Official notice was read in an existing session; preview exercises and the real exam were not entered.",
                   "Default agent example is scripted offline replay, not LLM inference; live API path was not run.",
                   "Browser inventory does not establish camera, microphone, display, RAM or network readiness.",
                   "Local links were checked; external source access status is recorded in source registers."]
    }
    result["passed"] = (completed.returncode == 0 and not missing and not unregistered_quiz_sources
                        and result["quiz_questions"] == 40 and result["advanced_quiz_questions"] == 36
                        and result["backend_selected_questions"] == 20
                        and result["advanced_priorities"] == {"first_round_core": 28, "extension": 8}
                        and result["readiness_cases"] == 3 and example_check.returncode == 0 and offline_ok and lab_matches_record)
    (ROOT / "reports" / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["passed", "test_count", "markdown_files_checked", "local_links_checked", "missing_local_links", "quiz_questions", "advanced_quiz_questions", "unregistered_quiz_source_urls", "unique_source_urls"]}, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
