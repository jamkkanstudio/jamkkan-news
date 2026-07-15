import streamlit as st

from services.auth_service import render_auth_sidebar

from components.completion_banner import render_completion_banner
from components.design_system import (
    apply_design_system,
    render_page_intro,
    render_section_header,
    render_topic_strip,
)
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

apply_design_system()
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


def render_news_grid(
    news_items: list[dict],
    section: str,
    interests: list[str] | None = None,
) -> None:
    """뉴스를 데스크톱 2열, 모바일 1열 카드로 표시합니다."""
    for row_start in range(0, len(news_items), 2):
        columns = st.columns(2, gap="medium")
        row_items = news_items[row_start : row_start + 2]

        for offset, news in enumerate(row_items):
            rank = row_start + offset + 1
            personal_score = None
            if interests is not None:
                personal_score = calculate_personal_score(news, interests)

            with columns[offset]:
                render_news_card(
                    news=news,
                    rank=rank,
                    personal_score=personal_score,
                    section=section,
                )


render_page_intro(
    "DAILY BRIEF · 30 SEC",
    "잠깐.",
    "오늘 꼭 알아야 할 흐름을 한눈에 보고, 필요한 기사만 30초로 읽어보세요.",
)

render_growth_banner()


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
        render_section_header(
            "오늘 읽은 브리핑",
            "필요한 내용을 빠르게 다시 확인할 수 있습니다.",
        )

    else:
        render_section_header(
            "오늘의 TOP5",
            "제목과 주제를 훑고, 궁금한 브리핑만 열어보세요.",
        )

    render_topic_strip(today_top5)
    render_news_grid(today_top5, section="today")

    # 나의 TOP5
    render_section_header(
        "나의 TOP5",
        "관심 분야를 반영해 다시 정렬한 브리핑입니다.",
    )

    if not interests:
        st.info("관심 분야를 먼저 설정해 주세요.")

        if st.button(
            "관심 분야 설정하기",
            use_container_width=True,
            type="primary",
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

        render_topic_strip(personal_top5)
        render_news_grid(
            personal_top5,
            section="personal",
            interests=interests,
        )

        if st.button(
            "관심 분야 변경",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/3_관심분야_설정.py"
            )
