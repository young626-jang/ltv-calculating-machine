import streamlit as st
from ltv_app import run_ltv_app

# ✅ 반드시 가장 위에 선언 (딱 여기만!)
st.set_page_config(page_title="LTV 계산기", layout="wide")

# ✔ 앱 실행
run_ltv_app()
