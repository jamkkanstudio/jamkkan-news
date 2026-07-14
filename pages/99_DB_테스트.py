import streamlit as st

from services.news_service import sync_all_news_to_supabase
from services.supabase_service import get_supabase_client


st.set_page_config(
    page_title="DB 테스트 | 잠깐.",
    page_icon="🗄️",
    layout="centered",
)

st.title("Supabase 연결 테스트")

if st.button(
    "연결 확인",
    use_container_width=True,
):
    try:
        response = (
            get_supabase_client()
            .table("news")
            .select("id, title")
            .limit(5)
            .execute()
        )

        st.success("Supabase 연결에 성공했습니다.")
        st.write(response.data)

    except Exception as error:
        st.error(f"연결 실패: {error}")


st.divider()
st.subheader("JSON → Supabase 동기화")
st.caption("news.json의 기존 뉴스를 UUID 기준으로 추가하거나 갱신합니다.")

if st.button(
    "기존 뉴스 동기화",
    use_container_width=True,
):
    if sync_all_news_to_supabase():
        st.success("기존 뉴스 동기화가 완료되었습니다.")
    else:
        st.error("동기화에 실패했습니다. 서버 로그를 확인해 주세요.")
