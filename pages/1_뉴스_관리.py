import streamlit as st

from services.news_service import (
    add_news,
    delete_news,
    load_news,
    update_news,
)


CATEGORY_OPTIONS = [
    "경제",
    "정치",
    "사회",
    "국제",
    "테크",
    "기타",
]


st.set_page_config(
    page_title="뉴스 관리 | 잠깐.",
    page_icon="✍️",
    layout="centered",
)

st.title("뉴스 관리")
st.caption("잠깐. 아침 브리핑에 표시할 기사를 관리합니다.")


# 뉴스 추가
st.subheader("뉴스 추가")

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

    category = st.selectbox(
        "카테고리",
        options=CATEGORY_OPTIONS,
    )

    importance = st.slider(
        "중요도",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
    )

    submitted = st.form_submit_button(
        "뉴스 추가",
        use_container_width=True,
    )


if submitted:
    required_fields = [
        title,
        summary,
        reason,
        source,
        url,
    ]

    if not all(field.strip() for field in required_fields):
        st.error("모든 항목을 입력해 주세요.")

    elif not url.startswith(("http://", "https://")):
        st.error("원문 주소는 http:// 또는 https://로 시작해야 합니다.")

    else:
        new_news = {
            "title": title.strip(),
            "summary": summary.strip(),
            "reason": reason.strip(),
            "source": source.strip(),
            "url": url.strip(),
            "category": category,
            "importance": importance,
        }

        add_news(new_news)
        st.success("뉴스가 추가되었습니다.")
        st.rerun()


# 등록된 뉴스
st.divider()
st.subheader("등록된 뉴스")

news_list = load_news()

if not news_list:
    st.info("등록된 뉴스가 없습니다.")

else:
    for index, news in enumerate(news_list):
        news_id = news["id"]
        current_category = news.get("category", "기타")

        if current_category not in CATEGORY_OPTIONS:
            current_category = "기타"

        with st.container(border=True):
            st.markdown(f"**{index + 1}. {news['title']}**")

            st.caption(
                f"{news['source']} · "
                f"{current_category} · "
                f"중요도 {news.get('importance', 50)}"
            )

            st.write(news["summary"])

            with st.expander("수정"):
                edit_title = st.text_input(
                    "기사 제목",
                    value=news["title"],
                    key=f"edit_title_{news_id}",
                )

                edit_summary = st.text_area(
                    "기사 요약",
                    value=news["summary"],
                    height=120,
                    key=f"edit_summary_{news_id}",
                )

                edit_reason = st.text_area(
                    "왜 중요할까?",
                    value=news["reason"],
                    height=100,
                    key=f"edit_reason_{news_id}",
                )

                edit_source = st.text_input(
                    "언론사",
                    value=news["source"],
                    key=f"edit_source_{news_id}",
                )

                edit_url = st.text_input(
                    "원문 주소",
                    value=news["url"],
                    key=f"edit_url_{news_id}",
                )

                edit_category = st.selectbox(
                    "카테고리",
                    options=CATEGORY_OPTIONS,
                    index=CATEGORY_OPTIONS.index(current_category),
                    key=f"edit_category_{news_id}",
                )

                edit_importance = st.slider(
                    "중요도",
                    min_value=0,
                    max_value=100,
                    value=int(news.get("importance", 50)),
                    step=5,
                    key=f"edit_importance_{news_id}",
                )

                if st.button(
                    "수정 내용 저장",
                    key=f"update_{news_id}",
                    use_container_width=True,
                ):
                    updated_data = {
                        "title": edit_title.strip(),
                        "summary": edit_summary.strip(),
                        "reason": edit_reason.strip(),
                        "source": edit_source.strip(),
                        "url": edit_url.strip(),
                        "category": edit_category,
                        "importance": edit_importance,
                    }

                    required_fields = [
                        updated_data["title"],
                        updated_data["summary"],
                        updated_data["reason"],
                        updated_data["source"],
                        updated_data["url"],
                    ]

                    if not all(required_fields):
                        st.error("모든 항목을 입력해 주세요.")

                    elif not updated_data["url"].startswith(
                        ("http://", "https://")
                    ):
                        st.error(
                            "원문 주소는 http:// 또는 https://로 시작해야 합니다."
                        )

                    else:
                        updated = update_news(
                            news_id,
                            updated_data,
                        )

                        if updated:
                            st.success("뉴스가 수정되었습니다.")
                            st.rerun()

                        else:
                            st.error("수정할 뉴스를 찾지 못했습니다.")

            if st.button(
                "삭제",
                key=f"delete_{news_id}",
                type="secondary",
                use_container_width=True,
            ):
                deleted = delete_news(news_id)

                if deleted:
                    st.success("뉴스가 삭제되었습니다.")
                    st.rerun()

                else:
                    st.error("삭제할 뉴스를 찾지 못했습니다.")