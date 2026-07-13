import json
import streamlit as st

st.set_page_config(
    page_title="잠깐.",
    page_icon="📰",
    layout="centered",
)

st.title("잠깐.")
st.caption("오늘 알아야 할 뉴스만")

with open("data/news.json", "r", encoding="utf-8") as file:
    news_list = json.load(file)

for index, news in enumerate(news_list, start=1):
    st.subheader(f"{index}. {news['title']}")
    st.write(news["summary"])

    st.markdown("**왜 중요할까?**")
    st.write(news["reason"])

    st.caption(news["source"])
    st.link_button("원문 보기", news["url"])

    st.divider()