import streamlit as st

from services.news_service import load_news
from services.user_service import load_interests


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


def render_news_card(
    news: dict,
    rank: int,
    personal_score: int | None = None,
) -> None:
    """뉴스 한 개를 카드 형태로 표시합니다."""
    with st.container(border=True):
        st.markdown(f"### {rank}. {news['title']}")

        caption_parts = [
            news.get("source", "출처 없음"),
            news.get("category", "기타"),
            f"중요도 {news.get('importance', 50)}",
        ]

        if personal_score is not None:
            caption_parts.append(f"관심 점수 {personal_score}")

        st.caption(" · ".join(caption_parts))

        st.write(news.get("summary", ""))

        st.markdown("**왜 중요할까?**")
        st.write(
            news.get(
                "reason",
                "중요한 이유가 아직 작성되지 않았습니다.",
            )
        )

        if news.get("url"):
            st.link_button(
                "원문 보기",
                news["url"],
                use_container_width=True,
            )


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
    today_top5 = sorted(
        news_list,
        key=lambda news: int(news.get("importance", 0)),
        reverse=True,
    )[:5]

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