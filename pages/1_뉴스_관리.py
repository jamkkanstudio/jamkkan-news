import json
from pathlib import Path

import streamlit as st


DATA_FILE = Path("data/news.json")


def load_news() -> list[dict]:
    """news.json에서 기사 목록을 불러옵니다."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_news(news_list: list[dict]) -> None:
    """기사 목록을 news.json에 저장합니다."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            news_list,
            file,
            ensure_ascii=False,
            indent=2,
        )


st.set_page_config(
    page_title="뉴스 관리 | 잠깐.",
    page_icon="✍️",
    layout="centered",
)

st.title("뉴스 관리")
st.caption("잠깐. 아침 브리핑에 표시할 기사를 추가합니다.")

with st.form("news_form", clear_on_submit=True):
    title = st.text_input(
        "기사 제목",
        placeholder="예: 한국은행, 기준금리 동결",
    )

    summary = st.text_area(
        "기사 요약",
        placeholder="핵심 내용을 2~3문장으로 작성하세요.",
        height=120,
    )

    reason = st.text_area(
        "왜 중요할까?",
        placeholder="이 기사가 중요한 이유를 한 문장으로 작성하세요.",
        height=100,
    )

    source = st.text_input(
        "언론사",
        placeholder="예: 연합뉴스",
    )

    url = st.text_input(
        "원문 주소",
        placeholder="https://...",
    )

    submitted = st.form_submit_button(
        "뉴스 추가",
        use_container_width=True,
    )

if submitted:
    required_fields = [title, summary, reason, source, url]

    if not all(field.strip() for field in required_fields):
        st.error("모든 항목을 입력해 주세요.")

    elif not url.startswith(("http://", "https://")):
        st.error("원문 주소는 http:// 또는 https://로 시작해야 합니다.")

    else:
        news_list = load_news()

        new_news = {
            "title": title.strip(),
            "summary": summary.strip(),
            "reason": reason.strip(),
            "source": source.strip(),
            "url": url.strip(),
        }

        news_list.append(new_news)
        save_news(news_list)

        st.success("뉴스가 추가되었습니다.")