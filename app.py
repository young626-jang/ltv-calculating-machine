import streamlit as st
from ltv_app import run_ltv_app

# ✅ Streamlit 페이지 설정은 여기서만 허용 (첫 명령)
st.set_page_config(
    page_title="LTV 계산기 (최종)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 💻 메인 앱 실행
run_ltv_app()
