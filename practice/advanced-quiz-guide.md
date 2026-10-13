# 심화 AI 개념 문제 학습 안내

심화 문제 36개는 용어를 아는지보다 비슷해 보이는 방법의 차이를 판단하는 연습이다. 기본 문제를 처음부터 풀어본 뒤, 이 문제에서 틀린 개념을 확인하고 실전형 사례로 연결한다. 모든 선택형 문제를 맞히더라도 실제 시험의 모든 과제를 대비했다는 뜻은 아니다. 공개되지 않은 출제 범위를 이 문제집으로 확정하지 않는다.

`advanced-quiz.json`의 각 문항은 문제, 선택지 네 개, 정답 인덱스, 풀이, 학습 근거를 담고 있다. 문제의 수치·가격·규정은 합성 예시이며 실제 회사 자료나 서비스 가격이 아니다. 출처는 기술 개념을 확인하는 원문이다. `first_round_core`는 먼저 공부할 항목, `extension`은 추가로 익힐 항목이라는 자체 표시다.

## 처음 시작하는 순서

1. 기본 문제에서 토큰·프롬프트·검색·지표·근거 확인을 먼저 익힌다.
2. 심화의 핵심 문항을 8~12개씩 풀고, 선택하기 전에 답의 이유를 한 줄 적는다.
3. 틀린 문제의 풀이를 읽은 뒤 왜 나머지 세 선택지가 틀렸는지도 설명한다.
4. 정답 문구를 외우지 말고 숫자·단위·조건을 하나 바꿔 다시 판단한다.
5. CSV 분석이나 문서 충돌 같은 실전형 사례에서 같은 원칙을 직접 사용한다.

처음부터 CNN 수식이나 optimizer 내부를 모두 암기할 필요는 없다. 핵심 문항의 계산·검증 원칙을 이해한 뒤 확장 항목으로 넘어간다. 확장이라는 표시는 대회에 나오지 않는다는 뜻도 아니다.

## 실행 명령

프로젝트 폴더의 PowerShell에서 실행한다. 아래 명령은 로컬 문제 파일을 사용하며 외부 모델 API를 호출하지 않는다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --bank advanced --priority first_round_core --count 12
```

풀이를 마지막에 공개하는 자체 시험 모드로 핵심 문항 전체를 풀려면 다음을 사용한다. 36은 선택 개수의 상한이며 핵심 문항은 그보다 적다. 명령에 실제 시험의 제한 시간이 설정되는 것은 아니다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --bank advanced --priority first_round_core --count 36 --exam
```

확장만 풀 때는 다음을 사용한다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --bank advanced --priority extension --count 36
```

한 영역만 풀 수 있다.

```powershell
.\.venv-study\Scripts\python.exe -m practice quiz --bank advanced --category "LLM·RAG·에이전트" --count 12
```

오답 기록을 다시 풀 때는 실행 결과가 알려준 실제 JSON 경로를 `--review`에 넣는다. 문제집을 바꿔도 같은 숫자 위치의 문제를 오답으로 잘못 해석하지 않도록 기록의 bank와 문항 ID를 함께 확인한다.

## 문항별로 설명할 수 있어야 하는 개념

| 문항 | 개념 | 자기 설명의 기준 |
| --- | --- | --- |
| AQ01 | 시간과 그룹 분할 | 내가 평가하려는 미래·처음 보는 객체가 무엇인지 설명 |
| AQ02 | 확률 보정 | 예측 0.8인 집단의 실제 양성 비율과 확률 추정 차이를 설명 |
| AQ03 | 불균형 학습과 평가 | 학습 resampling과 운영 분포 평가를 분리 |
| AQ04 | 임계값 | 고정 점수와 선택 집합의 변화로 TP·FP·recall을 설명 |
| AQ05 | 회귀 오차 | 절대 오차 평균과 제곱 오차 평균의 제곱근을 계산 |
| AQ06 | scaling | 거리의 단위·범위와 업무 중요도를 구분 |
| AQ07 | K-means | 군집 번호에 고장 의미나 위험 순위가 없는 이유를 설명 |
| AQ08 | PCA | 분산 보존률과 라벨 예측 성능을 구분 |
| AQ09 | 학습과 추론 | 평가 모드와 자동 미분 기록의 역할을 분리 |
| AQ10 | 역전파 | gradient 계산·누적·업데이트의 시점을 구분 |
| AQ11 | optimizer | Adam이 gradient 통계를 사용하는 방식의 역할을 설명 |
| AQ12 | CNN 크기 | 배치·채널·공간 축과 stride·padding을 계산 |
| AQ13 | workflow와 agent | 고정 순서와 동적 계획 필요성을 비교 |
| AQ14 | MCP 계약과 권한 | 입력 형식 검사가 자료 접근 권한 검사가 아닌 이유를 설명 |
| AQ15 | LoRA | 동결한 기본 가중치와 학습하는 저랭크 업데이트를 구분 |
| AQ16 | 양자화 | bit·byte와 순수 가중치·실행 메모리를 분리 |
| AQ17 | KV cache | 답변·문서 캐시와 attention 표현 재사용을 구분 |
| AQ18 | chunk와 의미 경계 | 원칙·예외·인접 문서가 검색 문맥에서 끊기는 문제를 설명 |
| AQ19 | 생성 충실성 | 검색 성공 뒤에도 답변 주장과 근거를 대조 |
| AQ20 | 현행 문서 검색 | 게시일과 효력일을 분리 |
| AQ21 | 임베딩 공간 | 같은 차원과 호환되는 의미 공간의 차이를 설명 |
| AQ22 | 문맥 예산 | 입력과 출력 합계라는 가정에서 남은 토큰을 계산 |
| AQ23 | 도구 오류 | 응답 수신·구조화 결과·업무 성공을 구분 |
| AQ24 | 평가 정답 노출 | 검색·프롬프트에도 누수가 생기는 이유를 설명 |
| AQ25 | JOIN 집계 | 일대다 복제와 가중 평균 오류를 원래 분모로 수정 |
| AQ26 | 비용과 경보 제약 | 미탐·오탐 비용과 점검 가능 건수를 함께 비교 |
| AQ27 | 토큰 비용 | 입력·출력 단가를 각각 계산해 합산 |
| AQ28 | 검색 precision과 recall | 필요한 전체 근거와 반환 결과라는 분모를 구분 |
| AQ29 | 시간대 | UTC 시각을 KST로 바꿔 효력 시점을 판단 |
| AQ30 | 전송 단위 | Mbps와 바이트 파일 크기를 같은 단위로 변환 |
| AQ31 | 자료의 주장 범위 | 목표·소규모 실험·전체 성과를 구분 |
| AQ32 | 병렬 의존 관계 | 독립 작업과 선행 조건을 나눠 완료 시간 계산 |
| AQ33 | 접근 통제와 캐시 | 같은 질문에도 사용자의 자료 권한이 다른 경우를 처리 |
| AQ34 | 구조와 계산 검증 | 스키마가 통과해도 필드 간 공식이 틀릴 수 있음을 확인 |
| AQ35 | SQL 식별자 | 값 바인딩과 허용된 테이블 선택을 구분 |
| AQ36 | 신뢰구간 | 우위 미확정과 동등성 증명을 구분 |

이 표는 정답 위치를 외우기 위한 요약이 아니다. 설명 기준을 읽고도 자신의 말로 적용할 수 없다면 해당 문제를 다시 푼다.

## 오답을 고치는 방법

오답을 네 종류로 나눠 보완한다.

| 오답 종류 | 바로 할 연습 |
| --- | --- |
| 용어 혼동 | calibration과 threshold, RAG와 LoRA처럼 혼동한 두 개념을 각 한 문장으로 정의하고 각각 필요한 업무를 적음 |
| 계산 오류 | 식·분모·단위를 쓴 뒤 숫자를 바꾼 두 번째 예시를 독립 계산 |
| 조건 누락 | 시간·그룹·권한·효력·운영 한계를 체크하고 어느 조건이 결론을 바꾸는지 표시 |
| 근거 확대 | 관측·기대·계획·인과·배포를 분리하고 자료가 실제로 허용하는 결론까지만 작성 |

모델에게 풀이를 물을 때는 이미 선택한 답과 이유를 먼저 제공한다. 예를 들어 “나는 precision과 recall의 분모를 이렇게 썼다. 어느 분모가 목표와 다른가”처럼 자신의 판단을 검토하게 한다. 정답 번호를 알려 달라는 요청만 반복하면 이해 여부가 남지 않는다.

## 원문에서 확인할 범위

scikit-learn 문서는 [분할](https://scikit-learn.org/stable/modules/cross_validation.html), [calibration](https://scikit-learn.org/stable/modules/calibration.html), [임계값](https://scikit-learn.org/stable/modules/classification_threshold.html), [평가 지표](https://scikit-learn.org/stable/modules/model_evaluation.html)의 정의와 예시를 확인하는 데 쓴다. 전체 API를 외울 필요는 없다.

PyTorch는 [학습과 평가 흐름](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html), [gradient 초기화](https://docs.pytorch.org/tutorials/recipes/recipes/zeroing_out_gradients.html), [Conv2d 출력 크기](https://docs.pytorch.org/docs/2.14/generated/torch.nn.modules.conv.Conv2d.html)를 참고한다. 코드 이름보다 무엇을 계산하고 언제 상태가 바뀌는지 이해한다.

LLM 쪽은 [LoRA](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora), [양자화](https://huggingface.co/docs/transformers/en/quantization/overview), [KV cache](https://huggingface.co/docs/transformers/en/cache_explanation), [workflow와 agent](https://www.anthropic.com/engineering/building-effective-agents), [MCP 도구 계약](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)을 골라 읽는다. 서로 다른 기능을 하나의 “AI 최적화”로 뭉뚱그리지 않는다.

문항별 출처와 확인 범위는 `research/advanced-quiz-sources.json`에 있다. 외부 원문이 없는 AQ27과 AQ31은 문제에 주어진 창작 값만으로 푸는 산술·근거 해석 문항이다.

## 선택형 점수와 실제 준비를 연결하기

선택형 점수는 이 문제집의 답을 구분한 기록이다. 실제 준비의 증거는 같은 원리를 CSV·문서·AI 응답에 직접 적용한 답안과 수정 기록이다. 심화 핵심 문항을 마친 뒤 `readiness-cases.json`에서 예산 계획, 문서 적용, AI 보고서 감사를 수행한다.

다음 단계로 넘어갈 기준은 스스로 계산을 재현하고, 그럴듯한 오답의 잘못된 조건을 설명하며, 검증되지 않은 내용을 보류할 수 있는지다. 처음부터 한 번에 맞히지 못했더라도 오답을 수정하고 조건을 바꾼 문제를 다시 푸는 과정이 학습 기록으로 남는다.
