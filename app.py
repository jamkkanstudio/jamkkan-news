import streamlit as st

from services.news_service import load_news


st.set_page_config(
    page_title="잠깐.",
    page_icon="📰",
    layout="centered",
)

st.title("잠깐.")
st.caption("오늘 알아야 할 뉴스만")

news_list = load_news()

if not news_list:
    st.info("등록된 뉴스가 없습니다.")

else:
    sorted_news = sorted(
        news_list,
        key=lambda news: news.get("importance", 0),
        reverse=True,
    )

    for index, news in enumerate(sorted_news, start=1):
        st.subheader(f"{index}. {news['title']}")

        st.caption(
            f"{news['source']} · "
            f"{news.get('category', '기타')} · "
            f"중요도 {news.get('importance', 50)}"
        )

        st.write(news["summary"])

        st.markdown("**왜 중요할까?**")
        st.write(news["reason"])

        st.link_button(
            "원문 보기",
            news["url"],
        )

        st.divider()