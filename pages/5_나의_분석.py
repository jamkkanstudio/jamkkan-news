import streamlit as st

from services.analytics_service import (
    get_category_statistics,
    load_events,
)


def format_seconds(seconds: int) -> str:
    """초를 읽기 쉬운 시간으로 변환합니다."""
    if seconds < 60:
        return f"{seconds}초"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if remaining_seconds == 0:
        return f"{minutes}분"

    return f"{minutes}분 {remaining_seconds}초"


st.set_page_config(
    page_title="나의 분석 | 잠깐.",
    page_icon="📊",
    layout="centered",
)

st.title("📊 나의 분석")
st.caption("내가 어떤 분야에 시간을 투자했는지 확인합니다.")

events = load_events()
statistics = get_category_statistics()

if not events or not statistics:
    st.info("아직 분석할 기록이 없습니다.")
    st.caption("기사에서 🌱 투자 완료를 누르면 기록이 쌓입니다.")

else:
    total_articles = sum(
        item["articles"]
        for item in statistics
    )

    total_seconds = sum(
        item["seconds"]
        for item in statistics
    )

    top_category = statistics[0]["category"]

    st.subheader("나의 투자 기록")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "읽은 기사",
            f"{total_articles}개",
        )

    with col2:
        st.metric(
            "투자 시간",
            format_seconds(total_seconds),
        )

    with st.container(border=True):
        st.markdown("### 가장 많이 읽은 분야")
        st.markdown(f"## {top_category}")
        st.caption(
            "지금까지 가장 많은 시간을 투자한 분야입니다."
        )

    st.divider()
    st.subheader("분야별 투자 시간")

    max_seconds = max(
        item["seconds"]
        for item in statistics
    )

    for item in statistics:
        category = item["category"]
        articles = item["articles"]
        seconds = item["seconds"]

        progress = (
            seconds / max_seconds
            if max_seconds > 0
            else 0
        )

        with st.container(border=True):
            st.markdown(f"### {category}")

            article_col, time_col = st.columns(2)

            with article_col:
                st.metric(
                    "기사",
                    f"{articles}개",
                )

            with time_col:
                st.metric(
                    "투자 시간",
                    format_seconds(seconds),
                )

            st.progress(progress)

    st.divider()

    with st.container(border=True):
        st.markdown("### 나의 성향")

        if top_category == "경제":
            st.write("📈 경제 흐름에 관심이 많은 투자형입니다.")

        elif top_category in ["테크", "AI", "반도체"]:
            st.write("🤖 기술 변화에 관심이 많은 기술형입니다.")

        elif top_category == "국제":
            st.write("🌍 세계의 흐름에 관심이 많은 글로벌형입니다.")

        elif top_category == "정치":
            st.write("🏛️ 정책과 사회 변화에 관심이 많은 정책형입니다.")

        elif top_category == "사회":
            st.write("👥 사람과 일상에 관심이 많은 생활형입니다.")

        else:
            st.write("🌱 다양한 분야를 탐색하고 있습니다.")