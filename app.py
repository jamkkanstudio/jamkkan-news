import streamlit as st

from services.news_service import load_news
from services.user_service import load_interests
from services.ranking_service import sort_news_by_importance

from components.news_card import render_news_card


st.set_page_config(
    page_title="잠깐.",
    page_icon="📰",
    layout="centered",
)


def calculate_personal_score(news: dict, interests: list[str]) -> int:
    """뉴스 중요도에 관심 분야 일치 점수를 더합니다."""
    score = int(news.get("importance", 50))

    title = news.get("title", "").lower()
    summary = news.get("summary", "").lower()
    category = news.get("category", "").lower()

    searchable_text = f"{title} {summary} {category}"

    for interest in interests:
        if interest.lower() in searchable_text:
            score += 30

    return score


st.title("잠깐.")
st.markdown(
    """
    ### 30초면,  
    오늘을 놓치지 않습니다.
    """
)

st.divider()

news_list = load_news()
interests = load_interests()

if not news_list:
    st.info("등록된 뉴스가 없습니다.")

else:
    today_top5 = sort_news_by_importance(news_list)[:5]

    st.subheader("🌍 오늘의 TOP5")
    st.caption("오늘 모두가 알아야 할 뉴스")

    for rank, news in enumerate(today_top5, start=1):
        render_news_card(
            news=news,
            rank=rank,
        )

    st.divider()

    st.subheader("👤 나의 TOP5")
    st.caption("내 관심사를 반영한 뉴스")

    if not interests:
        st.info("관심 분야를 먼저 설정해 주세요.")

        if st.button(
            "관심 분야 설정하기",
            use_container_width=True,
        ):
            st.switch_page("pages/3_관심분야_설정.py")

    else:
        personal_ranked_news = sorted(
            news_list,
            key=lambda news: calculate_personal_score(
                news,
                interests,
            ),
            reverse=True,
        )[:5]

        st.caption(
            "관심 분야: "
            + ", ".join(interests)
        )

        for rank, news in enumerate(
            personal_ranked_news,
            start=1,
        ):
            personal_score = calculate_personal_score(
                news,
                interests,
            )

            render_news_card(
                news=news,
                rank=rank,
                personal_score=personal_score,
            )

        if st.button(
            "관심 분야 변경",
            use_container_width=True,
        ):
            st.switch_page("pages/3_관심분야_설정.py")