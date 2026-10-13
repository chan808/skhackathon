# 연습 환경과 공개 파일 범위

2026년 10월 14일 기준. 학습 실행은 Python 3.11 이상과 표준 라이브러리만 필요하다. 최종 점검은 Python 3.12.14 별도 가상환경에서 수행했다. 기존 Python 3.9 환경은 보존했으며 현재 학습 명령은 `.venv-study`를 사용한다.

`python -m practice doctor`는 개인 PC의 실행 경로와 도구 정보를 `reports/environment.json`으로 기록한다. `scripts/windows-preflight.ps1`은 브라우저와 읽을 수 있는 시스템 정보만 기록한다. 이번 PC 점검에서는 Chrome·Edge 설치를 확인했고 메모리·해상도 조회는 실패했다. 카메라·마이크·화면 공유·네트워크 품질은 검사하지 않았다. 실제 시험 환경은 운영사의 상세 안내와 제공되는 사전 테스트로 확인한다.

다음 자료는 로컬에서 보존하고 Git에 올리지 않는다.

- `.venv/`, `.venv-study/`, `.cache/`, `tmp/`, Python 캐시
- `.env`와 API 키 파일
- `data/private/`의 개인 자료와 진도 기록
- `reports/environment.json`, `reports/windows-preflight.json`, `reports/participant-status.json`
- 개인 퀴즈·서술형·답안 기록과 `reports/agent-loop-live.json`

공개하는 데이터·퀴즈·서술형·에이전트 예시는 모두 자체 제작 합성 자료다. 공식 기출이나 실제 시험 답안이 아니다. `reports/lab-result.json`과 `reports/agent-example.json`은 기준 풀이이며, `reports/agent-loop-offline.json`은 실제 LLM 추론이 없는 재생 시연 기록이다. `reports/verification.json`은 도구·파일 검증 결과이며 개인 점수나 합격 가능성을 나타내지 않는다.

개인 학습 기록을 작성할 때는 `templates/study-log.csv`와 `templates/learning-progress.csv`를 `data/private/`로 복사해 사용한다. 공개 템플릿을 개인 점수로 덮어쓰지 않는다.
