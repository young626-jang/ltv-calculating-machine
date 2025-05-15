import streamlit as st
import fitz
from utils_pdf import extract_address_area_floor_from_text, extract_owner_number_from_summary
from utils_pdfviewer import pdf_viewer_with_navigation
from utils_deduction import get_deduction_ui
from utils_ltv import handle_ltv_ui_and_calculation
from utils_fees import handle_fee_ui_and_calculation
from utils_css import inject_custom_css

st.set_page_config(page_title="LTV 계산기", layout="wide")
inject_custom_css(st)

st.title("🏠 LTV 계산기 (주소+면적추출)")

# 📂 주소 & 시세 입력 (항상 표시)
with st.expander("📂 주소 & 시세 입력 (접기)", expanded=True):
    address_input = st.text_input("주소", key="address_input")
    if st.button("🔎 KB 시세 조회"):
        url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"
        st.components.v1.html(f"<script>window.open('{url}','_blank')</script>", height=0)
    col1, col2 = st.columns(2)
    raw_price_input = col1.text_input("KB 시세 (만원)", key="raw_price")
    area_input = col2.text_input("전용면적 (㎡)", key="area_input")

# ✅ 방공제 입력
deduction = get_deduction_ui(st)

# ✅ LTV UI + 계산
handle_ltv_ui_and_calculation(st, raw_price_input, deduction)

# ✅ 수수료 계산
handle_fee_ui_and_calculation(st)

# ✅ PDF 업로드 시 Viewer만 표시
uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])
if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with fitz.open(path) as doc:
        full_text = "".join(page.get_text() for page in doc)
        total_pages = doc.page_count

        # PDF Viewer 호출
        pdf_viewer_with_navigation(st, path, total_pages)
