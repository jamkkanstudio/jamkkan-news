import streamlit as st

from services.growth_service import get_growth_summary
from services.settings_service import get_daily_goal_seconds


def _format_seconds(seconds: int) -> str:
    """초를 읽기 쉬운 시간으로 변환합니다."""
    if seconds < 60:
        return f"{seconds}초"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if remaining_seconds == 0:
        return f"{minutes}분"

    return f"{minutes}분 {remaining_seconds}초"


def render_growth_banner() -> None:
    """메인 상단에 오늘의 성장 기록과 목표를 표시합니다."""
    summary = get_growth_summary()

    today_articles = summary["today_articles"]
    today_seconds = summary["today_seconds"]
    total_articles = summary["total_articles"]
    total_seconds = summary["total_seconds"]
    current_streak = summary["current_streak"]

    daily_goal_seconds = get_daily_goal_seconds()

    progress = min(
        today_seconds / daily_goal_seconds,
        1.0,
    )

    remaining_seconds = max(
        daily_goal_seconds - today_seconds,
        0,
    )

    with st.container(border=True):
        st.markdown("### 🌱 오늘도 성장 중")

        if current_streak > 0:
            st.caption(
                f"{current_streak}일째 이어가고 있습니다."
            )
        else:
            st.caption("오늘 첫 브리핑을 시작해 보세요.")

        st.markdown(
            f"**오늘의 목표 · "
            f"{_format_seconds(daily_goal_seconds)}**"
        )

        st.progress(progress)

        if today_seconds >= daily_goal_seconds:
            st.success(
                "오늘의 목표를 달성했습니다. "
                "오늘은 여기까지면 충분합니다."
            )
        else:
            st.caption(
                f"앞으로 {_format_seconds(remaining_seconds)}"
            )

        today_col, total_col = st.columns(2)

        with today_col:
            st.markdown("**오늘**")
            st.metric(
                label="읽은 기사",
                value=f"{today_articles}개",
            )
            st.caption(
                "나에게 투자한 시간 · "
                f"{_format_seconds(today_seconds)}"
            )

        with total_col:
            st.markdown("**누적**")
            st.metric(
                label="읽은 기사",
                value=f"{total_articles}개",
            )
            st.caption(
                "나에게 투자한 시간 · "
                f"{_format_seconds(total_seconds)}"
            )