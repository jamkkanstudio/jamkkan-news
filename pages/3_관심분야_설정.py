import streamlit as st

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

personal_mode = is_user_data_enabled() and is_logged_in()
if personal_mode:
    render_auth_sidebar()
else:
    require_admin_page()

st.title("설정")
st.caption("나에게 맞는 잠깐의 시간을 설정합니다.")

current_interests = load_interests()
current_goal_seconds = get_daily_goal_seconds()

st.subheader("관심 분야")

selected_interests = st.multiselect(
    "나의 TOP5에 반영할 분야",
    options=INTEREST_OPTIONS,
    default=[
        interest
        for interest in current_interests
        if interest in INTEREST_OPTIONS
    ],
    max_selections=5,
)

st.divider()
st.subheader("오늘의 목표")
st.caption("하루에 나에게 투자할 시간을 선택하세요.")

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
    "설정 저장",
    use_container_width=True,
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
