import logging

import streamlit as st
from supabase import Client, create_client


logger = logging.getLogger(__name__)


@st.cache_resource
def get_supabase_client() -> Client:
    """Supabase 클라이언트를 생성하고 재사용합니다."""
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

    return create_client(
        supabase_url,
        supabase_key,
    )


def upsert_news(news: dict) -> bool:
    """뉴스 한 건을 Supabase에 추가하거나 갱신합니다."""
    try:
        get_supabase_client().table("news").upsert(news).execute()
        return True
    except Exception:
        logger.exception(
            "Supabase 뉴스 저장에 실패했습니다: %s",
            news.get("id"),
        )
        return False


def delete_news(news_id: str) -> bool:
    """Supabase에서 id가 일치하는 뉴스 한 건을 삭제합니다."""
    try:
        (
            get_supabase_client()
            .table("news")
            .delete()
            .eq("id", news_id)
            .execute()
        )
        return True
    except Exception:
        logger.exception(
            "Supabase 뉴스 삭제에 실패했습니다: %s",
            news_id,
        )
        return False


def replace_interests(interests: list[str]) -> bool:
    """Supabase 관심 분야 목록을 새 목록으로 교체합니다."""
    try:
        table = get_supabase_client().table("interests")
        table.delete().neq("id", 0).execute()

        if interests:
            table.insert(
                [{"interest": interest} for interest in interests]
            ).execute()

        return True
    except Exception:
        logger.exception("Supabase 관심 분야 저장에 실패했습니다.")
        return False


def upsert_setting(setting_key: str, setting_value: object) -> bool:
    """Supabase에 설정 한 건을 추가하거나 갱신합니다."""
    try:
        get_supabase_client().table("settings").upsert(
            {
                "setting_key": setting_key,
                "setting_value": setting_value,
            }
        ).execute()
        return True
    except Exception:
        logger.exception(
            "Supabase 설정 저장에 실패했습니다: %s",
            setting_key,
        )
        return False


def upsert_growth_daily(growth_day: dict) -> bool:
    """Supabase에 일별 성장 기록을 추가하거나 갱신합니다."""
    try:
        get_supabase_client().table("growth_daily").upsert(
            growth_day
        ).execute()
        return True
    except Exception:
        logger.exception(
            "Supabase 일별 성장 기록 저장에 실패했습니다: %s",
            growth_day.get("activity_date"),
        )
        return False
