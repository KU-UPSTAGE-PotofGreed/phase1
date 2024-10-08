# 📝 Filtering AI : AI 자소서를 잡아라


https://github.com/user-attachments/assets/5b72a15f-cca8-4466-b488-e48a7628cf52


이 프로젝트는 Upstage의 Solar 모델을 사용하여 개발되었으며, 주로 한국어 자기소개서 텍스트를 대상으로 합니다. Gen AI로 생성된 텍스트를 탐지하고 분석하는 Streamlit 기반의 웹 어플리케이션입니다. 

## Goal

Gen AI의 의존도가 높은 자기소개서 판별


## Target Audience

기업 인사팀, 채용 담당자


## 주요 기능 : Gen AI로 생성된 자기소개서 탐지 및 분석

 - Gen AI 탐지 결과 True/False 제공
 - Gen AI 작성으로 추정되는 문장 하이라이트 제시
 - Gen AI 생성 가능성을 백분율(%)로 제시
 - 주요 키워드 추출 및 시각화
 - 텍스트 통계 정보 제공 (단어 수, 문자 수, 문장 수)


## Installation

#### 1. 저장소 클론:

```
git clone 
cd gpt-text-detector
```


#### 2. 필요한 패키지 설치

```
pip install -r requirements.txt
```

#### 3. 환경변수 설정
.env 파일을 생성하고 다음 내용을 추가:

```
UPSTAGE_API_KEY=your_upstage_api_key_here
```


## Demo

```
streamlit our_demo/run app_v01.py
```


## 폴더 구조

```
Origin-main/
└── our_demo                        # 데모파일 모음    
│   ├── .env                        # 환경 변수 파일 (git에 포함하지 않음)
│   ├── app_v01.py                  # 메인 Streamlit 애플리케이션
│   ├── detection_prompt.txt        # GPT 탐지 Prompt
│   ├── threadhold.py               # Threadhold 확인을 위한 테스트 py
│   ├── Generation_file             # GenAI 생성 자기소개서 모음
│   │   ├── resume_generation.csv   # GenAI 생성 자기소개서리스트
│   │   └── test.csv                # threadhold 확인을 위한 excel
│   ├── static                      # 정적 파일 (로고 등)
│   │   ├── korea_univ.png
│   │   └── upstage.png
│   └── textmining                  # 텍스트 마이닝 관련 파일
│       text
│       ├── textmining.ipynb
│       ├── resume_generation.csv
│       ├── adverb_list.txt    
│       ├── adjective_list.txt
│       ├── adverb_list.txt
│       ├── noun_list.txt
│       ├── verb_list.txt
│       └── wordcloud
│           ├── adjective.png
│           ├── adverb.png
│           ├── noun.png
│           └── verb.png
│
├── LLM Innovators Challenge_ 도파밍 (김은채, 이자경, 지현아).pdf  #제출 ppt 
├── 데모영상.mp4                                                   #제출 영상
├── README.md
└── requirements.txt                              # 필요한 Python 패키지 목록

```

## 주의사항

- 이 도구는 100% 정확하지 않을 수 있으며, 결과는 참고용으로만 사용해야 합니다.
- 짧은 텍스트나 매우 일반적인 문장의 경우 정확도가 떨어질 수 있습니다.
- API 키를 안전하게 관리하고, 공개 저장소에 업로드하지 않도록 주의하세요.


## 감사의 글

이 프로젝트는 고려대학교와 Upstage의 협력으로 개발되었습니다. 모든 기여자와 지원해 주신 분들께 감사드립니다.
