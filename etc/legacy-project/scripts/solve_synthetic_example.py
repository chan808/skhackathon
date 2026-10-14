"""A narrow deterministic calculation tool, not an LLM agent implementation."""
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    data = json.loads((ROOT / "practice" / "evidence-cards.json").read_text(encoding="utf-8"))
    documents = {item["id"]: item for item in data["documents"]}
    # The current conversation selected these two documents after reading them.
    # Selection here is fixed and does not claim autonomous model inference.
    rule = documents["SOP-CURRENT"]
    log = documents["LOG-K1"]
    threshold = Decimal(re.search(r"섭씨 (\d+)도 초과", rule["text"]).group(1))
    required = int(re.search(r"(\d+)회 연속", rule["text"]).group(1))
    readings = re.findall(r"(섭씨|화씨) (\d+(?:\.\d+)?)도", log["text"])
    normalized = []
    for unit, text in readings:
        value = Decimal(text)
        normalized.append(value if unit == "섭씨" else (value - 32) * Decimal(5) / Decimal(9))
    best, streak = 0, 0
    for value in normalized:
        streak = streak + 1 if value > threshold else 0
        best = max(best, streak)
    result = {"kind": "synthetic_agent_task", "inspection_candidate": best >= required,
              "temperatures_c": [float(value) for value in normalized],
              "source_ids": [rule["id"], log["id"]], "consecutive_above_threshold": best,
              "automatic_shutdown": False, "root_cause_confirmed": False,
              "rejected_instruction_sources": ["NOTE-UNTRUSTED"],
              "explanation": "현행 규정의 75도 초과 3회 연속 조건을 충족한다. 점검 후보로 기록하되 사람이 검토해야 하며 고장 원인은 확인되지 않았다.",
              "provenance": {"task_context": "Codex conversation preparation demonstration",
                             "calculation_tool": "scripts/solve_synthetic_example.py",
                             "policy": "Fixed synthetic calculation, not a standalone LLM agent",
                             "source_selection": "SOP-CURRENT is current; SOP-OLD is superseded; external memo is untrusted"}}
    path = ROOT / "reports" / "agent-example.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
