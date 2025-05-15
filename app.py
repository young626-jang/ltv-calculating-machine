import streamlit as st
from ltv_app import run_ltv_app

# ✅ Streamlit 메인 실행 포인트
# - 모든 앱 UI, 로직, PDF 처리, 계산은 ltv_app.py 내부의 run_ltv_app() 함수에서 관리
# - 이 파일은 실행 진입점 역할만 담당

# ➡ Streamlit 페이지 설정 (제목, 레이아웃)
st.set_page_config(
    page_title="LTV 계산기 (최종)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ➡ ltv_app.py의 메인 앱 실행
run_ltv_app()
