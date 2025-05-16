import streamlit as st
import fitz

from utils_pdf import extract_address_area_floor_from_text, extract_owner_number_from_summary
from utils_pdfviewer import pdf_viewer_with_navigation
from utils_deduction import get_deduction_ui
from utils_ltv import handle_ltv_ui_and_calculation
from utils_fees import handle_fee_ui_and_calculation

def inject_custom_css():
    st.markdown("""
        <style>
        html, body, .stApp {
            background-color: #C7D3D4 !important;
            color: #02343F !important;
            min-height: 100vh;
        }
        </style>
    """, unsafe_allow_html=True)

def format_ltv_results(price, sum_dh, sum_sm, owner_number, address, area, deduction, loan_items):
    try:
        price_int = int(price.replace(",", "").strip())
        선순위_가능 = int(price_int * 0.8) - sum_dh
        후순위_가능 = 선순위_가능 - sum_sm

        result_text = ""
        result_text += f"{owner_number}\n"
        result_text += f"{address} | {area} | {deduction:,}만\n\n"
        result_text += "[대출항목]\n"
        for item in loan_items:
            result_text += f"{item}\n"
        result_text += f"\n선순위 대출한도: {선순위_가능:,}만 (가용자금)\n"
        result_text += f"후순위 대출한도: {후순위_가능:,}만 (가용자금)\n\n"
        result_text += "[진행구분별 잔액]\n"
        result_text += f"선말소잔액: {sum_sm:,}만\n"
        result_text += f"대환잔액: {sum_dh:,}만\n"

        return result_text
    except:
        return "계산 오류"

def run_ltv_app():
    st.title("🏠 LTV 계산기 (주소+면적추출)")
    inject_custom_css()

    uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])

    extracted_address = ""
    extracted_area = ""
    floor_num = None
    owner_number = ""

    if uploaded_file:
        st.success(f"✅ 업로드 완료: {uploaded_file.name}")
        path = f"./{uploaded_file.name}"
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with fitz.open(path) as doc:
            full_text = "".join(page.get_text() for page in doc)
            total_pages = doc.page_count
            extracted_address, extracted_area, floor_num = extract_address_area_floor_from_text(full_text)
            owner_number = extract_owner_number_from_summary(full_text)

        st.markdown("### 👤 고객명 & 주민번호")
        st.info(owner_number)
        pdf_viewer_with_navigation(st, path, total_pages)

    with st.expander("📂 주소 & 시세 입력", expanded=True):
        address_input = st.text_input("주소", value=extracted_address if uploaded_file else "")
        raw_price_input = st.text_input("KB 시세 (만원)")
        area_input = st.text_input("전용면적 (㎡)", value=extracted_area if uploaded_file else "")
        deduction = get_deduction_ui(st)

    with st.expander("💳 대출 항목 + LTV 계산", expanded=True):
        loan_items, sum_dh, sum_sm = handle_ltv_ui_and_calculation(st, raw_price_input, deduction)

    with st.expander("📋 결과 내용", expanded=True):
        text_to_copy = ""
        if raw_price_input:
            text_to_copy = format_ltv_results(
                raw_price_input,
                sum_dh,
                sum_sm,
                owner_number,
                address_input,
                area_input,
                deduction,
                loan_items
            )
        st.text_area("", value=text_to_copy.strip(), height=400)

    with st.expander("💰 수수료 계산", expanded=True):
        handle_fee_ui_and_calculation(st)

if __name__ == "__main__":
    run_ltv_app()
