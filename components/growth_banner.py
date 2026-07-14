import streamlit as st

from services.growth_service import get_growth_summary


def _format_seconds(seconds: int) -> str:
    """초를 사람이 읽기 쉬운 형태로 변환합니다."""
    if seconds < 60:
        return f"{seconds}초"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if remaining_seconds == 0:
        return f"{minutes}분"

    return f"{minutes}분 {remaining_seconds}초"


def render_growth_banner() -> None:
    """메인 상단에 성장 기록을 표시합니다."""
    summary = get_growth_summary()

    today_articles = summary["today_articles"]
    today_seconds = summary["today_seconds"]
    total_articles = summary["total_articles"]
    total_seconds = summary["total_seconds"]
    current_streak = summary["current_streak"]

    with st.container(border=True):
        st.markdown("### 🌱 오늘도 성장 중")

        if current_streak > 0:
            st.caption(f"{current_streak}일째 이어가고 있습니다.")
        else:
            st.caption("오늘 첫 브리핑을 시작해 보세요.")

        today_col, total_col = st.columns(2)

        with today_col:
            st.markdown("**오늘**")
            st.metric(
                label="읽은 기사",
                value=f"{today_articles}개",
            )
            st.caption(
                f"나에게 투자한 시간 · "
                f"{_format_seconds(today_seconds)}"
            )

        with total_col:
            st.markdown("**누적**")
            st.metric(
                label="읽은 기사",
                value=f"{total_articles}개",
            )
            st.caption(
                f"나에게 투자한 시간 · "
                f"{_format_seconds(total_seconds)}"
            )