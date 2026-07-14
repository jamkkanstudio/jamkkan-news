import streamlit as st

from services.rss_service import RSS_FEEDS, fetch_rss_news


st.set_page_config(
    page_title="뉴스 수집 | 잠깐.",
    page_icon="📰",
    layout="centered",
)

st.title("뉴스 수집")
st.caption("RSS에서 최신 기사 후보를 가져옵니다.")

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

    for index, news in enumerate(news_list, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {news['title']}**")

            st.caption(
                f"{news['source']} · "
                f"{news['category']} · "
                f"{news['published_at']}"
            )

            if news.get("summary"):
                st.write(news["summary"])

            st.link_button(
                "원문 보기",
                news["url"],
            )