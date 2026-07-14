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

        st.markdown("# 🌱")

        st.markdown("## 오늘 브리핑 완료")

        st.write(
            f"오늘 **{time_text}**를\n"
            "나에게 투자했습니다."
        )

        st.success("오늘도 조금 성장했습니다.")

        st.caption("좋은 하루 보내세요.")

        st.caption("내일 다시 잠깐.")