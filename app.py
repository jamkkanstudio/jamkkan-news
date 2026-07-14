import streamlit as st

from services.auth_service import render_auth_sidebar

from components.completion_banner import render_completion_banner
from components.growth_banner import render_growth_banner
from components.news_card import render_news_card

from services.growth_service import is_today_brief_completed
from services.news_service import load_news
from services.ranking_service import sort_news_by_importance
from services.user_service import load_interests


st.set_page_config(
    page_title="잠깐.",
    page_icon="🌱",
    layout="centered",
)

render_auth_sidebar()


def calculate_personal_score(
    news: dict,
    interests: list[str],
) -> int:
    """기본 중요도에 관심 분야 일치 점수를 더합니다."""

    score = int(news.get("importance", 50))

    searchable_text = " ".join(
        [
            news.get("title", ""),
            news.get("summary", ""),
            news.get("reason", ""),
            news.get("category", ""),
        ]
    ).lower()

    for interest in interests:
        if interest.lower() in searchable_text:
            score += 30

    return score


def get_personal_top5(
    news_list: list[dict],
    interests: list[str],
) -> list[dict]:
    """관심 분야 점수를 기준으로 나의 TOP5를 반환합니다."""

    if not interests:
        return []

    return sorted(
        news_list,
        key=lambda news: calculate_personal_score(
            news,
            interests,
        ),
        reverse=True,
    )[:5]


# 상단 브랜드 영역
st.title("잠깐.")

st.markdown(
    """
    ### 30초면,  
    오늘을 놓치지 않습니다.
    """
)

render_growth_banner()

st.divider()


# 데이터 불러오기
news_list = load_news()
interests = load_interests()


if not news_list:
    st.info("등록된 뉴스가 없습니다.")

    st.caption(
        "뉴스 수집 페이지에서 오늘의 브리핑을 등록해 주세요."
    )

else:
    # 오늘의 TOP5
    ranked_news = sort_news_by_importance(news_list)
    today_top5 = ranked_news[:5]

    brief_completed = is_today_brief_completed(today_top5)

    if brief_completed:
        render_completion_banner()

        st.divider()
        st.subheader("🌍 오늘 읽은 브리핑")
        st.caption("필요한 내용을 다시 확인할 수 있습니다.")

    else:
        st.subheader("🌍 오늘의 TOP5")
        st.caption("오늘 모두가 알아야 할 뉴스")

    for rank, news in enumerate(
        today_top5,
        start=1,
    ):
        render_news_card(
            news=news,
            rank=rank,
            section="today",
        )

    st.divider()

    # 나의 TOP5
    st.subheader("👤 나의 TOP5")
    st.caption("내 관심사를 반영한 뉴스")

    if not interests:
        st.info("관심 분야를 먼저 설정해 주세요.")

        if st.button(
            "관심 분야 설정하기",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/3_관심분야_설정.py"
            )

    else:
        personal_top5 = get_personal_top5(
            news_list,
            interests,
        )

        st.caption(
            "관심 분야 · "
            + ", ".join(interests)
        )

        for rank, news in enumerate(
            personal_top5,
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
                section="personal",
            )

        if st.button(
            "관심 분야 변경",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/3_관심분야_설정.py"
            )
