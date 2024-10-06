import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
import plotly.graph_objects as go
from collections import Counter
from PIL import Image
import base64
from io import BytesIO


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

def calculate_korean_gpt_probability(text):
    score = 0
    total_checks = 4

    # 쉼표 비율 체크
    comma_ratio = text.count(',') / len(text) if len(text) > 0 else 0
    if comma_ratio > 0.05:  # 텍스트 길이의 5% 이상이 쉼표일 경우
        score += 1

    # 한국어 접속사 체크
    korean_connectives = ['그리고', '하지만', '그러나', '또한', '그래서', '따라서', '그러므로', '그런데']
    connective_count = sum(text.count(word) for word in korean_connectives)
    if connective_count > 3:  # 3개 이상의 접속사가 있을 경우
        score += 1

    # 긴 문장 체크
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]  # 빈 문장 제거
    long_sentences = [s for s in sentences if len(s.split()) > 15]  # 15단어 이상을 긴 문장으로 간주
    if sentences and len(long_sentences) > len(sentences) / 3:  # 1/3 이상의 문장이 긴 경우
        score += 1

    # 복잡한 단어 체크
    complex_words = ['따라서', '그럼에도 불구하고', '결과적으로', '그렇지만']
    if any(word in text for word in complex_words):
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

# 이미지를 Base64로 인코딩하는 함수
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


# Create gauge chart
def create_gauge_chart(probability):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        title={'text': "GPT 생성 가능성"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#8E44AD"},
            'steps': [
                {'range': [0, 50], 'color': "#4A235A"},
                {'range': [50, 75], 'color': "#6C3483"},
                {'range': [75, 100], 'color': "#8E44AD"}
            ],
            'threshold': {'line': {'color': "white", 'width': 0}, 'thickness': 0.75, 'value': 90}
        }))
    fig.update_layout(height=300)
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
        go.Bar(x=counts, y=words, orientation='h', 
               marker_color=['#8E44AD', '#9B59B6', '#AF7AC5', '#C39BD3', '#D7BDE2'])
    ])
    
    fig.update_layout(
        title="주요 키워드",
        xaxis_title="출현 빈도",
        yaxis_title="키워드",
        height=300
    )
    fig.update_yaxes(autorange="reversed")
    
    return fig

# Streamlit UI
def main_app():
    st.set_page_config(page_title="GPT 감지 보고서", layout="wide")

    # 사이드바 컨텐츠
    with st.sidebar:
        st.markdown("""
        🎓 **알림**    
        해당 페이지는 고려대학교와 upstage가 함께하는 명품인재 프로젝트 출전작 입니다.  
        """)
        st.subheader("🧑‍💻 만든이")
        st.markdown("""
        고려대학교 BA과정 김은채, 이자경, 지현아
        """)
        
        # 맨 아래에 로고 추가를 위한 공간 확보
        st.markdown("<div style='flex-grow: 1; height: 600px;'></div>", unsafe_allow_html=True)
        
        st.markdown("---")
    
        # 학교 로고 불러오기
        school_logo = Image.open("/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/static/korea_univ.png")
        company_logo = Image.open("/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/static/upstage.png")
        
        # 로고를 Base64로 인코딩한 후 HTML로 삽입
        school_logo_base64 = image_to_base64(school_logo)
        company_logo_base64 = image_to_base64(company_logo)
        
        # 하단에 로고와 카피라이트 배치 (여유 공간을 확보한 후 배치)
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
            <img src="data:image/png;base64,{school_logo_base64}" width="200"/>
            <img src="data:image/png;base64,{company_logo_base64}" width="200"/>
            <p>© 2024 고려대학교 & KU-Upstage. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)
    # 메인 컨텐츠
    st.title("🕵️‍♂️ GPT 감지 및 분석 보고서")

    # 입력 섹션
    st.header("자기소개서 확인해보기")
    user_input = st.text_area("분석할 텍스트를 입력하세요:", placeholder="여기에 텍스트를 입력하세요...", height=300)
    analyze_button = st.button("🔍 GPT 감지 및 분석 시작")

    if analyze_button and user_input:
        with st.spinner('분석 중...'):
            detection_result, probability = upstage_text_detection_with_prompt(user_input)

        # 분석 결과 섹션
        st.header("분석 결과")
        st.subheader("2.1 GPT 감지 결과")
        st.info(detection_result)

        if probability is not None:
            st.subheader("GPT 생성 가능성")
            fig = create_gauge_chart(probability)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("확률 정보를 계산하지 못했습니다.")

        # 텍스트 통계 섹션
        st.header("텍스트 통계")
        col1, col2, col3 = st.columns(3)
        word_count = len(user_input.split())
        char_count = len(user_input)
        sentence_count = len(re.findall(r'\w+[.!?]', user_input))
        
        with col1:
            st.metric("단어 수", word_count)
        with col2:
            st.metric("문자 수", char_count)
        with col3:
            st.metric("문장 수", sentence_count)

        # 키워드 분석 섹션
        st.header("주요 키워드 분석")
        keywords = analyze_keywords(user_input)
        fig = create_keyword_chart(keywords)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main_app()