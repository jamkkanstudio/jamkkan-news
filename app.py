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
from services.ranking_service import (
    calculate_personal_score,
    filter_news_for_date,
    select_personal_top_news,
    select_today_top_news,
)
from services.settings_service import load_global_daily_briefing
from services.time_service import now_kst, today_kst
from services.user_service import load_interests


st.set_page_config(
    page_title="잠깐.",
    page_icon="🌱",
    layout="centered",
)

apply_design_system()
render_auth_sidebar()


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
today = today_kst()
current_time = now_kst()
today_candidates = filter_news_for_date(news_list, today)
daily_snapshot = load_global_daily_briefing(today.isoformat())

if daily_snapshot:
    today_by_id = {
        str(news.get("id", "")): news
        for news in today_candidates
        if news.get("id")
    }
    candidate_pool = [
        today_by_id[news_id]
        for news_id in daily_snapshot["candidate_ids"]
        if news_id in today_by_id
    ]
else:
    candidate_pool = today_candidates


if not candidate_pool:
    st.info("오늘 발행된 브리핑 기사가 아직 없습니다.")

    st.caption(
        "오래된 기사를 오늘 기사로 섞지 않고, 새 소식을 기다립니다."
    )

else:
    today_top5 = select_today_top_news(
        candidate_pool,
        target_date=today,
        now=current_time,
    )
    personal_top5 = select_personal_top_news(
        candidate_pool,
        interests,
        target_date=today,
        now=current_time,
    )

    brief_completed = bool(daily_snapshot) and (
        is_today_brief_completed(today_top5)
        or (
            personal_top5
            and is_today_brief_completed(personal_top5)
        )
    )

    if brief_completed:
        render_completion_banner()

    render_section_header(
        "오늘의 브리핑",
        "두 관점 중 하나를 골라 최대 5개의 서로 다른 흐름만 확인하세요.",
    )
    view = st.segmented_control(
        "브리핑 관점",
        options=["모두에게 중요", "나에게 중요"],
        default="모두에게 중요",
    )

    if not daily_snapshot:
        st.caption("오늘 후보군을 고정하는 중이며, 현재도 오늘 기사만 보여드립니다.")

    if view == "나에게 중요" and interests:
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
    elif view == "나에게 중요":
        st.info("관심 분야를 먼저 설정해 주세요.")
        if st.button(
            "관심 분야 설정하기",
            use_container_width=True,
            type="primary",
        ):
            st.switch_page("pages/3_관심분야_설정.py")
    else:
        if len(today_top5) < 5:
            st.caption(
                f"오늘 발행 기사 {len(today_top5)}개만 보여드립니다. "
                "어제 기사는 섞지 않습니다."
            )
        render_topic_strip(today_top5)
        render_news_grid(today_top5, section="today")
