"""Original case practice: records work, then offers explicit self-assessment."""
import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
KST = timezone(timedelta(hours=9))


def load_cases():
    document = json.loads((ROOT / "practice" / "readiness-cases.json").read_text(encoding="utf-8-sig"))
    if document.get("assessment_mode") != "self_assessment":
        raise ValueError("Case pack must be marked self_assessment")
    ids = set()
    for case in document["cases"]:
        if case["id"] in ids:
            raise ValueError("Duplicate case ID")
        ids.add(case["id"])
        rubric = case["scoring_rubric"]
        if sum(item["points"] for item in rubric["criteria"]) != rubric["max_points"]:
            raise ValueError("Scoring rubric total mismatch")
    return document


def save(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def start(args):
    pack = load_cases()
    case = next((item for item in pack["cases"] if item["id"] == args.case), None)
    if case is None:
        raise ValueError("Unknown case ID")
    minutes = args.minutes if args.minutes is not None else case["recommended_minutes"]
    if minutes <= 0:
        raise ValueError("Minutes must be positive")
    print(pack["disclaimer"])
    visible = {key: case[key] for key in ["id", "title", "context", "data", "documents", "tasks"]}
    print(json.dumps(visible, ensure_ascii=False, indent=2))
    print("\n연습 시간 %d분. 실제 시험 제한 시간이 아닙니다." % minutes)
    print("답을 여러 줄로 입력하세요. /done 저장, /prompt 질문 초안 기록, /quit 중단.")
    print("/prompt는 질문을 기록할 뿐 AI를 호출하지 않습니다. 실제 사용한 답변은 풀이에 근거와 함께 적으세요.")
    began = datetime.now(KST)
    timer = time.monotonic()
    lines, prompts = [], []
    status = "draft"
    try:
        while True:
            line = input("> ")
            if line.strip() == "/done":
                status = "completed"
                break
            if line.strip() == "/quit":
                break
            if line.strip() == "/prompt":
                if len(prompts) >= case["max_ai_requests"]:
                    print("이 창작 연습의 질문 기록 한도에 도달했습니다.")
                    continue
                question = input("질문 초안: ").strip()
                if question:
                    prompts.append({"text": question, "elapsed_seconds": round(time.monotonic() - timer, 1), "kind": "recorded_prompt_not_api_call"})
                continue
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        print("\n중간 기록을 저장합니다.")
    elapsed = round(time.monotonic() - timer, 1)
    result = {"kind": "original_readiness_practice", "assessment_mode": "self_assessment",
              "case_id": case["id"], "started_kst": began.isoformat(), "status": status,
              "elapsed_seconds": elapsed, "practice_budget_minutes": minutes,
              "within_practice_budget": elapsed <= minutes * 60,
              "prompts": prompts, "answer": "\n".join(lines), "assessment": None,
              "limits": "Unscored learner work; does not establish official exam readiness or a passing score."}
    path = ROOT / "reports" / ("readiness-" + case["id"] + "-" + began.strftime("%Y%m%d-%H%M%S-%f") + ".json")
    save(path, result)
    print("\n저장: " + str(path))
    print("소요 %.1f분. 답안의 정확성은 아직 평가하지 않았습니다." % (elapsed / 60))
    return 0


def read_integer(prompt, maximum):
    while True:
        value = input(prompt).strip()
        if value.isdecimal() and 0 <= int(value) <= maximum:
            return int(value)
        print("0~%d의 정수를 입력하세요." % maximum)


def review(args):
    result = json.loads(args.path.read_text(encoding="utf-8-sig"))
    if result.get("kind") != "original_readiness_practice":
        raise ValueError("Not a readiness practice record")
    case = next((item for item in load_cases()["cases"] if item["id"] == result["case_id"]), None)
    if case is None:
        raise ValueError("Unknown case in record")
    print("상태 %s | 소요 %.1f분 / 연습 예산 %s분 | 질문 초안 %d개" %
          (result.get("status", "unknown"), result.get("elapsed_seconds", 0) / 60,
           result.get("practice_budget_minutes", "unknown"), len(result.get("prompts", []))))
    print("본인 풀이\n" + result["answer"])
    print("\n창작 과제의 기준 풀이\n" + json.dumps(case["answer_key"], ensure_ascii=False, indent=2))
    print("\n아래 점수는 본인이 근거와 비교하여 적는 자가 평가입니다. 자동 채점이 아닙니다.")
    scores, critical = [], []
    try:
        for criterion in case["scoring_rubric"]["criteria"]:
            value = read_integer("%s (0~%d): " % (criterion["criterion"], criterion["points"]), criterion["points"])
            scores.append({"id": criterion["id"], "awarded": value, "maximum": criterion["points"]})
        for error in case["critical_errors"]:
            value = read_integer("중대한 오류를 저질렀나요? %s (아니오0, 예1): " % error, 1)
            if value:
                critical.append(error)
    except (EOFError, KeyboardInterrupt):
        print("\n자가 평가를 저장하지 않았습니다. 원래 풀이 기록은 유지됩니다.")
        return 0
    result["assessment"] = {"kind": "self_reported", "reviewed_kst": datetime.now(KST).isoformat(),
                            "total": sum(item["awarded"] for item in scores), "maximum": case["scoring_rubric"]["max_points"],
                            "criteria": scores, "critical_errors_reported": critical,
                            "exam_readiness": "not_established"}
    save(args.path, result)
    print("자가 평가 %d/%d. 공식 합격 가능성을 판정하는 점수가 아닙니다." % (result["assessment"]["total"], result["assessment"]["maximum"]))
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="비공식 자료 해석과 AI 활용 준비도 연습")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    start_parser = sub.add_parser("start")
    start_parser.add_argument("--case", required=True)
    start_parser.add_argument("--minutes", type=int)
    review_parser = sub.add_parser("review")
    review_parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "list":
            for case in load_cases()["cases"]:
                print("%s | %s | 권장%d분" % (case["id"], case["title"], case["recommended_minutes"]))
            return 0
        return start(args) if args.command == "start" else review(args)
    except (OSError, ValueError, KeyError) as error:
        print("오류: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
