import streamlit as st

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
