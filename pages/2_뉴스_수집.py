import html
import re

import streamlit as st

from components.design_system import apply_design_system, render_page_intro
from services.auth_service import require_admin_page

from services.news_service import add_news, load_news
from services.news_collection_service import (
    format_collection_time_kst,
    is_collection_status_stale,
    load_collection_status,
)
from services.rss_service import (
    RSS_CATEGORIES,
    fetch_categorized_rss_news,
    fetch_rss_news,
)
from services.summarizer import create_brief, create_reason


st.set_page_config(
    page_title="뉴스 수집 | 잠깐.",
    page_icon="📰",
    layout="centered",
)

apply_design_system()
render_page_intro(
    "ADMIN · COLLECTION",
    "뉴스 수집",
    "자동 수집 상태를 확인하고, 필요할 때만 수동으로 복구합니다.",
)

require_admin_page()

registration_result = st.session_state.pop(
    "registration_result",
    None,
)

collection_status = load_collection_status()
if collection_status:
    last_attempt = format_collection_time_kst(
        collection_status.get("last_attempt_at")
    )
    last_success = format_collection_time_kst(
        collection_status.get("last_success_at")
    )
    if collection_status.get("status") == "success":
        if is_collection_status_stale(collection_status):
            st.warning("자동 수집 지연 확인 필요 · 마지막 성공 " + last_success)
        else:
            st.success("자동 수집 정상 · 마지막 성공 " + last_success)
        st.caption(
            f"최근 시도 {last_attempt} · "
            f"최근 추가 {collection_status.get('added_count', 0)}개 · "
            f"중복 제외 {collection_status.get('duplicate_count', 0)}개"
        )
    else:
        st.warning(
            "자동 수집 확인 필요 · 오류 코드 "
            + str(collection_status.get("failure_code", "unknown"))
        )
        st.caption(
            f"실패 시도 {last_attempt} · 마지막 성공 {last_success}. "
            "다음 예약 실행이 자동으로 재시도합니다. "
            "필요하면 아래 수동 복구를 사용하세요."
        )
else:
    st.info("자동 수집 실행 기록이 아직 없습니다.")

if registration_result:
    message_type, message = registration_result

    if message_type == "success":
        st.success(message)
    else:
        st.warning(message)


def clean_summary(summary: str) -> str:
    """RSS 요약에서 HTML 태그와 특수문자를 제거합니다."""
    if not summary:
        return ""

    text = re.sub(r"<[^>]+>", " ", summary)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


category = st.selectbox(
    "카테고리",
    options=["분류 통합", *RSS_CATEGORIES],
)

limit = st.slider(
    "가져올 기사 수",
    min_value=5,
    max_value=30,
    value=20,
    step=5,
)

if st.button(
    "복구용 기사 가져오기",
    use_container_width=True,
):
    try:
        with st.spinner("기사를 가져오는 중입니다..."):
            if category == "분류 통합":
                news_list = fetch_categorized_rss_news(limit=limit)
            else:
                news_list = fetch_rss_news(
                    category=category,
                    limit=limit,
                )

        st.session_state["rss_news_list"] = news_list
        st.success(f"{len(news_list)}개의 기사를 가져왔습니다.")

    except Exception:
        st.error("기사 수집에 실패했습니다. 잠시 후 다시 시도해 주세요.")


news_list = st.session_state.get("rss_news_list", [])

if news_list:
    st.divider()
    st.subheader("수집된 기사")
    st.caption("오늘의 뉴스로 등록할 기사를 최대 5개 선택하세요.")

    existing_news = load_news()
    existing_urls = {
        news.get("url")
        for news in existing_news
        if news.get("url")
    }

    with st.form("select_rss_news"):
        selected_indices = []

        for index, news in enumerate(news_list):
            already_registered = news["url"] in existing_urls

            with st.container(border=True):
                selected = st.checkbox(
                    news["title"],
                    key=f"select_{index}_{news['url']}",
                    disabled=already_registered,
                )

                st.caption(
                    f"{news['source']} · "
                    f"{news['category']} · "
                    f"{news['published_at']}"
                )

                cleaned_summary = clean_summary(
                    news.get("summary", "")
                )

                if cleaned_summary:
                    st.write(cleaned_summary)

                if already_registered:
                    st.info("이미 등록된 기사입니다.")

                st.link_button(
                    "원문 보기",
                    news["url"],
                )

                if selected:
                    selected_indices.append(index)

        submitted = st.form_submit_button(
            "선택한 기사 등록",
            use_container_width=True,
        )

    if submitted:
        if not selected_indices:
            st.warning("등록할 기사를 선택해 주세요.")

        elif len(selected_indices) > 5:
            st.error("기사는 최대 5개까지 선택할 수 있습니다.")

        else:
            added_count = 0
            mirrored_count = 0

            for index in selected_indices:
                rss_news = news_list[index]

                raw_summary = rss_news.get("summary", "")
                cleaned_summary = clean_summary(raw_summary)

                news_category = rss_news.get("category", "기타")

                brief = create_brief(
                    cleaned_summary or rss_news["title"]
                )

                reason = create_reason(
                    category=news_category,
                    title=rss_news["title"],
                )

                new_news = {
                    "title": rss_news["title"],
                    "summary": brief,
                    "reason": reason,
                    "source": rss_news["source"],
                    "url": rss_news["url"],
                    "category": news_category,
                    "importance": 50,
                    "published_at": rss_news.get("published_at", ""),
                    "collected_at": rss_news.get("collected_at", ""),
                }

                if add_news(new_news):
                    mirrored_count += 1

                added_count += 1

            if mirrored_count == added_count:
                registration_result = (
                    "success",
                    f"{added_count}개의 기사가 JSON과 Supabase에 "
                    "등록되었습니다.",
                )
            else:
                registration_result = (
                    "warning",
                    f"{added_count}개 기사는 JSON에 등록됐지만, "
                    f"Supabase에는 {mirrored_count}개만 저장됐습니다.",
                )

            st.session_state["registration_result"] = registration_result
            st.session_state.pop("rss_news_list", None)
            st.rerun()
