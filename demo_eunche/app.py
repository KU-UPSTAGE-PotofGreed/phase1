import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage

# 환경 변수 로드
load_dotenv()

# Upstage API Key 가져오기
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

# Upstage Chat 모델 초기화
chat = ChatUpstage(upstage_api_key=UPSTAGE_API_KEY)

# 프롬프트 파일 경로
DETECTION_PROMPT_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/detection_prompt.txt"

# 프롬프트 파일에서 프롬프트 읽기
def load_detection_prompt():
    try:
        with open(DETECTION_PROMPT_FILE, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
        return prompt_template
    except FileNotFoundError:
        st.error(f"{DETECTION_PROMPT_FILE} 파일을 찾을 수 없습니다.")
        return None

# GPT 생성 가능성을 계산하는 함수
def calculate_gpt_probability(text):
    # 여기에 텍스트 특성을 분석하는 로직을 구현합니다
    score = 0
    total_checks = 4

    # 1. 텍스트 길이 체크
    if len(text) > 100:
        score += 1

    # 2. 복잡한 단어 사용 체크
    complex_words = ['therefore', 'furthermore', 'consequently', 'nevertheless']
    if any(word in text.lower() for word in complex_words):
        score += 1

    # 3. 문장 구조의 다양성 체크
    sentences = re.split(r'[.!?]+', text)
    if len(set([len(s.split()) for s in sentences if s])) > 2:
        score += 1

    # 4. 특정 패턴 체크 (예: 숫자와 단위의 조합)
    if re.search(r'\d+\s*(kg|km|m|cm)', text):
        score += 1

    # 최종 확률 계산
    probability = (score / total_checks) * 100
    return probability

# 텍스트 판별 및 AI 응답 처리 함수 (프롬프트 사용)
def upstage_text_detection_with_prompt(user_input):
    prompt_template = load_detection_prompt()
    
    if prompt_template is None:
        return "프롬프트 파일을 로드할 수 없습니다.", None

    prompt = prompt_template.format(input_text=user_input)
    response = chat([{"role": "user", "content": prompt}])

    try:
        full_response = response.content
        probability = calculate_gpt_probability(user_input)
    except AttributeError:
        full_response = "응답 생성 중 오류가 발생했습니다."
        probability = None

    return full_response, probability

# Streamlit UI
def main_app():
    st.title("GPT 감지 및 판별 (프롬프트 기반)")

    user_input = st.text_area("질문을 입력하세요:", placeholder="여기에 질문을 입력하세요...")

    if st.button("GPT 감지 및 답변 생성"):
        if user_input:
            st.write(f"입력한 텍스트: {user_input}")

            detection_result, probability = upstage_text_detection_with_prompt(user_input)
            
            st.write("프롬프트 기반 판별 결과:")
            st.write(detection_result)

            if probability is not None:
                st.progress(probability / 100)  # 프로그레스 바로 퍼센트 표시
                st.write(f"GPT 생성 가능성: {probability:.2f}%")
            else:
                st.error("확률 정보를 계산하지 못했습니다.")
        else:
            st.error("입력한 텍스트가 없습니다. 질문을 입력하세요.")

# 메인 실행 부분
if __name__ == "__main__":
    main_app()