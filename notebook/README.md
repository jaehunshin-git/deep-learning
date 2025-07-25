# 법률 질의회신 개체명 인식(NER) 모델 구축 프로젝트

이 프로젝트는 대량의 한국어 법률 질의회신 텍스트에서 '질의', '회신', '법령' 등 주요 개체명을 자동으로 추출하고 구조화하기 위한 딥러닝 기반 NER(Named Entity Recognition) 모델을 구축하는 과정을 기록한 문서입니다.

![프로젝트 플로우차트](https://github.com/jaehunshin-git/deep-learning/blob/main/deep-learning-flowchart.png?raw=1)

---

## 🎯 프로젝트 개요 및 동기

이 프로젝트는 공공기관의 법령해석 데이터셋을 처리하는 실제 업무의 비효율을 해결하고자 시작되었습니다. 약 2만 개에 달하는 질의회신 세트를 수작업으로 검증하고 분류하는 작업은 엄청난 시간과 노력을 요구했습니다.

### 해결하고자 하는 문제

1.  **방대한 데이터 검증**: 2만 개의 질의-회신 세트가 올바르게 짝지어졌는지 수동으로 확인하는 작업.
2.  **논리적 연결성 판단**: 각 질의와 회신이 내용상 올바르게 연결되었는지 검토.
3.  **특이사항 분류**: 질의와 회신의 개수가 맞지 않거나, 법령에 근거하지 않은 답변 등 예외적인 경우를 식별.

이러한 반복적이고 비효율적인 업무를 자동화하고, 그 과정에서 딥러닝, 데이터 라벨링, Docker, NLP 등 최신 기술을 실질적으로 배우고 적용하는 것을 목표로 삼았습니다.

---

## 🛠️ 전체 워크플로우

프로젝트는 다음과 같은 단계로 진행되었습니다.

1.  **환경 설정 (Google Colab)**
    *   GPU 런타임 활성화 및 Google Drive 연동.
    *   `transformers`, `datasets`, `seqeval` 등 필요 라이브러리 설치.

2.  **데이터 준비 및 전처리**
    *   원본 텍스트 파일에서 정규표현식을 사용하여 불필요한 문자열, 공백 등을 제거.
    *   각 질의/회신 쌍을 Doccano에서 개별 문서로 인식할 수 있도록 분리.

3.  **데이터 라벨링 (Doccano & Weak Supervision)**
    *   Docker를 이용해 로컬 환경에 데이터 라벨링 도구 **Doccano**를 설치.
    *   정규표현식 기반의 **약 지도 학습(Weak Supervision)**을 적용하여 '질의 N', '회신 N' 등 명확한 패턴을 가진 개체를 자동으로 '초벌 라벨링'.
    *   Doccano에서 초벌 라벨링된 데이터를 검토 및 수정하고, 복잡한 개체명(`QUESTION_CONTENT`, `LAW_CONTENT` 등)을 수동으로 라벨링.
    *   라벨링된 데이터는 `JSONL` 형식으로 Export.

4.  **모델 학습 (Fine-tuning)**
    *   라벨링된 데이터를 Hugging Face `datasets` 형식으로 변환하고 BIO 태깅 체계 적용.
    *   사전 학습된 한국어 모델인 `klue/bert-base`를 기반으로 개체명 인식 작업을 위해 파인튜닝.
    *   Hugging Face `Trainer` API를 사용하여 학습 과정을 관리하고, `seqeval`을 통해 성능(F1-score 등)을 평가.

5.  **평가 및 추론**
    *   학습된 모델을 저장하고, 새로운 텍스트에 대해 개체명을 예측하는 추론 함수를 구현하여 성능 테스트.

---

## 💡 프로젝트 회고 및 배운 점

이번 프로젝트를 통해 딥러닝 모델을 실제 업무에 적용하는 전체 과정을 경험하며 많은 것을 배우고 느꼈습니다.

### 기술적 성장 및 경험

*   **클라우드 기반 GPU 활용**: Google Colab의 무료 T4 GPU를 통해 대규모 연산이 필요한 딥러닝 모델을 비용 효율적으로 학습하고 실험할 수 있었습니다.
*   **Docker와 컨테이너 환경 경험**: Doccano를 Docker로 실행하며, 애플리케이션을 격리된 환경에서 손쉽게 배포하고 실행하는 컨테이너 기술의 강력함을 이해했습니다.
*   **End-to-End 파이프라인 구축**: 데이터 전처리부터 라벨링, 모델 학습, 평가, 추론에 이르기까지 전체 머신러닝 파이프라인을 직접 설계하고 구축하며 각 단계의 유기적인 연결성을 실질적으로 이해했습니다.

### 딥러닝 모델과 데이터에 대한 깊은 이해

*   **"Garbage In, Garbage Out"**: 모델의 성능은 결국 데이터의 양과 질에 의해 결정된다는 것을 체감했습니다. 라벨링된 데이터 샘플의 수가 많을수록 모델의 정확도가 비례하여 향상되는 것을 직접 확인하며, 양질의 데이터 확보의 중요성을 깨달았습니다.
*   **사전 학습 모델(Pre-trained Model)의 위력**: `klue/bert-base`와 같이 이미 방대한 한국어 데이터를 학습한 모델을 활용함으로써, 비교적 적은 데이터로도 특정 도메인의 작업을 효율적으로 수행할 수 있다는 전이 학습의 개념을 실제로 적용해보았습니다.

### 현실적인 한계와 성과

*   **고품질 학습 데이터셋 구축의 어려움**: 모델이 전체 데이터의 패턴을 학습할 만큼 충분한 양의 대표적인 샘플을 고품질로 라벨링하는 것 자체가 매우 힘든 작업이었습니다. 이로 인해 100% 완벽한 모델을 만들지는 못했지만, 지도 학습의 핵심 원리와 데이터의 중요성을 체감하는 계기가 되었습니다.
*   **그럼에도 불구하고, 성공적인 자동화**: 비록 모델이 완벽하지는 않았지만, 개발된 자동화 시스템은 기존의 수작업 검증 방식에 비해 **업무 효율을 압도적으로 향상**시켰습니다. 반복적인 작업을 자동화하여 시간을 절약하고 더 중요한 분석 작업에 집중할 수 있게 되었다는 점에서 이 프로젝트는 매우 성공적이었습니다. 이는 '완벽함'보다 '개선'을 목표로 하는 것의 중요성을 일깨워 주었습니다.

---

## 🚀 향후 개선 방향

*   **더 많은 고품질 데이터 확보**: 모델 성능 향상의 가장 핵심적인 요소로, Doccano를 통해 더 많은 데이터를 일관성 있게 라벨링하는 것이 최우선 과제입니다.
*   **Active Learning 도입**: 모델이 예측을 가장 불확실하게 내놓은 샘플을 우선적으로 라벨링하여 효율적으로 성능을 개선합니다.
*   **하이퍼파라미터 튜닝**: `learning_rate`, `num_train_epochs` 등을 조정하여 모델의 학습 과정을 최적화합니다.
*   **모델 아키텍처 고도화**: 최신 또는 도메인 특화 모델을 활용하거나, 여러 모델의 예측을 결합하는 앙상블 기법을 도입합니다.
