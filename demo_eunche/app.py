import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
import plotly.graph_objects as go
from collections import Counter

# Load environment variables
load_dotenv()

# Get Upstage API Key
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

# Check if API key is available
if not UPSTAGE_API_KEY:
    st.error("UPSTAGE_API_KEY is not set in the environment variables.")
    st.stop()

# Initialize Upstage Chat model
try:
    chat = ChatUpstage(upstage_api_key=UPSTAGE_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize ChatUpstage: {str(e)}")
    st.stop()

# Prompt file path
DETECTION_PROMPT_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/detection_prompt.txt"

# Read prompt from file
def load_detection_prompt():
    try:
        with open(DETECTION_PROMPT_FILE, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
        return prompt_template
    except FileNotFoundError:
        st.error(f"{DETECTION_PROMPT_FILE} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"프롬프트 파일 로드 중 오류 발생: {str(e)}")
        return None

# Calculate GPT generation probability
def calculate_gpt_probability(text):
    score = 0
    total_checks = 4

    if len(text) > 100:
        score += 1
    complex_words = ['therefore', 'furthermore', 'consequently', 'nevertheless']
    if any(word in text.lower() for word in complex_words):
        score += 1
    sentences = re.split(r'[.!?]+', text)
    if len(set([len(s.split()) for s in sentences if s])) > 2:
        score += 1
    if re.search(r'\d+\s*(kg|km|m|cm)', text):
        score += 1

    return (score / total_checks) * 100

# Text detection and AI response processing function
def upstage_text_detection_with_prompt(user_input):
    prompt_template = load_detection_prompt()
    
    if prompt_template is None:
        return "프롬프트 파일을 로드할 수 없습니다.", None

    prompt = prompt_template.format(input_text=user_input)
    try:
        response = chat([{"role": "user", "content": prompt}])
        full_response = response.content
        probability = calculate_gpt_probability(user_input)
    except Exception as e:
        full_response = f"응답 생성 중 오류가 발생했습니다: {str(e)}"
        probability = None

    return full_response, probability

# Create gauge chart
def create_gauge_chart(probability):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        title={'text': "GPT 생성 가능성"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#3498DB"},
               'steps': [
                   {'range': [0, 50], 'color': "#EBF5FB"},
                   {'range': [50, 75], 'color': "#85C1E9"},
                   {'range': [75, 100], 'color': "#5DADE2"}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
    return fig

# 키워드 분석 함수
def analyze_keywords(text):
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    return word_freq.most_common(5)  # 상위 5개 키워드 반환

# 키워드 그래프 생성 함수
def create_keyword_chart(keywords):
    words, counts = zip(*keywords)
    fig = go.Figure(data=[
        go.Bar(x=counts, y=words, orientation='h', marker_color=['#5DADE2', '#85C1E9', '#AED6F1', '#D6EAF8', '#EBF5FB'])
    ])
    
    fig.update_layout(
        title="주요 키워드",
        xaxis_title="출현 빈도",
        yaxis_title="키워드",
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)')
    )
    fig.update_yaxes(autorange="reversed")
    
    return fig

# Streamlit UI
def main_app():
    st.set_page_config(page_title="GPT 감지 대시보드", layout="wide")

    st.title("🕵️‍♂️ GPT 감지 및 분석 대시보드")

    # 상단 레이아웃
    col1, col2 = st.columns([1, 1])

    # 왼쪽 상단: 텍스트 입력
    with col1:
        user_input = st.text_area("텍스트를 입력하세요:", placeholder="여기에 분석할 텍스트를 입력하세요...", height=200)
        analyze_button = st.button("🔍 GPT 감지 및 분석 시작")

    # 오른쪽 상단: 분석 결과
    with col2:
        st.subheader("📊 분석 결과")
        result_placeholder = st.empty()

    # 분석 시작
    if analyze_button and user_input:
        with st.spinner('분석 중...'):
            detection_result, probability = upstage_text_detection_with_prompt(user_input)
        
        # 분석 결과 표시
        with result_placeholder:
            st.info(detection_result)

            if probability is not None:
                fig = create_gauge_chart(probability)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("확률 정보를 계산하지 못했습니다.")

        # 하단 레이아웃
        if user_input:
            col3, col4 = st.columns([1, 1])

            # 왼쪽 하단: 텍스트 통계
            with col3:
                word_count = len(user_input.split())
                char_count = len(user_input)
                sentence_count = len(re.findall(r'\w+[.!?]', user_input))
                
                st.subheader("📝 텍스트 통계")
                st.write(f"**단어 수:** {word_count}")
                st.write(f"**문자 수:** {char_count}")
                st.write(f"**문장 수:** {sentence_count}")

            # 오른쪽 하단: 주요 키워드
            with col4:
                keywords = analyze_keywords(user_input)
                fig = create_keyword_chart(keywords)
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main_app()