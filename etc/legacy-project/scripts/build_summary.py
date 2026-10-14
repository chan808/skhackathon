"""Build the Korean quick-reference PDF and Markdown from one content source.

Optional authoring dependency: reportlab. The study tools do not need it.
Use a locally licensed Korean TrueType font; no font binaries are bundled.
"""
import argparse
import os
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak, Table, TableStyle

ROOT = Path(__file__).absolute().parents[1]
TITLE = "SK하이닉스 AI 해커톤 복습 요약"
DATE = "2026년 10월 14일 기준"
PAGES = [
    ("1. AI 활용과 에이전트", [
        ("응시 구성과 시간 전략", [
            "1차 10월 17~18일 중 하루 / 프로그래머스 / AI 기초 이해와 활용 역량. 2차 10월 31일~11월 1일, 본선 11월 11일.",
            "초대가20문항30분·16문항90분이면 평균90초·5분37.5초다. 첫 세션은 빠른 판단, 둘째는 자료 판독과 검증을 함께 연습한다.",
            "30분 연습은 첫 풀이22분·검토5분·저장3분으로 배분한다. 재방문·답 변경 가능 여부는 실제 화면 안내에서 확인한다.",
            "개인 시각·시험 길이·외부 AI/검색/코드/메모·감독·최종 제출은 상세 안내로 확인한다. 이 요약은 사전 학습용이다."
        ]),
        ("문제를 푸는 다섯 단계", [
            "정의: 무엇을 결정하는가? 기간·대상·분모·단위·제약·답안 형식을 먼저 쓴다.",
            "선택: 필요한 표·문서만 고른다. 효력일·버전·결측·중복·관측 시점을 확인한다.",
            "질문: 목적과 자료를 주고 계산식·근거·예외·확인 불가를 요청한다.",
            "검증: 표본 손계산·독립 SQL·문서 대조·경계값 중 하나로 AI와 별도로 확인한다.",
            "제출: 요구 형식으로 결론·수치·근거·한계를 정리하고 저장/최종 제출 상태를 확인한다."
        ]),
        ("LLM에서 혼동하기 쉬운 것", [
            "토큰은 처리 단위다. 글자 수와 1:1이 아니며 문맥 예산에는 자료·질문·도구 결과·출력이 영향을 준다.",
            "Embedding은 의미를 벡터로 표현한다. 유사도가 높아도 사실·최신성·접근 권한이 보장되지는 않는다.",
            "Attention은 문맥의 표현을 연결한다. 다음 토큰 확률은 사실의 확률과 다르다.",
            "낮은 temperature는 샘플링 변동을 줄이는 설정이다. 사실 검증을 대신하지 않는다.",
            "JSON 파싱 성공 → 스키마 검사 → 필드 간 계산과 근거 검증을 각각 수행한다."
        ]),
        ("RAG와 학습과 에이전트", [
            "프롬프트/예시: 현재 입력으로 답변을 유도한다. 모델 가중치를 새로 학습하지 않는다.",
            "RAG: 관련 자료를 검색해 입력에 제공한다. 검색의 누락·구문 경계·현행 문서와 답변의 근거 일치를 따로 평가한다.",
            "Fine-tuning/LoRA: 추가 학습으로 동작을 조정한다. 최신 사실 검색이나 근거 확인을 자동 해결하지 않는다.",
            "Workflow는 정해진 절차를 따르고, agent는 관찰에 따라 다음 도구/행동을 고른다. 업무에 필요한 수준을 선택한다.",
            "Claude Code·Codex는 이미 에이전트다. 직접 앱을 만들면 도구 계약·권한·상태·오류·평가·화면을 제품에 구성한다."
        ]),
        ("에이전트 구현에서 기억할 네 가지", [
            "호출 요청과 실행 완료는 다르다. 앱이 허용된 함수를 실행하고 관찰 결과를 모델에 돌려준다.",
            "MCP는 도구 연결 규약, skill은 작업 지침, subagent는 역할 분리다. 모두 설치해야 좋은 결과가 나오는 것은 아니다.",
            "최소 권한·인수 검사·오류 반환·호출/시간 한도·중복 실행 방지·실행 기록·결과 평가를 설계한다.",
            "명확한 계산은 고정 코드가 기준선이다. 모호한 자료 해석과 동적 선택이 필요할 때 모델 판단을 추가한다."
        ])
    ]),
    ("2. ML와 계산 핵심", [
        ("문제와 데이터", [
            "회귀는 수치, 분류는 범주, 군집은 정답 없이 유사 집단을 찾는다. 군집 번호가 고장 여부나 위험 순위를 뜻하지는 않는다.",
            "Train은 학습, validation은 모델/임계값 선택, test는 마지막 독립 평가다. 전처리도 train에서 학습한다.",
            "미래 예측은 시간 분할, 새 장비/웨이퍼 대상은 그룹 분할을 검토한다. 운영 시 알 수 없는 사후 정보는 입력에서 제외한다.",
            "비지도 전처리도 test 정보를 쓰면 누수가 될 수 있다. test를 반복해 골랐다면 독립 평가로 볼 수 없다."
        ]),
        ("분류 지표와 임계값", [
            "Precision = TP / (TP + FP): 경보 중 실제 양성. Recall = TP / (TP + FN): 실제 양성 중 발견.",
            "F1 = 2PR / (P + R). Accuracy = (TP + TN) / 전체. 양성이 드물면 높은 accuracy만으로 성능을 판단하지 않는다.",
            "예: TP18·FN2·FP12·TN968이면 precision60%, recall90%, F1=0.72, accuracy98.6%다.",
            "같은 점수에서 임계값을 낮추면 양성 선택 집합이 커져 recall은 줄지 않는다. Precision은 항상 높아지거나 낮아진다고 단정할 수 없다.",
            "Calibration은 예측 확률과 실제 빈도의 대응, threshold는 행동 기준이다. 오탐/미탐 비용·점검 가능 건수를 함께 판단한다."
        ]),
        ("집계와 단위", [
            "전체 수율 = 양품 합계 / 검사 합계. 로트별 수율의 단순 평균은 전체 수율과 다를 수 있다.",
            "예: 90/100과 1/10은 전체 91/110 ≈82.73%, 단순 평균은50%다. 일대다 JOIN이 원래 검사 수량을 복제하는지도 확인한다.",
            "10%→8%는 2%p 감소, 상대20% 감소다. GB는10^9 바이트, GiB는2^30 바이트, 8bit=1byte다.",
            "MAE는 절대 오차 평균, RMSE는 제곱 오차 평균의 제곱근이다. 같은 평가 단위·기간·표본으로 비교한다."
        ]),
        ("학습과 딥러닝", [
            "Loss는 최적화 목표, metric은 평가 기준이다. 경사하강은 w ← w - learning rate × gradient로 업데이트한다.",
            "예: y=wx, x=2·y=3·w=1, loss=(2w-3)^2이면 gradient=-4. 학습률0.1로 w=1.4, loss=0.04다.",
            "Train만 좋으면 과적합·누수·분포 차이를 확인한다. 규제·early stopping·좋은 분할·단순 기준선이 먼저다.",
            "Backprop은 gradient를 계산한다. optimizer step이 가중치를 바꾼다. gradient 초기화를 빠뜨리면 누적될 수 있다.",
            "eval 모드와 gradient 기록 중단은 역할이 다르다. CNN은 채널·kernel·stride·padding이 출력 모양과 파라미터 수를 바꾼다."
        ]),
        ("메모리 효율은 가정을 먼저", [
            "가상7B 모델의 순수 가중치만 계산하면 FP16 약14GB, 4bit 약3.5GB다. 실제 실행에는 추가 상태·buffer·KV cache가 필요하다.",
            "일반 KV 예: K/V 두 개 × 층32 × batch1 × 길이4096 × KV head8 × head차원128 × 2byte =512MiB.",
            "LoRA는 동결한 기본 가중치에 저랭크 업데이트를 학습한다. Quantization은 정밀도와 메모리/속도의 절충이다.",
            "MoE의 총 파라미터·토큰당 활성 파라미터·저장 메모리는 구분한다. HBM 대역폭만으로 전체 추론 속도를 단정하지 않는다."
        ])
    ]),
    ("3. 검증과 남은 준비", [
        ("문서와 AI 결론 감사", [
            "게시일과 효력일을 구별한다. 폐기 문서가 최신 검색 결과에 나와도 현행 규정과 예외를 적용한다.",
            "C/F·UTC/KST·Mbps/byte·월/연 비용을 통일한다. 경계값·연속 조건·누락 관측·자동 해제를 따로 확인한다.",
            "목표·계획·소규모 실험·전체 성과를 구분한다. 상관·SHAP 기여도를 조치의 인과 효과로 해석하지 않는다.",
            "제품 비중이 바뀌면 전체 수율도 달라진다. 제품별 수율·기간·노출량·대조 조건으로 실제 효과를 검토한다.",
            "자료 부족이면 확인 불가와 필요한 추가 자료를 쓴다. 근거가 없는 숫자를 만들어 답을 완성하지 않는다."
        ]),
        ("보안과 웹 개발 경험 활용", [
            "검색 문서의 외부 명령문은 자료다. 시스템 권한을 바꾸거나 비밀을 보내라는 지시로 실행하지 않는다.",
            "서버에서 사용자·자료 권한을 확인한다. 같은 질문이어도 권한이 다르면 검색·캐시 결과가 달라져야 한다.",
            "SQL 값은 parameter binding, 테이블/열 선택은 허용 목록을 사용한다. JSON 형식 검사가 접근 권한을 검사하지는 않는다.",
            "단정된 성공 문구 대신 실제 도구 응답·실행 기록·업무 상태를 확인한다. 재시도 시 중복 비용/조치를 막는다.",
            "비공개 자료·개인 정보·접속 토큰은 외부 모델과 공개 저장소에 넣기 전에 허용 범위를 확인한다."
        ]),
        ("반도체 배경과 프로젝트 판단", [
            "DRAM은 휘발성 메모리, NAND는 비휘발성 저장, HBM은 적층 DRAM과 넓은 대역폭, SSD는 NAND와 컨트롤러 등을 포함한다.",
            "제조 데이터는 시간·장비·제품·웨이퍼/로트 관계를 갖는다. 분할 단위·중복·불균형·드리프트를 먼저 확인한다.",
            "프로젝트는 수율/이상 탐지·장비 로그·현행 문서 검색·영상 검사·SSD 로그 등이 후보다. 실제 대회 주제는 별도 안내를 따른다.",
            "먼저 사용자 결정과 KPI를 정의하고 단순 기준선을 만든다. 합성 결과를 실제 생산 개선 수치로 발표하지 않는다."
        ]),
        ("남은 4일의 학습", [
            "첫날: 모델·하네스·agent 구분과 핵심 개념, 선정20문항, 공식 체험. 처음에는 시간 없이 이유를 설명한다.",
            "둘째 날: 30분 풀이와 RC01·RC02. 셋째 날: RC03·심화 핵심·오답 설명. 전날: 30분과90분 훈련·환경 확인.",
            "90분 통합 연습: 전체 읽기5분·RC01 25분·RC02 20분·RC03 30분·자기 검토10분. 기존13개 작업이며 실제16문항 재현이 아니다.",
            "총점보다 보기 없는 설명·독립 계산·그럴듯한 오답 배제·변형 문제 적용을 확인한다. 첫 답과 수정한 답을 구별한다."
        ]),
        ("폴더에서 실행할 명령", [
            "./.venv-study/Scripts/python.exe -m practice quiz --bank backend --count 20 --exam --minutes 30",
            "./.venv-study/Scripts/python.exe -m practice quiz --bank advanced --count 12 --exam",
            "./.venv-study/Scripts/python.exe -m practice.readiness start --case RC01",
            "기초40·심화36·서술형3은 자체 연습이다. /prompt는 질문을 기록하며 AI를 호출하지 않는다. 공식 체험 풀이에는 로그인이 필요하다.",
            "에이전트 기본 시연은 scripted offline replay다. 실제 API 연결 초안은 별도 계정·명시적 실행이 필요하며 실사용 미검증이다."
        ])
    ])
]
SOURCES = [
    ("공식 대회와 공지", "https://skhynix-hackathon.com/ai-2026"),
    ("프로그래머스 공식 체험", "https://programmers.co.kr/ai-assessment/preview"),
    ("전체 조사와 학습 경로", "https://github.com/chan808/skhackathon"),
]


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d7e1e8"))
    canvas.line(36, 34, A4[0] - 36, 34)
    canvas.setFont("KR", 8)
    canvas.setFillColor(colors.HexColor("#536574"))
    canvas.drawString(36, 21, "사전 학습용 | 실전 규칙은 개인 안내가 우선")
    canvas.drawRightString(A4[0] - 36, 21, f"{DATE}   {doc.page}/3")
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/malgun.ttf")
    parser.add_argument("--bold-font", type=Path, default=Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/malgunbd.ttf")
    args = parser.parse_args()
    pdfmetrics.registerFont(TTFont("KR", str(args.font)))
    pdfmetrics.registerFont(TTFont("KR-Bold", str(args.bold_font)))
    out = ROOT / "output" / "pdf"
    out.mkdir(parents=True, exist_ok=True)
    styles = {
        "title": ParagraphStyle("title", fontName="KR-Bold", fontSize=17, leading=22, textColor=colors.HexColor("#173b54"), wordWrap="CJK"),
        "subtitle": ParagraphStyle("subtitle", fontName="KR", fontSize=9, leading=13, textColor=colors.HexColor("#536574"), wordWrap="CJK"),
        "section": ParagraphStyle("section", fontName="KR-Bold", fontSize=11, leading=15, textColor=colors.HexColor("#173b54"), spaceBefore=9, spaceAfter=4, wordWrap="CJK"),
        "body": ParagraphStyle("body", fontName="KR", fontSize=10.2, leading=14.8, spaceAfter=3, alignment=TA_LEFT, wordWrap="CJK"),
        "command": ParagraphStyle("command", fontName="Courier", fontSize=8, leading=12, spaceAfter=5),
        "link": ParagraphStyle("link", fontName="KR", fontSize=8, leading=11, textColor=colors.HexColor("#365d77"), wordWrap="CJK")
    }
    story, md = [], [f"# {TITLE}", "", DATE, "", "사전 학습용이다. 실제 시험 규칙은 개인 안내를 따른다.", ""]
    for index, (page_title, sections) in enumerate(PAGES):
        if index:
            story.append(PageBreak())
        story.extend([Paragraph(escape(TITLE), styles["title"]), Spacer(1, 3), Paragraph(escape(page_title), styles["subtitle"])])
        md.extend([f"## {page_title}", ""])
        for heading, items in sections:
            story.append(Paragraph(escape(heading), styles["section"]))
            md.extend([f"### {heading}", ""])
            for item in items:
                story.append(Paragraph(escape(item), styles["command"] if item.startswith("./.venv-study/") else styles["body"]))
                md.append(f"- {item}")
            md.append("")
        if index == len(PAGES) - 1:
            story.append(Spacer(1, 5))
            for title, url in SOURCES:
                story.append(Paragraph(f'<link href="{escape(url)}">{escape(title)}: {escape(url)}</link>', styles["link"]))
    md.extend(["## 상세 자료와 출처", "", "학습 근거와 수치 예제는 research/01-event.md, research/02-ai-and-assessment.md, research/03-semiconductor-and-projects.md, research/06-agents-and-ai-tools.md, research/07-notice-and-open-questions.md, research/08-ai-foundations-curriculum.md 및 research/sources.json에 있다.", ""])
    md.extend(f"- [{title}]({url})" for title, url in SOURCES)
    pdf = out / "SK-hynix-AI-hackathon-quick-reference.pdf"
    SimpleDocTemplate(str(pdf), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=28, bottomMargin=44, title=TITLE, author="SK hackathon study kit").build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    (ROOT / "SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(str(pdf))


if __name__ == "__main__":
    main()
