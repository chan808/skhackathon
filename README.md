# SK하이닉스 AI 해커톤 조사와 준비

2026년 10월 14일 KST 재점검 반영. 서류 합격 후 AI 학습과 체험을 시작하는 백엔드 개발자를 위한 조사와 로컬 연습 환경이다. 공부할 첫 문서는 **[최소 AI 지식](MINIMUM-KNOWLEDGE.md)**이다. 한 번에 한 블록을 3~5분 읽고, 확인 질문에 답한다. 전체 조사 파일을 먼저 읽을 필요는 없다. 읽은 뒤 [학습 순서](LEARNING-PATH.md)를 따라 짧은 연습을 시작한다.

[프로젝트 준비 점검](PREPARATION-CHECK.md)은 실제로 검증한 항목과 남은 응시 조건을 구분한다. 도구 테스트 통과를 본인의 응시 준비 완료로 해석하지 않는다.

초대가 **20문항·30분과 16문항·90분** 구성이라면 [두 세션의 학습 전략](research/09-first-round-time-strategy.md)과 [백엔드 경험을 AI에 연결하는 노트](research/10-backend-ai-bridge.md)를 먼저 읽는다. 세션 명칭과 외부 도구 허용은 문항 수만으로 확정하지 않는다.

전체 조사 결과는 [REPORT.md](REPORT.md)에서 시작한다. 상세 응시 메일은 공지상 10월 13일 발송 예정이었다. [메일 검색·미확정 조건·재발송 문의 초안](research/07-notice-and-open-questions.md)을 확인한다. 풀이 인터페이스는 [프로그래머스 공식 공개 체험](https://programmers.co.kr/ai-assessment/preview)에서 경험한다. 체험 풀이에는 개인회원 로그인이 필요하며 실전의 감독·시간·허용 도구는 개인 안내를 따른다.

틈틈이 복습할 때는 [3쪽 요약 PDF](output/pdf/SK-hynix-AI-hackathon-quick-reference.pdf) 또는 [요약 원문](SUMMARY.md)을 읽는다.

처음 배우는 용어의 설명과 확인 질문을 읽으려면 [최소지식 PDF](output/pdf/SK-hynix-minimum-AI-knowledge.pdf)를 사용한다. 3쪽 요약은 개념을 익힌 뒤 빠르게 복습할 때 쓴다.

## 바로 실행

PowerShell에서 이 폴더를 연다. 아래 명령은 가상환경을 활성화하지 않아도 실행된다. 추가 패키지 설치, API 키, 유료 서비스가 필요하지 않다.

진입 명령을 줄인 실행 스크립트도 있다. `learn`은 해설을 보며 풀기, `timed`는 30분 예산 기록, `case`는 RC02 자료 검증이다. 기존 환경을 점검하고 없으면 설치된 지원 버전의 Python으로 새 환경을 만든다. Python을 내려받거나 모델 계정을 연결하지 않는다.

```powershell
.\scripts\study.ps1 -Mode learn
.\scripts\study.ps1 -Mode timed
.\scripts\study.ps1 -Mode case
.\scripts\study.ps1 -Mode check
```

```powershell
.\.venv-study\Scripts\python.exe -m practice doctor
.\.venv-study\Scripts\python.exe -m practice quiz --count 10
```

백엔드 개발자에게 먼저 필요한 20문항을 조합한 연습은 다음과 같다. `--minutes`는 예산과 문항별 시간을 기록하며 입력을 강제 종료하지 않는다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --bank backend --count 20 --exam --minutes 30 --seed 18
```

전체 40문항을 끝난 뒤 채점하려면 다음을 사용한다. 자가 점검용 창작 문제이며 실제 출제 범위나 기출문제가 아니다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --count 40 --exam --seed 17
```

오답 기록은 `reports/quiz-시각.json`으로 자동 저장된다. 생성된 파일 경로를 그대로 넣어 오답만 다시 풀 수 있다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --review 'reports\quiz-생성된파일명.json' --count 40
```

## 데이터와 문서 검증 연습

기초 풀이 후에는 그럴듯한 오답을 구분하는 **심화 36문항**을 사용한다. 핵심 28개와 확장 8개는 자체 학습 순서이며 실제 출제 범위를 뜻하지 않는다. [심화 학습 안내](practice/advanced-quiz-guide.md)에서 문항별 개념과 오답 보완 방법을 확인한다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --bank advanced --priority first_round_core --count 12 --exam
```

심화 기록을 `--review`에 넣으면 저장된 문제집을 자동 선택한다.

[합성 데이터 과제](data/synthetic/README.md)와 [AI 활용 미션](practice/missions.md)을 먼저 읽고 자신의 풀이를 작성한다. 기준 결과는 이미 `reports/lab-result.json`에 있으므로 첫 시도에서는 열지 않는다.

```powershell
.\.venv-study\Scripts\python.exe -m practice lab
.\.venv-study\Scripts\python.exe -m practice check-answer templates\answer.example.json
.\.venv-study\Scripts\python.exe -m unittest discover -s tests -v
```

`lab`은 오류가 있는 합성 CSV를 정제하고 전체·장비·제품·기간별 수율을 계산한다. Python과 SQLite 계산 결과를 교차 확인한다. `check-answer`는 답변 JSON의 형식과 근거 필드를 검사한다. 내용의 진실성을 자동 판정하지 않는다.

## 낯선 서술형 과제

예산·시간 최적화, 문서 효력·단위·예외, AI 결론 검토의 창작 과제 3개를 추가했다. 정답을 보기 전에 풀고 소요 시간과 질문 초안을 기록한다. 자유서술은 자동 채점하지 않고 기준 풀이와 비교해 자가 평가한다. [사용 안내](practice/readiness-guide.md)를 참고한다.

```powershell
.\.venv-study\Scripts\python.exe -m practice.readiness list
.\.venv-study\Scripts\python.exe -m practice.readiness start --case RC01
.\.venv-study\Scripts\python.exe -m practice.readiness review 'reports\readiness-생성된파일명.json'
```

`/prompt`는 질문을 기록하며 AI를 호출하지 않는다. `/done`으로 풀이를 저장한다. 시간과 질문 수는 자체 연습 조건이며 실제 대회의 제한을 뜻하지 않는다.

## 파일 안내

| 파일 | 용도 |
| --- | --- |
| REPORT.md | 조사 결론과 상세 자료 안내 |
| MINIMUM-KNOWLEDGE.md | 3~5분씩 읽는 여섯 블록과 확인 문답 |
| PREPARATION-CHECK.md | 학습 세팅 검증 결과와 남은 실전 확인 |
| output/pdf/SK-hynix-minimum-AI-knowledge.pdf | 별도 최소지식 책의 PDF |
| SUMMARY.md | 3쪽 복습 요약의 원문 |
| output/pdf/SK-hynix-AI-hackathon-quick-reference.pdf | 휴대·출력용 한글 복습 요약 |
| LEARNING-PATH.md | 미학습 상태에서 시작하는 첫 90분과 전체 주제 지도 |
| research/01-event.md | 공식 일정 FAQ 플랫폼 규정 채용 혜택 |
| research/02-ai-and-assessment.md | AI 개념 평가 방식 학습 주제 |
| research/03-semiconductor-and-projects.md | 반도체 배경 산업 적용 사례 데이터셋 |
| research/04-preparation-plan.md | 1차 전 일정과 2차 이후 준비 |
| research/05-first-round-readiness.md | 준비 자료와 실제 수행 능력 구분 |
| research/06-agents-and-ai-tools.md | 기존 에이전트 사용과 앱 개발 비교 |
| research/07-notice-and-open-questions.md | 합격 공지 재확인 메일 검색과 미확정 시험 조건 |
| research/08-ai-foundations-curriculum.md | ML 통계 최적화 DL LLM 기초와 수치 예제 |
| research/09-first-round-time-strategy.md | 30분 개념 판단과 90분 자료 검증 준비 |
| research/10-backend-ai-bridge.md | 하네스·workflow·agent·모델과 백엔드 경험 연결 |
| research/sources.json | 통합 출처 등록부 |
| practice/quiz.json | 해설과 출처가 있는 40문항 |
| practice/advanced-quiz.json | 심화 36문항과 핵심·확장 표시 |
| practice/backend-core-selection.json | 기존 76개에서 최우선20개를 조합하는 선택 목록 |
| practice/missions.md | 데이터 문서 코드 검증 미션 |
| practice/readiness-cases.json | 낯선 서술형 과제 3개와 기준 풀이 |
| templates/agent-task.md | 기존 에이전트로 수행하는 목표와 출력 계약 |
| examples/README.md | 선택적 에이전트 실행 구조 시연과 API 연결 초안 |
| templates/learning-progress.csv | 주제별 설명 계산 변형 적용 기록 |
| templates/exam-preflight.md | 본인 응시 안내 확인 |
| templates/problem-solving.md | 문제 정의 AI 질문 검증 기록 |
| templates/prompt-library.md | 연습용 질문 양식 |
| reports/local-status.md | 실행 환경·공개 제외 파일·미검증 범위 |
| reports/verification.json | 연습 도구 검증 결과 |

## 환경 재생성

새 `.venv-study`는 설치된 Codex 번들의 Python 3.12.14를 사용한다. 기존 `.venv`는 Python 3.9.13 환경으로 남아 있다. 연습 도구는 표준 라이브러리만 사용한다. 폴더를 옮기면 가상환경도 새로 만든다. 10월 13일의 환경과 준비 계획은 [기존 준비 계획](research/04-preparation-plan.md)에 남겨두고, 현재 실행 환경은 `reports/environment.json`을 기준으로 한다.

새 위치에서는 지원 중인 Python 실행 파일을 지정해 복원한다. 아래는 Python 3.12 런처가 등록된 PC의 예다. PowerShell 스크립트 실행 정책을 바꿀 필요가 없다.

```powershell
py -3.12 -m venv .venv-study --without-pip
.\.venv-study\Scripts\python.exe -m practice doctor
```

실제 대회 데이터·문제·답안의 외부 공개 범위와 시험 중 도구 사용 범위는 대회 약관과 개인 안내를 따른다. 이 폴더의 데이터와 문제는 사전 학습용으로 직접 만든 자료다.

개인 점수·진도는 템플릿을 `data/private/`에 복사해 기록한다. 가상환경·개인 실행 기록·PC 정보·참가 상태·API 키는 Git에서 제외한다. [공개 파일 범위](reports/local-status.md)를 참고한다.

## 새 PC에서 재현

저장소를 내려받고 그 폴더에서 Python 3.11 이상으로 환경을 만든다. 아래 첫 명령은 Python 3.12 런처가 등록된 Windows PC의 예다.

```powershell
git clone https://github.com/chan808/skhackathon.git
cd skhackathon
py -3.12 -m venv .venv-study --without-pip
.\.venv-study\Scripts\python.exe -m practice doctor
.\.venv-study\Scripts\python.exe scripts\verify.py
```

PDF 재생성만 선택적으로 `reportlab`과 한글 TrueType 글꼴이 필요하다. 이미 생성된 PDF를 보거나 퀴즈·실습·검증을 실행할 때는 추가 패키지가 필요 없다. `scripts/build_summary.py --font 경로 --bold-font 경로`로 글꼴을 지정할 수 있다.

최소지식 PDF 재생성은 `scripts/build_minimum_knowledge.py`가 같은 글꼴 옵션을 사용한다.

문서 저작 시에는 선택적으로 `pypdf`로 `scripts/check_minimum_knowledge.py`를 실행해 원문과 PDF의 버전·인용·수치를 기록한다. 최신 PDF를 렌더링해 직접 확인한 뒤에만 `--visual-reviewed`를 지정한다. 일반 학습 검증은 추가 패키지 없이 저장된 해시와 현재 파일을 비교하므로, 원문만 바꾸고 PDF를 갱신하지 않은 상태를 발견한다.
