import streamlit as st

from services.growth_service import (
    get_growth_summary,
)


def render_completion_banner():

    summary = get_growth_summary()

    minutes = summary["today_seconds"] // 60
    seconds = summary["today_seconds"] % 60

    if minutes:
        time_text = f"{minutes}분 {seconds}초"
    else:
        time_text = f"{seconds}초"

    with st.container(border=True):
        st.markdown(
            '<p class="jm-kicker">DAILY COMPLETE</p>'
            "<h2>🌱 오늘은 충분합니다.</h2>"
            f"<p>오늘 <strong>{time_text}</strong>를 나에게 투자했습니다.</p>",
            unsafe_allow_html=True,
        )
        st.success("브리핑 완료 · 내일 다시 잠깐.")
