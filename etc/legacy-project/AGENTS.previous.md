# 이 저장소에서 작업할 때

SK하이닉스 AI 해커톤 예선의 사전 학습·환경 준비 저장소다. 학습 실행은 Python 3.11 이상과 표준 라이브러리만 필요하다.

- 환경·출국 준비에는 `TRAVEL-RUNBOOK.md`와 `templates/project-skills/hackathon-preflight/SKILL.md`를 읽는다. 설치된 스킬은 `.agents/skills/hackathon-preflight/SKILL.md`에 있다.
- Windows 실행은 `.\.venv-study\Scripts\python.exe scripts\verify.py`, 새 PC는 `py -3 scripts\study.py --mode check`다. `python`이 WindowsApps 별칭이면 실제 런타임인지 확인한다.
- 코드 변경 후 `scripts/verify.py`를 실행한다. 일반 검증은 로컬 보고서에 기록하고 공개 검증 기록을 덮어쓰지 않는다.
- 개인 응시 일정·초대·운영사 답변·기기 점검은 `data/private/` 또는 Git에서 제외한 보고서에 기록한다. 공개 준비 문서와 개인 완료 증거를 구분한다.
- 시험 허용 도구·VPN·해외 접속은 개인 안내가 우선이다. 공개 체험이나 설치 완료를 실전 사용 허가로 해석하지 않는다.
- 1차 준비에 새 웹앱·Docker·CUDA·로컬 모델을 추가하려면 실제 과제와 필요성을 먼저 확인한다. 가상환경은 기기 간 복사하지 않는다.
- 출국용 작업 사본은 `scripts/build_travel_kit.py`로 만든다. 개인 파일·로그인 정보·VPN 계정은 공개 ZIP에 넣지 않는다.
