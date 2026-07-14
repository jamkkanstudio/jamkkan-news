import streamlit as st

from services.analytics_service import (
    get_article_read_events,
    get_category_statistics,
    get_current_week_daily_statistics,
    get_current_week_events,
)


CATEGORY_ICONS = {
    "경제": "📈",
    "정치": "🏛️",
    "사회": "👥",
    "국제": "🌍",
    "테크": "💻",
    "AI": "🤖",
    "반도체": "💾",
    "부동산": "🏠",
    "자동차": "🚗",
    "우주": "🚀",
    "미국주식": "🇺🇸",
    "기타": "📰",
}


def format_seconds(seconds: int) -> str:
    """초를 읽기 쉬운 시간으로 변환합니다."""
    if seconds < 60:
        return f"{seconds}초"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if remaining_seconds == 0:
        return f"{minutes}분"

    return f"{minutes}분 {remaining_seconds}초"


def get_personality_message(category: str) -> str:
    """가장 많이 읽은 분야에 따른 성향 문구를 반환합니다."""
    if category in ["경제", "미국주식", "부동산"]:
        return "📈 경제와 자산의 흐름에 관심이 많은 투자형입니다."

    if category in ["테크", "AI", "반도체"]:
        return "🤖 기술 변화와 미래 산업에 관심이 많은 기술형입니다."

    if category == "국제":
        return "🌍 세계의 흐름을 폭넓게 살펴보는 글로벌형입니다."

    if category == "정치":
        return "🏛️ 정책과 제도 변화에 관심이 많은 정책형입니다."

    if category == "사회":
        return "👥 사람과 일상의 변화에 관심이 많은 생활형입니다."

    return "🌱 다양한 분야를 탐색하며 성장하고 있습니다."


st.set_page_config(
    page_title="나의 분석 | 잠깐.",
    page_icon="📊",
    layout="centered",
)

st.title("📊 나의 분석")
st.caption("내가 어떤 분야에 시간을 투자했는지 확인합니다.")

all_events = get_article_read_events()
weekly_events = get_current_week_events()

period = st.radio(
    "분석 기간",
    options=["이번 주", "전체"],
    horizontal=True,
)

if period == "이번 주":
    selected_events = weekly_events
else:
    selected_events = all_events

statistics = get_category_statistics(selected_events)

if not selected_events or not statistics:
    st.info(f"{period}에 분석할 기록이 없습니다.")
    st.caption("기사에서 🌱 투자 완료를 누르면 기록이 쌓입니다.")

else:
    total_articles = len(selected_events)
    total_seconds = sum(
        int(event.get("seconds", 0))
        for event in selected_events
    )

    top_category = statistics[0]["category"]
    top_category_icon = CATEGORY_ICONS.get(
        top_category,
        "📰",
    )

    st.divider()
    st.subheader(f"{period} 투자 기록")

    article_col, time_col = st.columns(2)

    with article_col:
        st.metric(
            "읽은 기사",
            f"{total_articles}개",
        )

    with time_col:
        st.metric(
            "투자 시간",
            format_seconds(total_seconds),
        )

    with st.container(border=True):
        st.caption("가장 많이 읽은 분야")
        st.markdown(
            f"## {top_category_icon} {top_category}"
        )
        st.write(get_personality_message(top_category))

    if period == "이번 주":
        st.divider()
        st.subheader("이번 주 기록")

        daily_statistics = get_current_week_daily_statistics()
        day_columns = st.columns(7)

        for column, day_data in zip(
            day_columns,
            daily_statistics,
        ):
            with column:
                st.caption(day_data["day"])

                if day_data["articles"] > 0:
                    st.markdown("### 🌱")
                else:
                    st.markdown("### ○")

                st.caption(
                    format_seconds(day_data["seconds"])
                )

        chart_data = {
            item["day"]: item["seconds"]
            for item in daily_statistics
        }

        st.bar_chart(
            chart_data,
            horizontal=False,
        )

    st.divider()
    st.subheader("분야별 투자")

    for item in statistics:
        category = item["category"]
        articles = item["articles"]
        seconds = item["seconds"]
        icon = CATEGORY_ICONS.get(category, "📰")

        percentage = (
            seconds / total_seconds * 100
            if total_seconds > 0
            else 0
        )

        with st.container(border=True):
            st.markdown(f"### {icon} {category}")

            article_col, time_col = st.columns(2)

            with article_col:
                st.metric(
                    "읽은 기사",
                    f"{articles}개",
                )

            with time_col:
                st.metric(
                    "투자 시간",
                    format_seconds(seconds),
                )

            st.progress(min(percentage / 100, 1.0))
            st.caption(f"전체 투자 시간의 {percentage:.0f}%")

    st.divider()

    with st.container(border=True):
        st.markdown("### 오늘의 한마디")

        if period == "이번 주":
            st.write(
                f"이번 주에는 총 "
                f"**{format_seconds(total_seconds)}**를 "
                "나에게 투자했습니다."
            )
        else:
            st.write(
                f"지금까지 총 "
                f"**{format_seconds(total_seconds)}**를 "
                "나에게 투자했습니다."
            )

        st.success("잠깐의 시간이 차곡차곡 쌓이고 있습니다.")