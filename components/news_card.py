from html import escape

import streamlit as st

from components.design_system import CATEGORY_ICONS

from services.analytics_service import (
    record_article_read_event,
)
from services.growth_service import (
    is_read_today,
    record_article_read,
)


def render_news_card(
    news: dict,
    rank: int,
    personal_score: int | None = None,
    section: str = "today",
) -> None:
    """뉴스 한 건을 잠깐. 브리핑 카드로 표시합니다."""

    news_id = news.get("id", "")
    category = news.get("category", "기타")
    category_icon = CATEGORY_ICONS.get(category, "📰")
    title = news.get("title", "제목 없음")
    summary = news.get(
        "summary",
        "브리핑이 아직 작성되지 않았습니다.",
    )
    reason = news.get(
        "reason",
        "이 기사가 중요한 이유가 아직 작성되지 않았습니다.",
    )
    source = news.get("source", "출처 없음")
    url = news.get("url", "")

    with st.container(border=True):
        st.markdown(
            '<div class="jm-news-copy">'
            '<div class="jm-news-meta">'
            f'<span class="jm-rank">TOP {rank:02d}</span>'
            f'<span class="jm-category">{escape(category_icon)} '
            f'{escape(category)}</span>'
            "</div>"
            f"<h3>{escape(title)}</h3>"
            f"<p>{escape(summary)}</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        if personal_score is not None:
            st.markdown(
                '<div class="jm-personal-note">내 관심사를 반영했어요</div>',
                unsafe_allow_html=True,
            )

        with st.expander("30초 브리핑 열기"):
            st.markdown("**왜 중요할까?**")
            st.write(reason)

            st.caption(f"출처: {source}")

            if url:
                st.link_button(
                    "원문 보기 →",
                    url,
                    use_container_width=True,
                )

            if news_id:
                already_read = is_read_today(news_id)

                if already_read:
                    st.success("오늘 30초 투자 완료")

                else:
                    button_key = (
                        f"invest_{section}_{news_id}_{rank}"
                    )

                    if st.button(
                        "30초 투자 완료",
                        key=button_key,
                        use_container_width=True,
                    ):
                        recorded = record_article_read(
                            news_id=news_id,
                            seconds=30,
                        )

                        if recorded is not False:
                            record_article_read_event(
                                news_id=news_id,
                                category=category,
                                title=title,
                                seconds=30,
                            )

                            if recorded is True:
                                st.success(
                                    "30초를 나에게 투자했습니다."
                                )
                            else:
                                st.warning(
                                    "성장 기록은 JSON에 저장됐지만 "
                                    "Supabase 저장에 실패했습니다."
                                )
                            st.rerun()

                        else:
                            st.info(
                                "오늘 이미 투자 완료한 기사입니다."
                            )
