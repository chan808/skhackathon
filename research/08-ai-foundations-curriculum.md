# AI 기초부터 응용까지 학습하는 커리큘럼

기준일 2026년 10월 14일 한국시간. 이 문서는 처음 실습하는 참가자가 AI 기본 개념, 학습과 평가, LLM 활용, 에이전트와 반도체 맥락을 연결하는 학습 지도다. **아래 우선순위는 준비 권고이며 SK하이닉스의 확정 출제 범위나 배점표가 아니다.** 폭넓은 주제를 준비하되 한 번에 모든 라이브러리를 설치하거나 논문을 완독하는 것을 완료 기준으로 삼지 않는다.

첫 목표는 “어떤 문제를 어떤 방식으로 풀고, 결과가 맞는지 무엇으로 확인하는가”를 설명하고 작은 숫자로 직접 확인하는 것이다. 현재 준비를 넓힐 때 가장 먼저 추가할 범위는 고전 머신러닝, 학습 수학, 손실과 최적화, 딥러닝의 입력·출력 차원이다. LLM 도구 사용 경험과 연결하면 이해하기 쉽다.

## 전체 지도와 학습 순서

P0는 1차 전에 우선 익힐 기초, P1은 그다음에 이해를 넓힐 핵심, P2는 이후 과제와 관심에 따라 확장할 범위다. 실제 문제를 보고 우선순위를 바꿀 수 있다.

| 영역 | 우선 | 익힐 내용 | 설명 또는 손계산으로 확인할 것 |
|---|---|---|---|
| 문제와 학습 방식 | P0 | 지도·비지도·자기지도·강화, 회귀·분류·군집 | 생산량 예측과 불량 분류의 출력 차이 |
| 기초 수학 | P0 | 평균·분산·확률·벡터·행렬·미분 | 행렬 곱의 차원, 기울기와 업데이트 방향 |
| 데이터와 분할 | P0 | feature·label, train·validation·test, 시간·그룹 분할 | 예측 시 알 수 없는 정보를 찾기 |
| 전처리 | P0 | 결측·중복·표준화·범주형·이상치 | 평균과 표준편차를 어느 자료에서 학습하는가 |
| 고전 ML | P0 | 선형·로지스틱 회귀, 결정트리와 기준선 | 모델 출력과 적용할 지표 선택 |
| 성능 평가 | P0 | 혼동행렬·정밀도·재현율·F1·오차·임계값 | 불량이 드문 자료에서 accuracy의 한계 |
| 학습과 일반화 | P0 | loss·경사하강·학습률·과적합·규제 | train 성능만 높을 때 확인할 것 |
| 딥러닝 | P1 | 층·가중치·활성화·역전파·SGD·Adam·dropout | train과 eval의 동작 차이 |
| 영상과 전이학습 | P1 | CNN, 채널·kernel·stride·padding, freeze | CNN 출력 모양과 파라미터 수 |
| LLM 원리 | P0 또는 P1 | 토큰·embedding·attention·causal mask·logit·decoding | 확률·유사도·사실성의 차이 |
| 검색과 RAG | P0 또는 P1 | chunk·metadata·검색·hybrid·rerank·근거 평가 | 검색 누락과 답변 오류 구분 |
| 도구와 에이전트 | P0 또는 P1 | 구조화 출력·함수·관찰·종료·권한·MCP·skill | 호출 요청과 실제 실행 구분 |
| 모델 효율 | P2 | LoRA·quantization·MoE·KV cache·HBM | 계산량·메모리·대역폭·품질의 절충 |
| 현장 적용 | P2 | 예측·이상 탐지·문서·영상·운영 검증 | 업무 KPI와 분석 단위부터 정의 |

표의 뒤쪽 주제를 먼저 접했더라도 앞쪽의 문제 정의·데이터·평가를 함께 익혀야 한다. “모델 이름을 안다”, “프레임워크가 실행된다”보다 새로운 사례에서 잘못된 가정을 고칠 수 있는지를 확인한다.

## 문제 유형과 학습 방식

지도학습은 입력과 정답의 관계를 학습한다. 수치 출력이면 회귀, 범주 출력이면 분류로 생각할 수 있다. 비지도학습은 주어진 정답 라벨 없이 구조를 찾으며 군집이 대표적인 예다. 강화학습은 환경에서 행동하고 얻은 보상으로 정책을 학습한다. 생성형 모델도 여러 학습 방식을 결합할 수 있다. [Google 머신러닝 입문](https://developers.google.com/machine-learning/intro-to-ml/what-is-ml)

자기지도학습은 입력에서 학습 목표를 구성한다. 문맥으로 다음 토큰이나 가려진 토큰을 예측하는 언어모델 학습이 예다. “사람이 매번 라벨을 만들지 않았다”와 “정답 역할을 하는 학습 목표가 없다”는 다른 말이다. [Hugging Face Transformer 입문](https://huggingface.co/learn/llm-course/en/chapter1/4)

자체 분류 연습을 한다. 다음 달 생산량은 회귀, 불량 여부는 분류, 비슷한 장비 로그를 묶는 일은 군집, 보상을 고려한 행동 전략은 강화학습과 연결된다. 동일 업무에도 여러 접근을 조합할 수 있으므로 문제를 보고 딱 하나의 이름만 고르는 것으로 끝내지 않는다. 생성형 AI로 규정 설명을 만들면서 계산은 코드로 수행할 수도 있다.

**자기 점검:** “모든 자동화는 강화학습인가?”에 “아니다. 도구를 호출하거나 규칙으로 다음 단계를 정하는 실행 자체는 보상으로 정책을 학습하는 과정과 구분한다”라고 설명할 수 있으면 된다.

## 수학과 고전 모델을 작은 숫자로 이해하기

시작할 수학은 행렬을 깊게 증명하는 것이 아니라 입력·가중치·출력이 어떻게 연결되는지 확인하는 수준이다. 길이 3인 feature 벡터와 길이 3인 가중치 벡터의 내적은 스칼라 하나다. 여러 표본을 2×3 행렬로 묶고 3×1 가중치와 곱하면 출력은 2×1이다. 내적의 값과 cosine similarity의 정규화는 구분한다.

선형 모델의 기본형은 y_hat = w×x+b다. 로지스틱 회귀는 선형 점수에 sigmoid를 적용해 이진 분류 확률을 다룬다. 따라서 이름에 회귀가 있어도 일반적인 용도는 수치 회귀와 다르다. [Google 로지스틱 회귀](https://developers.google.com/machine-learning/crash-course/logistic-regression)

결정트리는 feature 조건에 따라 자료를 나눈다. 깊고 제한 없는 트리는 과적합할 수 있다. 수치 스케일에 민감한 방법과 달리 트리에는 같은 방식의 표준화가 필수인 것은 아니다. 자료 형식과 결측 처리는 구현에 맞춰 확인해야 한다. [scikit-learn 결정트리](https://scikit-learn.org/stable/modules/tree.html)

| 방법 | 우선 이해할 역할 | 먼저 확인할 함정 |
|---|---|---|
| 선형 회귀 | 수치 예측의 기준선 | 관계가 선형이라는 가정과 이상치 |
| 로지스틱 회귀 | 이진 분류 확률·기준선 | 확률 출력과 최종 클래스의 임계값 |
| 결정트리 | 조건 분기에 따른 예측 | 과도한 깊이와 표본별 변동 |
| Random Forest | 여러 트리의 결과를 결합 | 더 많은 트리가 누설을 고치지는 않음 |
| Gradient Boosting | 순차적으로 모델을 더해 개선 | 학습률·복잡도·검증 조건 |
| K-means | 가까운 표본을 k개 군집으로 묶기 | k·거리·스케일과 군집의 업무 의미 |
| PCA | 분산을 보존하는 방향으로 차원 축소 | 정답 라벨에 가장 유용한 방향과 같지는 않음 |

뒤쪽 방법은 P1 또는 P2로 넓히면 된다. 앙상블, 군집, 차원 축소의 공식 설명은 필요한 행을 찾아 읽는 방식으로 사용한다. [앙상블](https://scikit-learn.org/stable/modules/ensemble.html), [군집](https://scikit-learn.org/stable/modules/clustering.html), [PCA](https://scikit-learn.org/stable/modules/decomposition.html)

### 손실과 경사하강 한 번 계산하기

loss는 모델을 학습시킬 때 줄이려는 값이다. MSE는 오차의 제곱을 평균하며 큰 오차의 영향을 크게 받는다. 평가지표는 최종 업무 성능을 측정하는 기준으로 loss와 같을 수도 다를 수도 있다. [Google 손실](https://developers.google.com/machine-learning/crash-course/linear-regression/loss)

다음은 이 문서가 만든 단일 표본 예제다. x=2, 정답 y=3, 초기 w=1, b=0이고 **b는 고정**한다. 손실은 L=(w×x−y)²이며 평균을 취할 표본은 하나다.

1. 예측은 2, 오차는 −1, 손실은 1이다.
2. dL/dw = 2×(w×x−y)×x = −4다.
3. 학습률 0.1로 w_new = w−0.1×dL/dw = 1.4다.
4. 새 예측은 2.8, 손실은 0.04다.

기울기를 구하는 것과 가중치를 업데이트하는 것은 별도 단계다. 학습률이 크면 개선을 지나쳐 진동·발산할 수 있고 작으면 느리게 학습할 수 있다. 한 사례에서 손실이 줄었다고 다른 자료의 일반화가 확인된 것은 아니다. [Google 경사하강](https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent), [학습률과 hyperparameter](https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters)

**자기 점검:** 같은 조건에서 학습률을 1로 바꾸면 w=5, 예측=10, 손실=49다. “학습률을 크게 하면 항상 빨리 좋은 답에 도달한다”는 주장을 이 수치로 반박할 수 있다.

## 데이터와 평가를 모델보다 먼저 익히기

train은 파라미터 학습, validation은 선택·튜닝, test는 최종 확인을 위한 구분이다. 고정된 정답 비율을 모든 업무에 그대로 적용하지 않는다. 최종 test 결과를 계속 보며 설정을 고르면 평가 자료에 적응할 수 있다. [Google 데이터셋 분할](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets)

feature는 예측 시 사용할 입력이고 label은 예측하려는 대상이다. 누락값과 중복, 단위·타입을 먼저 확인한다. 표준화는 평균과 표준편차를 사용하며, 범주형 값은 숫자 ID를 곧바로 크기 관계로 해석하지 않도록 인코딩을 검토한다. [scikit-learn 전처리](https://scikit-learn.org/stable/modules/preprocessing.html)

전처리의 fit은 train에만 적용하고 test에는 학습한 변환을 적용한다. 검사 이후에 확정되는 원인 코드를 검사 이전의 예측 feature로 쓰는 것도 누설의 후보다. 같은 wafer·lot, 시간 순서에 대한 분할은 [기존 평가 설명](./02-ai-and-assessment.md)을 함께 본다. [scikit-learn 누설 설명](https://scikit-learn.org/stable/common_pitfalls.html)

### 혼동행렬과 확률 보정 계산하기

자체 예제로 제품 1,000개 중 실제 불량은 20개라고 하자. 불량을 양성으로 정의한다. 모델은 불량 18개를 찾고 정상 12개를 불량이라고 했다.

- TP=18, FN=2, FP=12, TN=968.
- precision=18/(18+12)=60%.
- recall=18/(18+2)=90%.
- accuracy=(18+968)/1,000=98.6%.
- F1=2×0.6×0.9/(0.6+0.9)=0.72.

여기서 accuracy가 높다는 사실만으로 불량 오탐과 누락 비용을 판단할 수 없다. 어떤 클래스를 양성으로 두었는지도 확인한다. 같은 고정 점수와 표본에서 임계값을 낮추면 양성으로 분류되는 집합이 넓어지지만 precision이 항상 단조롭게 움직이는 것은 아니다. [Google 분류 지표](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall)

ROC-AUC는 여러 임계값에서의 구분 능력을 다루며 특정 임계값의 accuracy와 다르다. 불균형 자료에서는 정밀도·재현율과 실제 오류 비용도 같이 본다. [Google ROC와 AUC](https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc)

calibration은 예측 확률과 실제 빈도의 일치다. 예측 0.8을 받은 100개 중 실제 양성이 60개라면 이 표본에서는 80%라는 예측이 과신되어 있다. “클래스를 잘 맞춘다”, “순위를 잘 정한다”, “확률이 잘 보정됐다”는 별도 속성이다. 보정 모델을 학습할 자료도 독립 조건을 지켜야 한다. [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html)

**자기 점검:** loss, metric, threshold, calibration의 차이를 각각 한 문장으로 설명하고, 위 표의 분자를 다시 손으로 계산한다.

## 일반화와 딥러닝 학습

과적합은 학습 자료에 맞춘 성능이 새 자료로 이어지지 않는 현상이다. bias는 평균적인 예측의 체계적 차이, variance는 학습 자료가 바뀔 때 예측이 달라지는 정도와 연결된다. “복잡한 모델이 항상 좋다” 대신 데이터·복잡도·검증을 함께 본다. [scikit-learn bias와 variance 예시](https://scikit-learn.org/stable/auto_examples/ensemble/plot_bias_variance.html)

L2 규제는 가중치 크기에 대한 penalty를 더한다. 일반적인 nn.Dropout은 학습 시 일부 활성값을 확률적으로 0으로 만들며 평가 때 같은 방식으로 무작위 제거하지 않는다. early stopping은 validation 기준으로 학습 중단 시점을 고르는 접근이다. [Google L2 규제](https://developers.google.com/machine-learning/crash-course/overfitting/regularization), [PyTorch Dropout](https://docs.pytorch.org/docs/main/generated/torch.nn.Dropout.html), [scikit-learn early stopping 설정](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html)

신경망은 선형 변환과 활성화를 조합한다. 비선형 활성화가 없다면 선형 층을 여러 개 쌓는 것만으로 같은 의미의 비선형 표현이 생기지는 않는다. 역전파는 여러 층의 기울기를 계산하는 과정이고 optimizer는 그것을 사용해 파라미터를 갱신한다. Adam은 기울기의 모멘트 추정 등을 이용하는 optimizer이며 문제마다 무조건 최선인 것은 아니다. [Google 신경망](https://developers.google.com/machine-learning/crash-course/neural-networks), [역전파](https://developers.google.com/machine-learning/crash-course/neural-networks/backpropagation), [PyTorch Adam](https://docs.pytorch.org/docs/main/generated/torch.optim.Adam.html)

딥러닝을 처음 실습할 때에는 batch, epoch, train/eval 모드, gradient, learning rate가 각각 어디에서 사용되는지 확인한다. 파라미터와 hyperparameter도 구분한다. 모델이 학습하는 w와 사람이 선택하는 학습률은 같은 종류의 값이 아니다.

### CNN 모양과 파라미터 수

PyTorch의 일반 Conv2d 입력은 N,C,H,W다. dilation=1이면 한 공간 축의 출력은 floor((입력+2×padding−kernel)/stride)+1이다. [PyTorch Conv2d](https://docs.pytorch.org/docs/main/generated/torch.nn.Conv2d.html)

자체 예제로 입력 (2,3,32,32), 출력 채널 16, kernel=3, stride=2, padding=1, groups=1, bias=True를 두면 다음과 같다.

- 공간 출력: floor((32+2−3)/2)+1=16.
- 출력 모양: (2,16,16,16).
- 학습 파라미터: 16×(3×3×3+1)=448.

batch 크기가 2라고 가중치를 두 벌 학습하는 것은 아니다. 출력 채널과 공간 크기도 별도 축이다. 다른 프레임워크의 축 순서, grouped convolution, dilation이 바뀌면 조건을 다시 확인한다.

전이학습은 사전학습 모델을 새 작업에 사용한다. 앞부분을 고정하고 마지막 층만 학습하거나 전체를 추가 학습할 수 있다. 데이터가 적은 영상 작업에서는 이 두 방식의 차이를 먼저 익힌다. [PyTorch 전이학습 튜토리얼](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

## LLM을 앞의 기초와 연결하기

토큰화는 입력을 처리 단위로 나누고 embedding은 벡터 표현을 만든다. attention은 Q·K의 관련 점수로 V를 조합한다. causal mask는 미래 위치의 정보를 보지 않게 한다. softmax는 점수를 지정한 축에서 분포로 바꾸지만 그 확률이 답변 전체의 사실성은 아니다. 세부 설명과 자체 문제는 [AI 기초 보고서](./02-ai-and-assessment.md)를 이어서 본다. [PyTorch scaled dot product attention](https://docs.pytorch.org/docs/main/generated/torch.nn.functional.scaled_dot_product_attention.html)

준비할 추가 구분은 사전학습, fine-tuning, prompt 예시, RAG다. 입력에 예시를 넣는 것과 모델 가중치를 학습하는 것은 다르다. decoding의 temperature·top-p는 생성 선택, context window는 입력·진행 문맥의 제한이다. 긴 문맥을 넣었다고 모든 근거를 안정적으로 사용했는지 확인한 것은 아니다.

### 이후에 넓힐 모델 효율 주제

LoRA는 기반 가중치를 고정하고 저랭크 행렬을 학습하는 접근이다. MoE는 입력별로 일부 expert 파라미터를 선택하는 희소 구조다. 총 파라미터 수, 토큰당 활성 파라미터 수, 실제 저장 메모리와 통신 비용을 구분한다. [LoRA 원 논문](https://arxiv.org/abs/2106.09685), [Switch Transformer 원 논문](https://arxiv.org/abs/2101.03961)

자체 LoRA 계산에서 4,096×4,096 가중치 하나에 rank=8의 두 행렬만 학습하면 4,096×8+8×4,096=65,536개다. 원 가중치 16,777,216개의 약 0.39%다. bias·다른 층·학습 상태는 제외한 한 행렬 예제이며 실제 모델 전체의 메모리가 이 비율로 줄어든다는 뜻은 아니다.

quantization은 더 낮은 정밀도의 표현을 사용한다. 메모리·속도·오차의 절충이 있고 가중치, 활성값, KV cache의 양자화는 동일한 설정이 아니다. [Hugging Face quantization](https://huggingface.co/docs/transformers/main/en/quantization/overview), [KV cache](https://huggingface.co/docs/transformers/main/en/kv_cache)

자체 가중치 계산으로 정확히 70억 개를 FP16 2바이트로 저장하면 14GB, 4비트로 빈틈없이 저장하면 3.5GB다. decimal GB이며 scale·metadata·활성값·KV·임시 버퍼는 제외했다. 실제 실행에 필요한 GPU 메모리의 측정값은 아니다.

별도의 일반적인 cache 예제로 층 32, batch 1, 길이 4,096, KV head 8, head 차원 128, 원소당 2바이트를 가정한다. K와 V를 모두 저장하면 2×32×1×4,096×8×128×2=536,870,912바이트, 즉 512MiB다. 길이·동시 요청 수가 늘면 cache 예산이 늘어난다. 모델별 attention 방식과 cache 전략에 따라 실제 구조는 달라진다.

KV의 배치와 낭비를 줄이는 것이 serving 처리량에도 영향을 준다는 점은 PagedAttention 연구로 이어진다. 반도체 관점에서는 저장 용량, 이동 대역폭, 연산을 함께 본다. HBM 세부 맥락은 [반도체 조사 보고서](./03-semiconductor-and-projects.md)에 연결했다. [PagedAttention 원 논문](https://arxiv.org/abs/2309.06180)

## RAG와 에이전트를 공부하는 순서

chunk는 문서 경계를 정하는 과정이다. 관련 문맥이 끊기는 경우와 너무 많은 잡음이 들어오는 경우를 함께 평가하고 문서 ID·버전·권한 등의 metadata를 유지한다. 검색에서 날짜·속성 필터를 사용하는 방식도 익힌다. [OpenAI retrieval](https://developers.openai.com/api/docs/guides/retrieval)

hybrid search는 lexical 검색과 semantic 검색을 함께 사용하고, reranker는 먼저 찾은 후보의 순서를 더 정교하게 판단한다. 장비 코드 같은 정확한 문자열과 의미가 비슷한 문장을 모두 다룰 때 비교할 수 있다. reranking은 처음 검색에서 빠진 문서를 자동으로 복구하는 단계는 아니다. [Elastic hybrid search](https://www.elastic.co/docs/solutions/search/hybrid-search), [Sentence Transformers retrieve and rerank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)

평가는 검색 근거의 포함 여부, 최종 답변의 근거 충실성, 숫자·인용의 일치, unknown 처리, 시간·비용으로 나누어 생각한다. 관련 문서가 검색됐다는 것과 답변이 맞다는 것을 따로 검증한다. 작은 정답 사례와 일부 실패 사례를 만든 뒤 설정을 비교하면 된다.

구조화 출력은 형식 계약이고 도구 호출은 실행 요청이다. JSON 문법·스키마·업무 의미와 실제 도구 성공을 구분한다. [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [function calling](https://developers.openai.com/api/docs/guides/function-calling)

에이전트의 목표·관찰·다음 행동·중단 조건, MCP·skill·subagent, 외부 문서의 prompt injection과 권한은 [에이전트와 도구 보고서](./06-agents-and-ai-tools.md)를 사용한다. 처음에는 기존 코딩 에이전트 하나와 좁은 계산·검색 도구로 반복 검증을 해본다. 직접 만든 규칙 기반 데모는 실제 LLM이 다음 행동을 선택하는 실행과 구분해 설명한다.

## 공개 학습 자료로 첫 실습 시작하기

유료 강의나 새 GPU 없이 아래 순서로 시작할 수 있다. 공식 웹 문서의 개념과 공개 연습을 사용하며 실제 모델 훈련에 필요한 실행 자원은 별도로 확인한다.

1. **20분 문제 구분:** 지도·비지도·자기지도·강화의 사례를 각 2개 적고 입력·출력을 정한다.
2. **30분 손계산:** 위 선형 모델의 학습률을 0.01, 0.1, 1로 바꾸고 예측·손실을 다시 구한다.
3. **30분 평가:** 혼동행렬과 분모를 계산하고 어떤 오류의 비용이 더 큰지 적는다.
4. **30분 데이터:** 누락·중복·스케일·시간·wafer 그룹이 분할에 주는 영향을 설명한다.
5. **30분 DL:** CNN 모양과 파라미터를 계산하고 train/eval, backward/optimizer의 차이를 말한다.
6. **40분 LLM 활용:** 합성 표나 SOP에서 AI 답을 얻고 직접 숫자·인용·조건을 검증한다.
7. **20분 회고:** 실제 수행한 작업과 못 한 확인, 발견한 오류, 수정 후 같은 사례의 결과를 적는다.

Google MLCC에는 손실·경사하강·분류·신경망 등의 공개 연습이 모여 있다. 첫날에는 위 2·3단계와 관련한 연습 두 개만 선택한다. [Google 공식 연습 목록](https://developers.google.com/machine-learning/crash-course/exercises)

| 내 상태 | 다음 자료 | 학습 완료 기준 |
|---|---|---|
| AI 문제 유형이 헷갈림 | Google 머신러닝 입문 | 각 사례의 입력·출력·정답 구성 설명 |
| 수식이 부담스러움 | Google 손실·경사하강 | 단일 표본 업데이트 손계산 |
| 결과가 좋다는 판단이 어려움 | Google 분류 지표·scikit-learn calibration | 정밀도·재현율·확률 보정 구분 |
| DL 실행 결과만 봄 | Google 역전파·PyTorch CNN | 축·가중치·기울기·업데이트 설명 |
| LLM과 도구 사용만 익숙함 | 기존 AI 보고서와 본 문서 앞부분 | 누설과 독립 평가 사례 제시 |
| 모델을 직접 훈련하고 싶음 | PyTorch 전이학습 | 작은 데이터의 분할·학습·검증 기록 |
| RAG·agent를 만들고 싶음 | 기존 에이전트 보고서와 검색 문서 | 도구 계약·근거·종료·실패 기준 설명 |

각 단계는 “읽었다”가 아니라 예시 하나를 설명하고 수치 또는 실행 증거로 확인한 경우에 체크한다. 잘못된 답을 발견하면 어떤 가정이 틀렸는지 먼저 적고 같은 사례를 다시 확인한다. 전체 지도는 이후에도 확장할 수 있지만, 1차 전에는 P0 개념과 검증 습관을 먼저 안정시키는 편이 낫다.

## 기록과 출처

이 문서의 수치·시나리오·학습 시간은 자체 작성 예제다. 공개 논문과 공식 문서는 기술 원리의 근거이며 SK 대회 문제를 입증하지 않는다. 버전이 바뀔 수 있는 PyTorch·Hugging Face 문서는 확인한 본문을 기준으로 했고, 해당 main 버전을 설치하도록 요구하지 않는다.

URL, 제목, 접근 날짜와 제한은 [기초 학습 출처 등록부](./foundation-sources.json)에 있다. 실제 대회 플랫폼·규정은 [대회 정보](./01-event.md)를 기준으로 별도 확인한다.
