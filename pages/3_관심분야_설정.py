import streamlit as st

from components.design_system import (
    apply_design_system,
    render_page_intro,
    render_section_header,
)
from services.auth_service import (
    is_logged_in,
    render_auth_sidebar,
    require_admin_page,
)
from services.data_routing_service import is_user_data_enabled

from services.settings_service import (
    get_daily_goal_seconds,
    save_daily_goal_seconds,
)
from services.user_service import (
    load_interests,
    save_interests,
)


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

GOAL_OPTIONS = {
    "30초": 30,
    "1분": 60,
    "2분": 120,
    "3분": 180,
    "5분": 300,
}


st.set_page_config(
    page_title="설정 | 잠깐.",
    page_icon="⚙️",
    layout="centered",
)

apply_design_system()
render_page_intro(
    "PERSONAL SETUP",
    "관심 분야와 하루 목표",
    "보고 싶은 주제를 고르고, 오늘 나에게 투자할 시간을 정해보세요.",
)

user_data_enabled = is_user_data_enabled()
personal_mode = user_data_enabled and is_logged_in()
if personal_mode:
    render_auth_sidebar()
elif user_data_enabled:
    render_auth_sidebar()
    st.info("개인 설정을 저장하려면 사이드바에서 Google로 로그인해 주세요.")
    st.stop()
else:
    require_admin_page()
current_interests = load_interests()
current_goal_seconds = get_daily_goal_seconds()

render_section_header(
    "관심 분야",
    "나의 TOP5에 반영할 분야를 최대 5개까지 선택하세요.",
)

selected_interests = st.multiselect(
    "분야 선택",
    options=INTEREST_OPTIONS,
    default=[
        interest
        for interest in current_interests
        if interest in INTEREST_OPTIONS
    ],
    max_selections=5,
)

render_section_header(
    "오늘의 목표",
    "부담 없이 매일 이어갈 수 있는 시간을 선택하세요.",
)

goal_labels = list(GOAL_OPTIONS.keys())
current_goal_label = next(
    (
        label
        for label, seconds in GOAL_OPTIONS.items()
        if seconds == current_goal_seconds
    ),
    "3분",
)

selected_goal_label = st.radio(
    "목표 시간",
    options=goal_labels,
    index=goal_labels.index(current_goal_label),
    horizontal=True,
)

if st.button(
    "관심 분야와 목표 저장",
    use_container_width=True,
    type="primary",
):
    interests_mirrored = save_interests(selected_interests)
    goal_mirrored = save_daily_goal_seconds(
        GOAL_OPTIONS[selected_goal_label]
    )

    mirrored_items = interests_mirrored + goal_mirrored

    if mirrored_items == 2:
        if personal_mode:
            st.success("관심 분야와 목표 시간이 개인 저장소에 저장되었습니다.")
        else:
            st.success("관심 분야와 목표 시간이 JSON과 Supabase에 저장되었습니다.")
    else:
        st.warning(
            "설정은 JSON에 저장됐지만 Supabase에는 "
            f"{mirrored_items}/2개 항목만 저장됐습니다. "
            "서버 로그를 확인해 주세요."
        )
