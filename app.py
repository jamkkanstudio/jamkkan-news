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

from services.analytics_service import get_today_helpful_news_ids
from services.growth_service import (
    get_today_read_news_ids,
    is_today_brief_completed,
)
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
    read_news_ids: set[str] | None = None,
    helpful_news_ids: set[str] | None = None,
    rank_prefix: str = "TOP",
) -> None:
    """뉴스를 데스크톱 2열, 모바일 1열 카드로 표시합니다."""
    read_news_ids = read_news_ids or set()
    helpful_news_ids = helpful_news_ids or set()
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
                    already_read=str(news.get("id", "")) in read_news_ids,
                    already_helpful=(
                        str(news.get("id", "")) in helpful_news_ids
                    ),
                    rank_prefix=rank_prefix,
                )


def get_briefing_batch(
    target_date: str,
    section: str,
    initial_items: list[dict],
    candidate_by_id: dict[str, dict],
) -> tuple[str, dict, list[dict]]:
    """세션 안에서 현재 묶음과 이미 표시한 기사 ID를 관리합니다."""
    state_key = f"briefing_batch_{target_date}_{section}"
    initial_ids = [
        str(news.get("id", ""))
        for news in initial_items
        if news.get("id")
    ]
    state = st.session_state.get(state_key)
    if not isinstance(state, dict):
        state = {
            "current_ids": initial_ids,
            "displayed_ids": initial_ids,
            "batch_number": 0,
        }
        st.session_state[state_key] = state

    current_items = [
        candidate_by_id[news_id]
        for news_id in state.get("current_ids", [])
        if news_id in candidate_by_id
    ]
    return state_key, state, current_items


def render_more_news_control(
    state_key: str,
    state: dict,
    next_items: list[dict],
) -> None:
    """사용자가 원할 때만 현재 묶음을 다음 새 기사로 교체합니다."""
    if not next_items:
        st.caption(
            "오늘 새 기사는 여기까지예요. "
            "오래된 기사·같은 소식은 섞지 않았어요."
        )
        return

    count = len(next_items)
    if st.button(
        f"새 기사 {count}개",
        key=f"more_news_{state_key}",
        use_container_width=True,
        type="primary",
    ):
        next_ids = [str(news["id"]) for news in next_items]
        displayed_ids = list(
            dict.fromkeys(state.get("displayed_ids", []) + next_ids)
        )
        st.session_state[state_key] = {
            "current_ids": next_ids,
            "displayed_ids": displayed_ids,
            "batch_number": int(state.get("batch_number", 0)) + 1,
        }
        st.rerun()


render_page_intro(
    "DAILY BRIEF · 30 SEC",
    "잠깐.",
    "오늘의 흐름을 30초로.",
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
    candidate_by_id = {
        str(news.get("id", "")): news
        for news in candidate_pool
        if news.get("id")
    }
    read_news_ids = get_today_read_news_ids()
    helpful_news_ids = get_today_helpful_news_ids()

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
        "TOP 5부터, 원할 때만 다음 5개.",
    )
    view = st.segmented_control(
        "브리핑 관점",
        options=["오늘의 TOP", "추천"],
        default="오늘의 TOP",
    )

    if not daily_snapshot:
        st.caption("오늘 후보군을 고정하는 중이며, 현재도 오늘 기사만 보여드립니다.")

    if view == "추천" and interests:
        st.caption(
            "관심 분야 · "
            + ", ".join(interests)
        )
        state_key, batch_state, visible_news = get_briefing_batch(
            today.isoformat(),
            "personal",
            personal_top5,
            candidate_by_id,
        )
        render_topic_strip(visible_news)
        render_news_grid(
            visible_news,
            section="personal",
            interests=interests,
            read_news_ids=read_news_ids,
            helpful_news_ids=helpful_news_ids,
            rank_prefix=(
                "TOP" if batch_state.get("batch_number", 0) == 0 else "NEW"
            ),
        )
        excluded_ids = set(batch_state.get("displayed_ids", []))
        excluded_ids.update(read_news_ids)
        next_items = select_personal_top_news(
            candidate_pool,
            interests,
            target_date=today,
            now=current_time,
            excluded_ids=excluded_ids,
        )
        render_more_news_control(
            state_key,
            batch_state,
            next_items,
        )
        if st.button(
            "관심사 변경",
            use_container_width=True,
        ):
            st.switch_page(
                "pages/3_관심분야_설정.py"
            )
    elif view == "추천":
        st.info("관심사를 먼저 설정해 주세요.")
        if st.button(
            "관심사 설정",
            use_container_width=True,
            type="primary",
        ):
            st.switch_page("pages/3_관심분야_설정.py")
    else:
        state_key, batch_state, visible_news = get_briefing_batch(
            today.isoformat(),
            "today",
            today_top5,
            candidate_by_id,
        )
        render_topic_strip(visible_news)
        render_news_grid(
            visible_news,
            section="today",
            read_news_ids=read_news_ids,
            helpful_news_ids=helpful_news_ids,
            rank_prefix=(
                "TOP" if batch_state.get("batch_number", 0) == 0 else "NEW"
            ),
        )
        excluded_ids = set(batch_state.get("displayed_ids", []))
        excluded_ids.update(read_news_ids)
        next_items = select_today_top_news(
            candidate_pool,
            target_date=today,
            now=current_time,
            excluded_ids=excluded_ids,
        )
        render_more_news_control(
            state_key,
            batch_state,
            next_items,
        )
