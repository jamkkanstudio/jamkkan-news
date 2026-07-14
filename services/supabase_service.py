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
        logger.exception("Supabase 뉴스 저장에 실패했습니다: %s", news.get("id"))
        return False


def delete_news(news_id: str) -> bool:
    """Supabase에서 뉴스 한 건을 삭제합니다."""
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
        logger.exception("Supabase 뉴스 삭제에 실패했습니다: %s", news_id)
        return False


def sync_news(news_list: list[dict]) -> bool:
    """JSON 뉴스 전체를 UUID 기준으로 Supabase에 동기화합니다."""
    if not news_list:
        return True

    try:
        get_supabase_client().table("news").upsert(news_list).execute()
        return True
    except Exception:
        logger.exception("Supabase 뉴스 전체 동기화에 실패했습니다.")
        return False
