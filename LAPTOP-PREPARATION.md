# 노트북과 해외 응시 준비

2026년 10월 14일 확인. 목표는 **실제 응시 노트북에서 로그인·파일·연습·통신을 미리 검증하는 것**이다. 설치 수가 준비 정도를 뜻하지 않는다. 오늘 준비와 일본 도착 후 점검을 나눠 진행한다. 이 문서는 일반 준비 안내이며, 참가자별 시험 조건은 초대와 운영사 답변을 우선한다.

## 오늘 할 일: 약 90분

| 순서 | 할 일 | 완료 기준 |
| --- | --- | --- |
| 1 · 10분 | OS·CPU 종류 확인, 업데이트와 재부팅, 충전기 준비 | 개인 기기에서 설치·재부팅 가능; 회사 기기는 관리 정책 확인 |
| 2 · 15분 | 최신 Chrome 설치, 메일·프로그래머스 로그인 | 실제 응시 계정으로 로그인, 초대 메일과 문의 연락처 접근 가능 |
| 3 · 15분 | ChatGPT 앱과 웹 로그인, 작은 합성 파일로 연습 | CSV 읽기·검산·한국어 입력·다시 로그인 방법 확인 |
| 4 · 15분 | Python 설치, 저장소 clone 또는 ZIP 풀기 | `study.py --mode check` 통과, PDF가 오프라인에서 열림 |
| 5 · 15~30분 | 공식 체험, 제공된 시험 사전 테스트 | 실제 노트북에서 답안 입력·저장·권한·제출 방법 직접 확인 |
| 6 · 10분 | VPN 조건 확인, 예비 회선과 개인 자료 보관 | 운영자 답변 기록, 승인된 연결 경로와 장애 복구 순서 확보 |

시간 배분은 준비 제안이며 공식 시험 절차가 아니다. 실제 시험 시작 버튼과 사전 테스트·공개 체험을 구분한다.

## 설치·다운로드 판단

| 항목 | 판단 | 이유와 공식 경로 |
| --- | --- | --- |
| 최신 Chrome | 우선 | 공식 응시 지원 브라우저. [설치 도움말](https://support.google.com/chrome/answer/95346), [전체 MSI](https://chromeenterprise.google/download/) |
| Python 3.11 이상 | 우선 | 이 저장소 연습은 표준 라이브러리만 필요. [공식 다운로드](https://www.python.org/downloads/); 보관용 Windows x64는 [3.13.16 전체 EXE](https://www.python.org/downloads/release/python-31316/) |
| Git | clone할 때 | [Git for Windows](https://gitforwindows.org/). ZIP을 풀어 쓸 때는 없어도 됨 |
| ChatGPT 앱 | 오늘 설치·로그인 권장 | 학습과 합성 자료 연습용. [공식 Windows 안내](https://learn.chatgpt.com/docs/app/windows), [macOS 등 안내](https://learn.chatgpt.com/docs/app) |
| ChatGPT 웹 | 함께 로그인 | 앱 설치·실행 문제에 대비하는 별도 진입점. AI 서비스는 온라인 연결이 필요 |
| Claude 앱/Code | 이미 익숙하면 선택 | 둘째 도구는 계정과 파일 입력까지 시험한 경우만 준비. 이번 예선에 필수라는 근거 없음 |
| VPN 데스크톱 앱 1개 | 조건 확인 후 | 운영자 지정 제품·한국 IP 조건을 우선. 무료 플랜에 한국 서버가 있다고 가정하지 않음 |
| Monito+ 등 감독 앱 | 초대에서 요구할 때 | [공식 안내](https://user-guide.grepp.co/en/articles/Monitio-42b3563a). 다른 시험의 감독 도구를 임의로 설치하지 않음 |
| Docker·WSL·VM·CUDA·로컬 LLM·에이전트 프레임워크 | 이번 준비에서는 미룸 | 현재 연습에 필요 없음. 감독 앱 사용 시험은 VM 등과 충돌할 수 있음 |

공식 최소사양 표는 Windows 10 이상 또는 macOS 12 이상, 쿼드코어·RAM 8GB, 최신 Chrome/Edge/Whale, 1280×720 및 100% 배율을 제시한다. 같은 페이지의 도입 문구와 OS 표에 차이가 있으므로 **개인 초대의 조건으로 최종 판단**한다. [프로그래머스 최소사양](https://user-guide.grepp.co/en/articles/Minimum-Requirements-b0a9cc7a)

저장소의 Windows x64 설치 파일을 Mac이나 Windows ARM64에 그대로 설치하지 않는다. CPU 종류를 먼저 확인한다. 이미 지원 Python이 정상 설치됐다면 재설치하지 않아도 된다. 현재 도구 검증은 Python 3.12.14에서 수행했으며 새 노트북에서는 다시 실행한다.

## Windows: 설치 후 저장소 실행

노트북의 PowerShell에서 실행한다. 아래는 **선택한 프로그램을 실제 설치하는 명령**이다. `winget`이 없으면 위 공식 페이지나 보관한 설치 파일로 설치한다. 설치가 끝나면 새 PowerShell 창을 연다.

```powershell
winget install --id Google.Chrome --exact --source winget
winget install --id Python.Python.3.13 --exact --source winget
winget install --id Git.Git --exact --source winget
winget install --id 9PLM9XGG6VKS --source msstore
```

ChatGPT의 Microsoft Store ID는 [OpenAI 공식 Windows 문서](https://learn.chatgpt.com/docs/app/windows)에 따른다. Store 설치와 로그인은 출국 전에 끝낸다. Python install manager나 앱 설치용 작은 다운로드 도구만 보관한 것을 전체 런타임의 오프라인 설치 준비와 혼동하지 않는다.

보관한 Python EXE로 설치한다면 일반 설치와 런처/PATH 옵션을 사용하고 설치 후 새 터미널에서 버전을 확인한다. free-threaded 실험 옵션이나 PDF 재생성 패키지는 필요하지 않다. Chrome 전체 MSI도 같은 Chrome의 배포 파일이며 관리 서비스 가입이 필수는 아니다. [Google 설명](https://chromeenterprise.google/download/)

```powershell
git clone https://github.com/chan808/skhackathon.git
cd skhackathon
py -3 scripts/study.py --mode check
py -3 scripts/study.py --mode learn
```

`py`가 없지만 Python이 PATH에 등록됐다면 `python scripts/study.py --mode check`로 실행한다. 설치한 Python이 여러 버전이면 `py -3.13 scripts/study.py --mode check`처럼 지원 버전을 지정한다. 이 Python 진입점은 PowerShell 실행 정책을 바꾸지 않아도 된다.

현재 저장소를 노트북에도 그대로 clone한다. `check` 결과와 학습 기록은 Git에서 제외된 로컬 파일로 저장하며, 공개 문서·코드·PDF는 함께 버전관리한다. 설치 파일·개인 초대·앱 로그인·VPN 설정은 clone에 포함되지 않으므로 별도로 준비한다. 일반 점검 보고서는 `reports/local-verification.json`이다.

## Mac: 설치 후 저장소 실행

[공식 Python 다운로드](https://www.python.org/downloads/macos/)에서 지원 버전을 설치한다. Git이 준비됐다면 다음을 실행하고, 그렇지 않으면 GitHub의 Download ZIP이나 이동용 ZIP을 먼저 사용한다. `git` 명령이 별도 개발 도구 설치를 요청하면 ZIP 사용이 더 간단하다.

```bash
git clone https://github.com/chan808/skhackathon.git
cd skhackathon
python3 scripts/study.py --mode check
python3 scripts/study.py --mode learn
```

ChatGPT 공식 앱 페이지는 Apple Silicon용 다운로드를 제공한다. 기기·계정에서 설치가 지원되지 않으면 브라우저를 사용하고 실제 응시 플랫폼의 Mac 지원은 초대로 확인한다. [공식 앱 안내](https://learn.chatgpt.com/docs/app)

## ChatGPT 앱 세팅의 완료 기준

앱과 브라우저 모두 기존 본인 계정으로 로그인한다. 인증 수단을 일본에서도 사용할 수 있는지 확인하고, 로그인 파일·쿠키·API 키를 Git으로 옮기지 않는다. 새 기기의 로그인·관리자 설치 확인은 본인이 수행한다.

앱에서 이 저장소 폴더를 열거나 학습용 프로젝트를 만들고 `MINIMUM-KNOWLEDGE.md`와 합성 `data/synthetic/lots.csv`를 사용한다. 질문 예시는 다음과 같다.

> 이 합성 CSV를 보고 유효 데이터의 가중 수율을 계산해줘. 제외한 행과 이유, 분자·분모, 계산 과정과 불확실성을 제시해줘. 결론을 검산할 Python 코드도 줘.

응답 수치와 실행 코드를 `practice lab`의 계산으로 비교하고, 작은 파일 업로드·다운로드·한국어 입력·복사·붙여넣기를 직접 수행한다. 일반 Chat은 질문·자료 분석에, 로컬 Codex 작업은 파일 처리·코드 실행을 배우는 데 사용한다. 학습에는 하나의 익숙한 흐름이면 충분하다. 긴 에이전트 작업이 필요하다는 근거는 없다.

이어 [프로그래머스 체험 상세 분석](research/11-programmers-preview-analysis.md)을 따라 내장 Assist의 문제 선택·파일 전달·답안 입력을 직접 연습한다. 앱에서 합성 파일을 처리한 경험과 시험 인터페이스 조작 경험을 모두 확보한다.

여러 줄 입력이 잦으면 설정에서 Ctrl+Enter(Windows)/Cmd+Enter(Mac) 전송을 선택할 수 있다. [공식 앱 설정](https://learn.chatgpt.com/docs/app/settings)

**앱 설치와 사전 연습이 실전 외부 AI 사용 허가를 뜻하지 않는다.** 시험에서 제공하는 AI와 외부 앱·검색·로컬 코드 허용은 따로 확인한다. 실제 시험 자료의 외부 업로드도 허용 범위 안에서만 수행한다.

## 일본에서 사용할 네트워크와 VPN

일본 JST와 한국 KST는 모두 UTC+9이므로 시차가 없다. 개인 초대의 시각과 날짜를 현지에서도 그대로 확인한다. 초대 시간·링크·VPN 관련 문의 답변은 공개 문서 대신 `data/private/`에 보관한다.

운영자가 VPN이 필요할 수 있다고 답했다면 다음을 확정한다. 이 항목은 아직 공개 규정으로 확인되지 않았다.

1. 일본 직접 접속이 가능한가, 한국 IP가 필수인가?
2. VPN 사용이 허용되는가? 지정 제품·서버·고정 IP가 필요한가?
3. 감독 앱을 쓰는 경우 VPN 클라이언트도 허용되는가?
4. 시험 중 회선·서버 변경과 재접속이 허용되는가? 답안은 어떻게 복구하는가?
5. 사전 테스트 완료 기한과 일본에서 재확인할 수 있는 절차는 무엇인가?

[공식 시험 규정](https://user-guide.grepp.co/en/articles/Test-Regulations-74bb73c8)은 기업별 상세 조건을 운영자에게 확인하도록 안내한다. 일반 가이드에서 해외 VPN 허용 또는 한국 IP 의무를 확정하지 못했다.

VPN 제품은 운영자 요구에 맞춘다. 한국 IP가 필요하면 실제로 **한국 서버를 선택할 수 있는 요금제**인지 확인한다. 예를 들어 Proton 무료 플랜의 서버 선택 정책만으로 한국 IP를 준비할 수 없다. 브라우저 확장은 다른 앱의 트래픽까지 처리하는 전체 기기 VPN과 다르다. [무료 플랜 정책](https://protonvpn.com/support/change-server-free-plan), [확장 범위](https://protonvpn.com/support/browser-extensions)

숙소에서는 **Wi-Fi 로그인 포털 → 일반 인터넷 → 필요한 VPN 연결 → 공식 사전 테스트** 순서로 확인한다. VPN 또는 Kill Switch가 로그인 포털을 막거나 연결 단절 시 인터넷을 차단할 수 있다. 동작을 직접 확인하고 운영자가 승인한 복구 절차를 기록한다. [호텔 로그인 포털](https://support.nordvpn.com/hc/en-us/articles/48557553837969-How-to-log-in-to-a-captive-portal-Wi-Fi-network-while-using-NordVPN), [Kill Switch](https://protonvpn.com/support/advanced-kill-switch)

가능하면 숙소의 안정된 유선 연결을 먼저 시험하고, 휴대폰 테더링은 예비 회선으로 준비한다. 로밍/eSIM의 테더링 허용과 사용량, 실제 응시 지역 연결을 확인한다. VPN을 켠 상태의 실제 품질도 확인한다. 일반 가이드는 업로드 최소 1Mbps·권장 5Mbps를 제시한다. [최소사양](https://user-guide.grepp.co/en/articles/Minimum-Requirements-b0a9cc7a)

## 일본 도착 후와 시험 당일

**도착 후:** 실제 숙소·노트북·회선·VPN 조합으로 로그인과 사전 테스트를 다시 확인한다. 같은 환경에서 하는 사전 테스트가 권장되며, 필수 시험은 지정 기한 내 완료해야 한다. [사전 테스트](https://user-guide.grepp.co/en/articles/What-is-a-Demo-Test-ac3f5c17)

**전날:** 브라우저·OS 업데이트와 재부팅을 마무리하고, 시험 시간에 재시작하지 않도록 해당 OS의 업데이트 시간 설정을 확인한다. 충전·절전·카메라·마이크·화면 공유·휴대폰·신분증은 초대 요구에 맞춘다. 감독 도구가 요구되면 실제 동작과 허용 프로그램을 확인한다. [준비물](https://user-guide.grepp.co/en/articles/What-to-Prepare-63beea5b)

**당일:** 입장 마감은 초대대로 지킨다. 개인 준비 기준으로 첫 세션 약 45~60분 전에 회선·전원·메일을 확인한다. 안정성 확인을 마친 VPN 서버와 회선을 유지하고 불필요한 백그라운드 다운로드를 종료한다. 새로운 도구 설치·설정 변경은 시험 직전에 시작하지 않는다.

**연결 장애:** 운영자 절차에 따라 재접속한다. VPN을 끄거나 IP를 바꿔도 되는지는 한국 IP 조건에 따라 다르므로 사전 답변을 따른다. 복구 후 답안의 저장·누락 상태를 확인한다. 통신 불안정으로 저장되지 않을 수 있다는 공식 안내가 있다. [연결 장애 안내](https://user-guide.grepp.co/en/articles/Lost-Connection-During-Test-4b8ac401)

Monito+ 사용 시험에서는 제한 프로그램·다중 모니터·중복 시험 접속이 문제가 될 수 있고 VM 계열과 충돌할 수 있다. 이번 시험의 적용 여부를 먼저 확인한다. [Monito+](https://user-guide.grepp.co/en/articles/Monitio-42b3563a), [VM 충돌 안내](https://user-guide.grepp.co/en/articles/Test-Interrupted-in-Monito-baf22989)

## 오프라인 이동과 완료 판정

Git clone 외에 `scripts/build_laptop_kit.py`로 **커밋된 공개 파일만 포함하는 ZIP**을 만들 수 있다. 출력은 `output/laptop-kit/`이며 Git에서 제외한다. ZIP에는 PDF·문제·합성 데이터·실행 코드가 있고 가상환경·개인 기록·로그인 정보·설치 파일은 없다. 별도 `installers/` 파일은 OS와 CPU가 일치할 때만 옮겨 설치한다. 현재 PC의 `.venv-study`는 복사하지 않고 노트북에서 새로 만든다.

인터넷 없이 PDF와 로컬 연습을 사용할 수 있다. 외부 원문 링크·ChatGPT·검색·VPN 서비스·실제 시험은 온라인 서비스이므로 ZIP에 내려받을 수 없다. 개인 초대 링크와 운영자 답변은 별도 비공개 경로로 옮긴다.

완료 증거는 [개인 노트북 체크리스트](templates/laptop-checklist.md)를 `data/private/`에 복사해 기록한다. **도구 테스트 통과 + 본인 공식 체험 + 실제 일본 연결 확인 + 운영자 조건 확인**을 모두 확보한 뒤 응시 세팅이 끝났다고 판단한다.
