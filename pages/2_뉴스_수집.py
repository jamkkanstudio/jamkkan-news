import html
import re

import streamlit as st

from services.news_service import add_news, load_news
from services.rss_service import RSS_FEEDS, fetch_rss_news
from services.summarizer import create_brief, create_reason


st.set_page_config(
    page_title="뉴스 수집 | 잠깐.",
    page_icon="📰",
    layout="centered",
)

st.title("뉴스 수집")
st.caption("RSS에서 기사 후보를 가져와 오늘의 뉴스로 등록합니다.")

registration_result = st.session_state.pop(
    "registration_result",
    None,
)

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
    options=list(RSS_FEEDS.keys()),
)

limit = st.slider(
    "가져올 기사 수",
    min_value=5,
    max_value=30,
    value=20,
    step=5,
)

if st.button(
    "기사 가져오기",
    use_container_width=True,
):
    try:
        with st.spinner("기사를 가져오는 중입니다..."):
            news_list = fetch_rss_news(
                category=category,
                limit=limit,
            )

        st.session_state["rss_news_list"] = news_list
        st.success(f"{len(news_list)}개의 기사를 가져왔습니다.")

    except Exception as error:
        st.error(f"기사 수집에 실패했습니다: {error}")


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

                if news_category == "최신":
                    news_category = "기타"

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
