import random
from datetime import date, timedelta

import streamlit as st

from services.growth_service import load_growth


MESSAGES = [
    "오늘도 조금 성장했습니다.",
    "30초의 투자가 차곡차곡 쌓이고 있습니다.",
    "천천히, 하지만 꾸준히.",
    "좋은 습관은 작은 반복에서 시작됩니다.",
]


def format_seconds(seconds: int) -> str:
    """초를 읽기 쉬운 시간 형식으로 변환합니다."""
    if seconds < 60:
        return f"{seconds}초"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if remaining_seconds == 0:
        return f"{minutes}분"

    return f"{minutes}분 {remaining_seconds}초"


def get_week_dates() -> list[date]:
    """이번 주 월요일부터 일요일까지 날짜를 반환합니다."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    return [
        monday + timedelta(days=offset)
        for offset in range(7)
    ]


st.set_page_config(
    page_title="나의 성장 | 잠깐.",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 나의 성장")
st.caption("매일 잠깐의 투자가 쌓이고 있습니다.")

growth = load_growth()
today_string = date.today().isoformat()

daily = growth.get("daily", {})
today_data = daily.get(
    today_string,
    {
        "articles": 0,
        "seconds": 0,
    },
)

current_streak = growth.get("current_streak", 0)
total_articles = growth.get("total_articles", 0)
total_seconds = growth.get("total_seconds", 0)

with st.container(border=True):
    if current_streak > 0:
        st.markdown(f"### 🌱 {current_streak}일째 성장 중")
    else:
        st.markdown("### 🌱 오늘 첫 브리핑을 시작해 보세요.")

st.divider()

today_col, total_col = st.columns(2)

with today_col:
    st.markdown("### 오늘")
    st.metric(
        "읽은 기사",
        f"{today_data.get('articles', 0)}개",
    )
    st.caption(
        "나에게 투자한 시간 · "
        f"{format_seconds(today_data.get('seconds', 0))}"
    )

with total_col:
    st.markdown("### 누적")
    st.metric(
        "읽은 기사",
        f"{total_articles}개",
    )
    st.caption(
        "나에게 투자한 시간 · "
        f"{format_seconds(total_seconds)}"
    )

st.divider()
st.subheader("이번 주")

week_dates = get_week_dates()
week_columns = st.columns(7)

day_names = ["월", "화", "수", "목", "금", "토", "일"]

for column, day_name, day_date in zip(
    week_columns,
    day_names,
    week_dates,
):
    day_string = day_date.isoformat()
    day_data = daily.get(day_string, {})
    articles = day_data.get("articles", 0)

    with column:
        st.caption(day_name)

        if articles > 0:
            st.markdown("### 🌱")
        else:
            st.markdown("### ○")

        st.caption(f"{articles}개")

st.divider()

message = random.choice(MESSAGES)

with st.container(border=True):
    st.markdown("### 오늘의 기록")
    st.write(message)

    if today_data.get("articles", 0) > 0:
        st.success("오늘도 나에게 시간을 투자했습니다.")
    else:
        st.info("오늘의 첫 브리핑이 기다리고 있습니다.")