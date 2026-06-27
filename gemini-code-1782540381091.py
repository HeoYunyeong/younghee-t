import streamlit as st
import re

# --- 1. 데이터 사전 정의 ---
KEYWORDS_BASE = {
    "set1": {
        "easy_task": ["쉬운", "취미", "노력", "친숙", "좋아하는", "커피숍", "도서관", "모임", "함께", "촉진"],
        "hard_task": ["어려운", "복잡", "도전", "연습", "익숙", "차분", "혼자", "집중", "억제"]
    },
    "set2": {
        "static": ["고여", "멈춰", "정지", "머물러", "이동하지", "조용", "안전", "위험하지"],
        "dynamic": ["흐르는", "폭포", "움직이는", "이동함", "위험", "감전"]
    },
    "set3": {
        "human": ["인간", "선수", "노력", "열정", "경험", "철학", "관점", "감정", "울림", "감동"],
        "ai": ["인공지능", "로봇", "알고리즘", "데이터", "벨라미", "감정없음", "철학없음", "범주확장", "상징"]
    }
}

METHOD_PATTERNS = {
    "정의": {"keywords": ["란", "뜻한다", "말한다", "개념"], "structure": r"(란|은|는).*?(말한다|뜻한다)"},
    "예시": {"keywords": ["예를", "예컨대", "대표적", "예로는"], "structure": r"(예를|예컨대|대표적|예로는)"},
    "인과": {"keywords": ["때문에", "원인은", "결과", "하므로", "왜냐하면"], "structure": r"(때문에|원인|결과|하므로|왜냐하면)"},
    "분석": {"keywords": ["이루어", "구성", "부분", "요소"], "structure": r"(이루어|구성|부분|요소)"},
    "비교와 대조": {"keywords": ["반면", "달리", "차이", "공통", "같다", "다르다"], "structure": r"(반면|달리|차이|공통|같다|다르다)"},
    "분류와 구분": {"keywords": ["나뉘", "나누", "종류", "분류", "묶인", "구분"], "structure": r"(나뉘|나누|종류|분류|묶|구분)"}
}

# --- 2. 핵심 채점 함수 구현 ---
def check_keywords(text, keyword_list):
    normalized = text.replace(" ", "")
    return any(kw in normalized for kw in keyword_list)

def score_question_1(set_num, ans_a, ans_b, ans_c):
    results = {}
    
    if set_num == "1세트 (학습 전략)":
        # ㉠ 검증
        results["㉠"] = "통과 (만점)" if check_keywords(ans_a, KEYWORDS_BASE["set1"]["easy_task"]) else "오답 (쉬운 과제 특성 누락)"
        # ㉡ 검증
        results["㉡"] = "통과 (만점)" if check_keywords(ans_b, ["혼자", "차분", "집중"]) else "오답 (혼자 집중하는 환경 누락)"
        # ㉢ 검증
        results["㉢"] = "통과 (만점)" if "억제" in ans_c.replace(" ", "") and "촉진" not in ans_c else "오답 (정확한 심리학 용어 미기재)"
        
    elif set_num == "2세트 (정전기)":
        results["㉠"] = "통과 (만점)" if check_keywords(ans_a, ["고여", "멈춘", "저장"]) else "오답 (고여 있는 물 비유 누락)"
        results["㉡"] = "통과 (만점)" if check_keywords(ans_b, ["이동하지", "멈춘", "정지", "머물"]) else "오답 (전하의 정지 상태 누락)"
        results["㉢"] = "통과 (만점)" if check_keywords(ans_c, ["위험하지", "안전", "피해가없"]) else "오답 (위험성 오판)"
        
    elif set_num == "3세트 (AI 예술)":
        results["㉠"] = "통과 (만점)" if check_keywords(ans_a, ["로봇", "피겨", "완벽"]) else "오답 (로봇 비유 누락)"
        results["㉡"] = "통과 (만점)" if check_keywords(ans_b, ["어렵", "아니다", "불가"]) and check_keywords(ans_b, ["감정", "철학", "이야기"]) else "오답 (예술 불가 근거 부족)"
        results["㉢"] = "통과 (만점)" if check_keywords(ans_c, ["확장", "변화", "상징"]) else "오답 (예술적 가치 인식 부족)"
        
    return results

def score_question_2(set_num, text_1, text_2):
    # 괄호 안 설명 방법 추출
    method_1 = re.findall(r"\((.*?)\)", text_1)
    method_2 = re.findall(r"\((.*?)\)", text_2)
    
    if not method_1 or not method_2:
        return "오답 (조건 위반: 문장 끝 괄호 안에 설명 방법 명칭 누락)"
    
    m1, m2 = method_1[-1].strip(), method_2[-1].strip()
    
    if m1 == m2:
        return f"오답 (조건 위반: 동일한 설명 방법 [{m1}] 중복 사용 불가)"
    
    if m1 not in METHOD_PATTERNS or m2 not in METHOD_PATTERNS:
        return "오답 (지정된 6종 설명 방법 외의 명칭 기재)"
        
    # 오개념 및 문장 구조 이중 필터링
    for m, text in [(m1, text_1), (m2, text_2)]:
        # 구조 체크
        if not re.search(METHOD_PATTERNS[m]["structure"], text):
            return f"오답 (괄호 명칭 [{m}]과 실제 문장 서술 구조 불일치)"
            
        # 본문 키워드 매칭 (오개념 방지 포함)
        if set_num == "1세트 (학습 전략)":
            if not (check_keywords(text, KEYWORDS_BASE["set1"]["easy_task"]) or check_keywords(text, KEYWORDS_BASE["set1"]["hard_task"])):
                return "오답 (본문에 제시된 내용 외의 외부 지식 사용)"
    
    return "통과 (만점: 중복 없음, 구조 및 결론 방향 일치)"

def score_question_3(set_num, scene, effect):
    if not scene or not effect:
        return "오답 (연출 계획 또는 효과 누락)"
        
    # 오개념 차단 및 본문 근거 체크
    if set_num == "1세트 (학습 전략)":
        if check_keywords(scene, ["시끄러운", "카페", "친구와함께"]): 
            return "오답 (오개념: 어려운 과제 상황에 맞지 않는 산만한 환경 연출)"
        if not check_keywords(effect, ["어려운", "도전", "억제"]):
            return "오답 (조건 미충족: 효과 기술 시 본문 상황 근거 누락)"
            
    elif set_num == "2세트 (정전기)":
        if check_keywords(scene, ["폭포", "흐르는", "움직이는"]):
            return "오답 (오개념: 정전기의 특성과 반대되는 역동적 연출)"
        if not check_keywords(effect, ["고여", "이동하지", "위험하지"]):
            return "오답 (조건 미충족: 효과 기술 시 본문 과학적 근거 누락)"
            
    elif set_num == "3세트 (AI 예술)":
        if check_keywords(scene, ["컴퓨터", "알고리즘", "차가운"]):
            return "오답 (오개념: 인간 예술의 특성 장면에 AI 연출 활용)"
        if not check_keywords(effect, ["감정", "철학", "경험", "울림", "감동"]):
            return "오답 (조건 미충족: 효과 기술 시 본문 고유 특성 근거 누락)"
            
    return "통과 (만점: 개념 반영, 인과 연결, 본문 근거 완비)"


# --- 3. Streamlit UI 구성 ---
st.set_page_index = "채점 프로그램"
st.title("📝 2회고사 대비 국어 서논술형 자동 채점 시스템")
st.caption("설명 방법 중복 확인 / 명칭-구조 일치 검증 / 오개념 차단 / 본문 근거 매칭")

set_option = st.selectbox("🎯 채점할 모의 문항 세트를 선택하세요", ["1세트 (학습 전략)", "2세트 (정전기)", "3세트 (AI 예술)"])

# 세트별 모범 답안 미리보기 가이드 제공
with st.expander("💡 선택한 세트의 채점 가이드 및 모범 답안 보기"):
    if set_option == "1세트 (학습 전략)":
        st.markdown("**[문항 1]** ㉠ 쉬운 과제 (유사어 인정) / ㉡ 혼자 차분히 집중함 / ㉢ 사회적 억제 (정확해야 함)")
        st.markdown("**[문항 2]** (1) 예를 들어 쉬운 과제는~ (예시) (2) 반면 어려운 과제는~ (비교와 대조) *중복 불허*")
        st.markdown("**[문항 3]** 시각/청각에 '혼자/차분함'이 드러나야 하며 효과에 '어려운 과제이므로 효율이 떨어짐' 등 본문 근거 필수.")
    elif set_option == "2세트 (정전기)":
        st.markdown("**[문항 1]** ㉠ 높은 곳에 고여 있는 물 / ㉡ 전하가 머물러 있음 / ㉢ 위험하지 않음")
        st.markdown("**[문항 2]** (1) 정전기란~ (정의) (2) 실생활 전기와 달리~ (비교와 대조)")
    elif set_option == "3세트 (AI 예술)":
        st.markdown("**[문항 1]** ㉠ 완벽하지만 울림이 없는 로봇 피겨 경기 / ㉡ 감정과 철학이 없어 예술이 아님 / ㉢ 범주 확장 및 상징 가치")

st.divider()

# --- 문항 입력 폼 ---
st.subheader("1️⃣ [서논술형 1] 요약 표 빈칸 채우기")
col1, col2, col3 = st.columns(3)
with col1: ans_a = st.text_input("㉠ 답안 입력")
with col2: ans_b = st.text_input("㉡ 답안 입력")
with col3: ans_c = st.text_input("㉢ 답안 입력")

st.subheader("2️⃣ [서논술형 2] 조건 지정 설명문 작성")
text_1 = st.text_input("(1)번 문장 작성 (문말에 괄호 명칭 포함 필수)", placeholder="예: 예를 들어 쉬운 과제는 공부 모임이 좋습니다. (예시)")
text_2 = st.text_input("(2)번 문장 작성 (문말에 괄호 명칭 포함 필수)", placeholder="예: 반면 지나치게 어려운 과제는 효율이 떨어집니다. (비교와 대조)")

st.subheader("3️⃣ [서논술형 3] 영상 기획안 및 효과 서술")
visual_scene = st.text_area("장면 2 시각/청각 연출 계획 입력 (Ⓐ 또는 Ⓑ)", placeholder="예: 학생이 아무도 없는 방에서 차분하게 혼자 문제집을 푸는 모습을 풀샷으로 보여준다.")
visual_effect = st.text_area("설정한 요소의 연출 효과 입력 (본문 근거 필수)", placeholder="예: 본문에서 어려운 과제는 타인의 시선이 있으면 효율이 떨어진다고 했으므로 혼자 집중하는 환경의 필요성을 시청자에게 효과적으로 전달한다.")

st.divider()

# --- 채점 프로세스 가동 ---
if st.button("🚀 즉시 자동 채점 실행"):
    st.header("📊 채점 결과 리포트")
    
    # 문항 1 결과
    st.write("**[서논술형 1] 결과:**")
    res1 = score_question_1(set_option, ans_a, ans_b, ans_c)
    for k, v in res1.items():
        if "통과" in v: st.success(f"{k}: {v}")
        else: st.error(f"{k}: {v}")
        
    st.write("---")
    
    # 문항 2 결과
    st.write("**[서논술형 2] 결과:**")
    res2 = score_question_2(set_option, text_1, text_2)
    if "통과" in res2: st.success(res2)
    else: st.error(res2)
        
    st.write("---")
    
    # 문항 3 결과
    st.write("**[서논술형 3] 결과:**")
    res3 = score_question_3(set_option, visual_scene, visual_effect)
    if "통과" in res3: st.success(res3)
    else: st.error(res3)