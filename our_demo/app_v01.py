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
from langchain.schema import HumanMessage

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

# Korean sentence tokenization function
def korean_sentence_tokenize(text):
    pattern = r'(?<=[.!?])\s+|(?<=[.!?])$'
    sentences = re.split(pattern, text)
    return [sent.strip() for sent in sentences if sent.strip()]

# Prompt file path
DETECTION_PROMPT_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/detection_prompt.txt"

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


# 파일에서 단어 리스트를 읽어오는 함수
def read_word_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [word.strip() for word in file.readlines() if word.strip()]
    except FileNotFoundError:
        st.error(f"{file_path} 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        st.error(f"파일 읽기 중 오류 발생: {str(e)}")
        return []

# 파일 경로 설정 (실제 파일 경로로 수정 필요)
ADVERB_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/textmining/adverb_list.txt"
NOUN_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/textmining/noun_list.txt"
VERB_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/textmining/verb_list.txt"
ADJECTIVE_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/textmining/adjective_list.txt"

# 단어 리스트 로드
ADVERBS = read_word_list(ADVERB_FILE)
NOUNS = read_word_list(NOUN_FILE)
VERBS = read_word_list(VERB_FILE)
ADJECTIVES = read_word_list(ADJECTIVE_FILE)


def calculate_korean_gpt_probability(text):
    score = 0
    total_checks = 100  # 체크 항목 수
    text_length = len(text)

    # 텍스트 길이에 따른 기준 설정
    # length_threshold = 500  # 500자를 기준으로 설정
    # length_factor = min(text_length / length_threshold, 1)  # 1을 초과하지 않도록 제한

    # 쉼표 개수 체크 (수정된 부분)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]  # 빈 문장 제거
    sentences_with_many_commas = [s for s in sentences if s.count(',') >= 2]
    if len(sentences_with_many_commas) >= 1:  # 10% 이상의 문장이 쉼표 2개 이상이면
        score += 20

    # 자주 등장하는 부분 체크
    korean_connectives = ['시절', '맡았으며', '특히', '우선', '입사 후', '에서,', '이에 따라', '바탕으로', '저는', '고,', '이는', '통해']
    connective_count = sum(text.count(word) for word in korean_connectives)
    if connective_count >= 2 :#* length_factor:  # 텍스트 길이에 비례하여 조정
        score += 35

    # 긴 문장 체크
    if sentences:
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        if len(long_sentences) >= len(sentences) * 0.3 :#* length_factor / 2:  # 텍스트 길이에 비례하여 조정
            score += 15

    # 부사 사용 체크
    adverb_count = sum(text.count(adverb) for adverb in ADVERBS)
    if adverb_count >= 2 :# * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 15

    # 명사 사용 체크
    noun_count = sum(text.count(noun) for noun in NOUNS)
    if noun_count >= 2 :# * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 5

    # 동사 사용 체크
    verb_count = sum(text.count(verb) for verb in VERBS)
    if verb_count >= 2 :#* length_factor:  # 텍스트 길이에 비례하여 조정
        score += 5

    # 형용사 사용 체크
    adj_count = sum(text.count(adj) for adj in ADJECTIVES)
    if adj_count >= 2 :# * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 5
    

    # 텍스트 길이에 따른 점수 조정
    # normalized_score = score * (1 - 0.2 * length_factor)  # 텍스트가 길수록 점수를 약간 낮춤

    return (score / total_checks) * 100

# 텍스트에서 GPT 사용 가능성이 높은 문장 식별 함수
def identify_gpt_sentences(text, threshold=50):
    sentences = korean_sentence_tokenize(text)
    gpt_sentences = []
    for sentence in sentences:
        probability = calculate_korean_gpt_probability(sentence)
        if probability >= threshold:
            gpt_sentences.append((sentence, probability))
    return gpt_sentences

# 하이라이트된 텍스트 생성 함수
def create_highlighted_text(text, gpt_sentences):
    highlighted_text = text
    for sentence, probability in sorted(gpt_sentences, key=lambda x: len(x[0]), reverse=True):
        highlighted_sentence = f'<span style="background-color: rgba(128, 92, 251, {probability/100});">{sentence}</span>'
        highlighted_text = highlighted_text.replace(sentence, highlighted_sentence)
    return highlighted_text

# Text detection and AI response processing function
def upstage_text_detection_with_prompt(user_input):
    prompt_template = load_detection_prompt()

    if prompt_template is None:
        return "프롬프트 파일을 로드할 수 없습니다.", None

    # Calculate GPT probability for user input
    probability = calculate_korean_gpt_probability(user_input)

    # Modify prompt to include the user's input and their question
    prompt = prompt_template.format(input_text=user_input, probability_score=probability)

    try:
        response = chat.invoke([HumanMessage(content=prompt)])
        full_response = response.content
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

def create_gauge_chart(probability):
    base_color = "#805CFB"
    grape_color = "rgba(255, 255, 255, 0.8)"
    lighter_color = "#A389FD"
    darker_color = "#5C3DB8"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        title={'text': "GPT 생성 가능성", 'font': {'size': 24}},
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'size': 40}, 'suffix': "%"},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': grape_color},
            'bgcolor': "white",
            'borderwidth': 0.8,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': darker_color},
                {'range': [33, 66], 'color': base_color},
                {'range': [66, 100], 'color': lighter_color}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.60,
                'value': 70
            }
        }))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig

# 키워드 분석 함수
def analyze_keywords(text):
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    return word_freq.most_common(5)  # 상위 5개 키워드 반환

# 키워드 그래프 생성 함수
def create_keyword_chart(keywords):
    words, counts = zip(*keywords)
    base_color = "#805CFB"
    color_scale = [
        f"rgba({128 + i * 25}, {92 + i * 25}, {251}, {1 - i * 0.15})"
        for i in range(5)
    ]

    fig = go.Figure(data=[
        go.Bar(x=counts, y=words, orientation='h', 
               marker_color=color_scale)
    ])

    fig.update_layout(
        title="주요 키워드",
        xaxis_title="출현 빈도",
        yaxis_title="키워드",
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
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
        school_logo = Image.open("/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/static/korea_univ.png")
        company_logo = Image.open("/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/our_demo/static/upstage.png")
        
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

    if analyze_button and user_input:  # 여기서 user_input을 체크합니다.
        with st.spinner('분석 중...'):
            detection_result, probability = upstage_text_detection_with_prompt(user_input)
            gpt_sentences = identify_gpt_sentences(user_input, threshold=0)

        # 분석 결과 섹션
        st.header("분석 결과")
        st.subheader("GPT 감지 결과")
        st.info(detection_result)

        if probability is not None:
            st.subheader("GPT 생성 가능성")
            fig = create_gauge_chart(probability)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("확률 정보를 계산하지 못했습니다.")

        # GPT 사용 가능성이 높은 문장 하이라이트
        if gpt_sentences:
            st.subheader("GPT 사용 가능성이 높은 부분")
            highlighted_text = create_highlighted_text(user_input, gpt_sentences)
            st.markdown(highlighted_text, unsafe_allow_html=True)

            # GPT 사용 가능성이 높은 문장 리스트
            st.subheader("GPT 사용 가능성이 높은 문장")
            for sentence, prob in gpt_sentences:
                st.markdown(f"- {sentence} (확률: {prob:.2f}%)")
        else:
            st.info("GPT 사용 가능성이 높은 문장이 발견되지 않았습니다.")

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
