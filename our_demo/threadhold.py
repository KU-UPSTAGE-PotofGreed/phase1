import pandas as pd
import re

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
ADVERB_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/textmining/adverb_list.txt"
NOUN_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/textmining/noun_list.txt"
VERB_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/textmining/verb_list.txt"
ADJECTIVE_FILE = "/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/textmining/adjective_list.txt"

# 단어 리스트 로드
ADVERBS = read_word_list(ADVERB_FILE)
NOUNS = read_word_list(NOUN_FILE)
VERBS = read_word_list(VERB_FILE)
ADJECTIVES = read_word_list(ADJECTIVE_FILE)


def calculate_korean_gpt_probability(text):
    score = 0
    total_checks = 7  # 체크 항목 수
    text_length = len(text)

    # 텍스트 길이에 따른 기준 설정
    length_threshold = 500  # 500자를 기준으로 설정
    length_factor = min(text_length / length_threshold, 1)  # 1을 초과하지 않도록 제한

    # 쉼표 개수 체크 (수정된 부분)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]  # 빈 문장 제거
    sentences_with_many_commas = [s for s in sentences if s.count(',') >= 2]
    if len(sentences_with_many_commas) > 0:  # 쉼표가 2개 이상인 문장이 하나라도 있으면
        score += 1

    # 한국어 접속사 체크
    korean_connectives = ['특히', '우선,', '입사 후,', '에서,', '이에 따라', '바탕으로', '저는', '고,', '이는', '통해']
    connective_count = sum(text.count(word) for word in korean_connectives)
    if connective_count > 2 * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 1

    # 긴 문장 체크
    if sentences:
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        if len(long_sentences) > len(sentences) * length_factor / 3:  # 텍스트 길이에 비례하여 조정
            score += 1


    # 부사 사용 체크
    adverb_count = sum(text.count(adverb) for adverb in ADVERBS)
    if adverb_count >= 2 * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 1

    # 명사 사용 체크
    noun_count = sum(text.count(noun) for noun in NOUNS)
    if noun_count >= 2 * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 1

    # 동사 사용 체크
    verb_count = sum(text.count(verb) for verb in VERBS)
    if verb_count >= 2 * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 1

    # 형용사 사용 체크
    adj_count = sum(text.count(adj) for adj in ADJECTIVES)
    if adj_count >= 2 * length_factor:  # 텍스트 길이에 비례하여 조정
        score += 1

    # 텍스트 길이에 따른 점수 조정
    normalized_score = score * (1 - 0.5 * length_factor)  # 텍스트가 길수록 점수를 약간 낮춤

    return (normalized_score / total_checks) * 100

def process_csv_file(input_file, output_file):
    # CSV 파일 읽기
    df = pd.read_csv(input_file)
    
    # 'answer' 열의 값을 입력으로 사용하여 GPT 확률 계산
    df['gpt_probability'] = df['answer'].apply(calculate_korean_gpt_probability)
    
    # 결과를 새로운 CSV 파일로 저장
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

# 파일 경로 설정
input_file = '/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/Generation_file/resume_generation.csv'
output_file = '/mnt/c/Users/kec91/Desktop/KuUpstage/phase1/demo_eunche/Generation_file/test.csv'

# 함수 실행
process_csv_file(input_file, output_file)