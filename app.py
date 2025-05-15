import streamlit as st
import fitz
from utils_pdfviewer import pdf_viewer_with_navigation
from utils_deduction import get_deduction_ui
from utils_ltv import handle_ltv_ui_and_calculation
from utils_fees import handle_fee_ui_and_calculation
from utils_pdf import extract_address_area_floor_from_text
from utils_css import inject_custom_css

st.set_page_config(page_title="LTV 계산기", layout="wide")
inject_custom_css(st)

st.title("🏠 LTV 계산기 (주소+면적추출)")

# ✅ PDF 업로드는 항상 최상단
uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])

# ✅ PDF 파싱 결과 초기값 항상 선언 (초기 깡통 값)
extracted_address = ""
extracted_area = ""
floor_num = None

# ✅ PDF 업로드 후 → 실제 값 업데이트
if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with fitz.open(path) as doc:
        full_text = "".join(page.get_text() for page in doc)
        total_pages = doc.page_count
        extracted_address, extracted_area, floor_num = extract_address_area_floor_from_text(full_text)

    # PDF Viewer 항상 하단에 표시
    pdf_viewer_with_navigation(st, path, total_pages)

# ✅ 주소 & 시세 입력 (PDF 업로드와 무관하게 항상 표시)
with st.expander("📂 주소 & 시세 입력 (접기)", expanded=True):
    address_input = st.text_input("주소", value=extracted_address, key="address_input")

    if st.button("🔎 KB 시세 조회"):
        url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"
        st.components.v1.html(f"<script>window.open('{url}','_blank')</script>", height=0)

    # 버튼과 입력 필드 사이 여백 추가로 UX 안정
    st.markdown("<div style='margin-top: 10px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    raw_price_input = col1.text_input("KB 시세 (만원)", key="raw_price")
    area_input = col2.text_input("전용면적 (㎡)", value=extracted_area, key="area_input")

# ✅ 방공제 입력 (항상)
deduction = get_deduction_ui(st)

# ✅ LTV 입력 + 계산 (항상)
with st.expander("💳 대출 항목 + LTV 계산", expanded=True):
    handle_ltv_ui_and_calculation(st, raw_price_input, deduction)

# ✅ 수수료 입력 + 계산 (항상)
with st.expander("💰 수수료 계산", expanded=True):
    handle_fee_ui_and_calculation(st)
