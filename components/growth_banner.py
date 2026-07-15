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
    """메인 상단에 오늘의 진행 상황을 짧게 표시합니다."""
    summary = get_growth_summary()

    today_articles = summary["today_articles"]
    today_seconds = summary["today_seconds"]
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
        streak_text = (
            f"{current_streak}일째 이어가는 중"
            if current_streak > 0
            else "오늘 첫 브리핑을 시작해 보세요"
        )
        st.markdown(
            '<div class="jm-growth-head">'
            "<strong>🌱 오늘의 성장</strong>"
            f"<span>{streak_text}</span>"
            "</div>"
            '<p class="jm-growth-summary">'
            f"오늘 {today_articles}개 · {_format_seconds(today_seconds)} 투자 · "
            f"목표 {_format_seconds(daily_goal_seconds)}"
            "</p>",
            unsafe_allow_html=True,
        )

        st.progress(progress)

        if today_seconds >= daily_goal_seconds:
            st.success(
                "오늘의 목표를 달성했습니다. "
                "오늘은 여기까지면 충분합니다."
            )
        else:
            st.caption(
                f"목표까지 {_format_seconds(remaining_seconds)} 남았습니다."
            )
