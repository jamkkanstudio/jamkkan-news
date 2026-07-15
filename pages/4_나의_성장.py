import random
from datetime import date

import streamlit as st

from components.design_system import (
    apply_design_system,
    render_page_intro,
    render_section_header,
    render_stat_grid,
    render_week_strip,
)
from services.auth_service import render_auth_sidebar

from services.growth_service import load_growth
from services.time_service import current_week_dates, today_kst


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


st.set_page_config(
    page_title="나의 성장 | 잠깐.",
    page_icon="🌱",
    layout="centered",
)

apply_design_system()
render_auth_sidebar()
render_page_intro(
    "GROWTH RECORD",
    "나의 성장",
    "매일의 30초가 얼마나 쌓였는지 가볍게 확인해 보세요.",
)

growth = load_growth()
today_string = today_kst().isoformat()

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

render_stat_grid(
    [
        {
            "label": "오늘 읽은 기사",
            "value": f"{today_data.get('articles', 0)}개",
            "detail": format_seconds(today_data.get("seconds", 0)),
        },
        {
            "label": "누적 읽은 기사",
            "value": f"{total_articles}개",
            "detail": format_seconds(total_seconds),
        },
    ]
)

render_section_header(
    "이번 주",
    "하루 한 번의 작은 투자가 이어진 날을 보여줍니다.",
)

week_dates = current_week_dates()

day_names = ["월", "화", "수", "목", "금", "토", "일"]
week_days = []

for day_name, day_date in zip(
    day_names,
    week_dates,
):
    day_string = day_date.isoformat()
    day_data = daily.get(day_string, {})
    articles = day_data.get("articles", 0)

    week_days.append(
        {
            "label": day_name,
            "active": articles > 0,
            "value": f"{articles}개",
        }
    )

render_week_strip(week_days)

message = random.choice(MESSAGES)

with st.container(border=True):
    st.markdown("### 오늘의 기록")
    st.write(message)

    if today_data.get("articles", 0) > 0:
        st.success("오늘도 나에게 시간을 투자했습니다.")
    else:
        st.info("오늘의 첫 브리핑이 기다리고 있습니다.")
