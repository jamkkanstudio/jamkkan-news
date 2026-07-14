import streamlit as st

from services.user_service import load_interests, save_interests


INTEREST_OPTIONS = [
    "경제",
    "미국주식",
    "AI",
    "반도체",
    "IT",
    "스타트업",
    "부동산",
    "자동차",
    "우주",
    "정치",
    "국제",
    "사회",
]


st.set_page_config(
    page_title="관심 분야 설정 | 잠깐.",
    page_icon="⚙️",
    layout="centered",
)

st.title("관심 분야 설정")
st.caption("나의 TOP5에 반영할 관심 분야를 최대 5개까지 선택하세요.")

current_interests = load_interests()

selected_interests = st.multiselect(
    "관심 분야",
    options=INTEREST_OPTIONS,
    default=[
        interest
        for interest in current_interests
        if interest in INTEREST_OPTIONS
    ],
    max_selections=5,
)

if st.button(
    "관심 분야 저장",
    use_container_width=True,
):
    save_interests(selected_interests)
    st.success("관심 분야가 저장되었습니다.")