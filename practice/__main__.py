import argparse
import json
import math
import platform
import random
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .core import ROOT, analyze, load_quiz, validate_answer, write_dataset

KST = timezone(timedelta(hours=9))
BANK_PATHS = {"basic": ROOT / "practice" / "quiz.json", "advanced": ROOT / "practice" / "advanced-quiz.json"}
SELECTION_PATH = ROOT / "practice" / "backend-core-selection.json"


def load_bank(bank):
    if bank in BANK_PATHS:
        return load_quiz(BANK_PATHS[bank])
    if bank != "backend":
        raise ValueError("Unknown quiz bank")
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8-sig"))
    available = {name: {item["id"]: item for item in load_quiz(path)["questions"]} for name, path in BANK_PATHS.items()}
    questions, seen = [], set()
    for item in selection["selection"]:
        if item["bank"] not in available or item["id"] not in available[item["bank"]] or item["id"] in seen:
            raise ValueError("Invalid backend quiz selection")
        questions.append(available[item["bank"]][item["id"]])
        seen.add(item["id"])
    return {"disclaimer": selection["disclaimer"], "questions": questions}


def save_json(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def quiz(args):
    bank = getattr(args, "bank", "basic")
    old = None
    if args.review:
        old = json.loads(Path(args.review).read_text(encoding="utf-8-sig"))
        bank = old.get("bank", bank)
    document = load_bank(bank)
    print(document["disclaimer"])
    questions = document["questions"]
    priority = getattr(args, "priority", None)
    if priority:
        questions = [item for item in questions if item.get("priority") == priority]
    if args.category:
        questions = [item for item in questions if item["category"] == args.category]
    if args.review:
        wrong = {row["id"] for row in old["responses"] if not row["correct"]}
        questions = [item for item in questions if item["id"] in wrong]
    random.Random(args.seed).shuffle(questions)
    if args.count < 1:
        raise ValueError("--count must be at least 1")
    questions = questions[:args.count]
    if not questions:
        print("선택한 조건에 해당하는 문제가 없습니다.")
        return 0
    responses = []
    minutes = getattr(args, "minutes", None)
    if minutes is not None and (not math.isfinite(minutes) or minutes <= 0):
        raise ValueError("--minutes must be a positive finite number")
    if minutes is not None:
        print("자체 연습 예산 %.1f분. 타이머는 입력을 강제 종료하지 않으며 실제 시험 설정이 아닙니다." % minutes)
    started = time.monotonic()
    try:
        for index, question in enumerate(questions, 1):
            question_started = time.monotonic()
            if minutes is not None:
                print("남은 자체 연습 예산 %.1f분" % max(0, minutes - (question_started - started) / 60))
            print("\n[%d/%d] %s %s\n%s" % (index, len(questions), question["id"], question["category"], question["question"]))
            for option_index, option in enumerate(question["options"], 1):
                print("  %d. %s" % (option_index, option))
            while True:
                selection = input("답 1~4 (q 종료): ").strip()
                if selection.lower() == "q":
                    raise EOFError
                if selection in ["1", "2", "3", "4"]:
                    break
                print("1~4 중에서 입력하세요.")
            correct = int(selection) - 1 == question["answer"]
            responses.append({"id": question["id"], "category": question["category"], "selected": int(selection) - 1, "correct": correct,
                              "question_seconds": round(time.monotonic() - question_started, 1)})
            if not args.exam:
                print("정답" if correct else "오답 (정답 %d)" % (question["answer"] + 1))
                print(question["explanation"])
    except (EOFError, KeyboardInterrupt):
        print("\n연습을 종료합니다.")
    moment = datetime.now(KST)
    score = sum(item["correct"] for item in responses)
    completed = len(responses) == len(questions)
    elapsed = round(time.monotonic() - started, 1)
    wrong_by_category = Counter(item["category"] for item in responses if not item["correct"])
    result = {"kind": "original_practice_not_official", "bank": bank, "priority_filter": priority, "time_kst": moment.isoformat(),
              "status": "completed" if completed else "partial",
              "elapsed_seconds": elapsed, "planned_questions": len(questions),
              "answered": len(responses), "correct": score, "seed": args.seed,
              "wrong_by_category": dict(wrong_by_category), "responses": responses}
    if minutes is not None:
        result.update({"practice_budget_minutes": minutes, "within_practice_budget": elapsed <= minutes * 60,
                       "completed_within_practice_budget": completed and elapsed <= minutes * 60,
                       "timer_mode": "advisory_no_forced_input_cutoff"})
    output = ROOT / "reports" / ("quiz-" + moment.strftime("%Y%m%d-%H%M%S-%f") + ".json")
    save_json(output, result)
    print("\n%s 응답 %d/%d, 정답 %d/%d, 기록: %s" % ("완료" if completed else "미완료", len(responses), len(questions), score, len(responses), output))
    if minutes is not None:
        print("소요 %.1f분 / 자체 예산 %.1f분. %s" % (elapsed / 60, minutes, "예산 내 종료" if result["within_practice_budget"] else "예산 초과"))
    if args.exam:
        by_id = {item["id"]: item for item in questions}
        for response in responses:
            question = by_id[response["id"]]
            print("%s 정답 %d: %s" % (question["id"], question["answer"] + 1, question["explanation"]))
    return 0


def doctor(args):
    document = load_quiz()
    dataset = ROOT / "data" / "synthetic" / "lots.csv"
    result = {"python": platform.python_version(), "executable": sys.executable,
              "minimum_python": "3.11", "supported_python": sys.version_info >= (3, 11),
              "virtual_environment": sys.prefix != sys.base_prefix,
              "external_python_packages_required": False,
              "quiz_questions": len(document["questions"]),
              "categories": sorted({item["category"] for item in document["questions"]}),
              "synthetic_dataset_present": dataset.is_file(),
              "tools": {name: shutil.which(name) for name in ["python", "node", "git", "uv"]}}
    if dataset.is_file():
        stats = analyze(dataset)
        result["lab_validated"] = True
        result["synthetic_raw_rows"] = stats["raw_rows"]
    case_path = ROOT / "practice" / "readiness-cases.json"
    if case_path.is_file():
        cases = json.loads(case_path.read_text(encoding="utf-8-sig"))
        result["readiness_cases"] = [case["id"] for case in cases["cases"]]
        result["readiness_assessment"] = "self_assessment_only"
    result["learner_exam_readiness"] = "not_established_by_environment_check"
    advanced_path = ROOT / "practice" / "advanced-quiz.json"
    if advanced_path.is_file():
        result["advanced_quiz_questions"] = len(load_quiz(advanced_path)["questions"])
    if SELECTION_PATH.is_file():
        result["backend_selected_questions"] = len(load_bank("backend")["questions"])
    save_json(ROOT / "reports" / "environment.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["supported_python"]:
        print("학습 환경에는 지원 중인 Python 3.11 이상이 필요합니다. .venv-study 실행 파일을 사용하세요.", file=sys.stderr)
        return 2
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="SK하이닉스 해커톤 대비용 비공식 오프라인 연습")
    sub = parser.add_subparsers(dest="command", required=True)
    quiz_parser = sub.add_parser("quiz", help="AI 개념 자가 점검")
    quiz_parser.add_argument("--count", type=int, default=10)
    quiz_parser.add_argument("--seed", type=int, default=17)
    quiz_parser.add_argument("--category")
    quiz_parser.add_argument("--bank", choices=["basic", "advanced", "backend"], default="basic")
    quiz_parser.add_argument("--minutes", type=float, help="자체 연습 예산과 문항별 시간 기록; 입력 강제 종료 없음")
    quiz_parser.add_argument("--priority", choices=["first_round_core", "extension"])
    quiz_parser.add_argument("--review", help="이전 quiz 기록 JSON의 오답만 연습")
    quiz_parser.add_argument("--exam", action="store_true", help="연습 종료 후 정답 공개")
    quiz_parser.set_defaults(handler=quiz)
    doctor_parser = sub.add_parser("doctor", help="환경과 연습자료 점검")
    doctor_parser.set_defaults(handler=doctor)
    generate_parser = sub.add_parser("generate", help="결정론적 합성 CSV 재생성")
    generate_parser.add_argument("--force", action="store_true")
    lab_parser = sub.add_parser("lab", help="합성 CSV 품질 및 Python SQL 교차검증")
    lab_parser.add_argument("--csv", type=Path, default=ROOT / "data" / "synthetic" / "lots.csv")
    lab_parser.add_argument("--out", type=Path, default=ROOT / "reports" / "lab-result.json")
    answer_parser = sub.add_parser("check-answer", help="답변 JSON 구조 및 근거 필드 점검")
    answer_parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if hasattr(args, "handler"):
            return args.handler(args)
        if args.command == "generate":
            path = ROOT / "data" / "synthetic" / "lots.csv"
            if path.exists() and not args.force:
                raise ValueError("CSV exists; use --force to replace the synthetic exercise only")
            write_dataset(path)
            print(str(path))
            return 0
        if args.command == "lab":
            result = analyze(args.csv)
            save_json(args.out, result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "check-answer":
            document = json.loads(args.path.read_text(encoding="utf-8-sig"))
            if not isinstance(document, dict):
                raise ValueError("Answer JSON must be an object")
            errors = validate_answer(document)
            print("\n".join(errors) if errors else "구조 확인 통과. 내용의 정확성은 출처와 수치로 따로 검증하세요.")
            return 1 if errors else 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print("오류: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
