import streamlit as st


CATEGORY_ICONS = {
    "경제": "📈",
    "정치": "🏛️",
    "사회": "👥",
    "국제": "🌍",
    "테크": "🤖",
    "AI": "🤖",
    "반도체": "💾",
    "부동산": "🏠",
    "자동차": "🚗",
    "기타": "📰",
}

RANK_ICONS = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
    4: "4",
    5: "5",
}


def render_news_card(
    news: dict,
    rank: int,
    personal_score: int | None = None,
) -> None:
    """뉴스 한 건을 잠깐. 브리핑 카드로 표시합니다."""

    category = news.get("category", "기타")
    category_icon = CATEGORY_ICONS.get(category, "📰")
    rank_icon = RANK_ICONS.get(rank, str(rank))

    title = news.get("title", "제목 없음")
    summary = news.get("summary", "브리핑이 아직 작성되지 않았습니다.")
    reason = news.get(
        "reason",
        "이 기사가 중요한 이유가 아직 작성되지 않았습니다.",
    )
    source = news.get("source", "출처 없음")
    url = news.get("url", "")

    with st.container(border=True):
        st.caption(f"{category_icon} {category}")

        st.markdown(f"### {rank_icon} {title}")

        st.markdown(
            f"""
            **{summary}**
            """
        )

        if personal_score is not None:
            st.caption("내 관심사를 반영한 기사입니다.")

        with st.expander("브리핑 보기"):
            st.markdown("**왜 중요할까?**")
            st.write(reason)

            st.caption(f"출처: {source}")

            if url:
                st.link_button(
                    "더 알아보기 →",
                    url,
                    use_container_width=True,
                )