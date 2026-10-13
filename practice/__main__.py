import argparse
import json
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
    if bank not in BANK_PATHS:
        raise ValueError("Unknown quiz bank")
    document = load_quiz(BANK_PATHS[bank])
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
    started = time.monotonic()
    try:
        for index, question in enumerate(questions, 1):
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
            responses.append({"id": question["id"], "category": question["category"], "selected": int(selection) - 1, "correct": correct})
            if not args.exam:
                print("정답" if correct else "오답 (정답 %d)" % (question["answer"] + 1))
                print(question["explanation"])
    except (EOFError, KeyboardInterrupt):
        print("\n연습을 종료합니다.")
    moment = datetime.now(KST)
    score = sum(item["correct"] for item in responses)
    wrong_by_category = Counter(item["category"] for item in responses if not item["correct"])
    result = {"kind": "original_practice_not_official", "bank": bank, "priority_filter": priority, "time_kst": moment.isoformat(),
              "elapsed_seconds": round(time.monotonic() - started, 1), "planned_questions": len(questions),
              "answered": len(responses), "correct": score, "seed": args.seed,
              "wrong_by_category": dict(wrong_by_category), "responses": responses}
    output = ROOT / "reports" / ("quiz-" + moment.strftime("%Y%m%d-%H%M%S-%f") + ".json")
    save_json(output, result)
    print("\n결과 %d/%d, 기록: %s" % (score, len(responses), output))
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
    save_json(ROOT / "reports" / "environment.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
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
    quiz_parser.add_argument("--bank", choices=["basic", "advanced"], default="basic")
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
