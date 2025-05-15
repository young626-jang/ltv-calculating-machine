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

    # ➡ 주소 + 시세 + 방공제 입력 (하나의 Expander 안)
    with st.expander("📂 주소 & 시세 입력", expanded=True):
        address_input = st.text_input("주소", value=extracted_address if uploaded_file else "", key="address_input")
        if st.button("🔎 KB 시세 조회"):
            st.components.v1.html(f"<script>window.open('https://kbland.kr/map?xy=37.5205559,126.9265729,17','_blank')</script>", height=0)

        col1, col2 = st.columns(2)
        raw_price_input = col1.text_input("KB 시세 (만원)", key="raw_price")
        area_input = col2.text_input("전용면적 (㎡)", value=extracted_area if uploaded_file else "", key="area_input")

        # 💡 방공제 입력 (안쪽으로 이동)
        deduction = get_deduction_ui(st)

    # ➡ 대출 항목 + LTV 계산
    with st.expander("💳 대출 항목 + LTV 계산", expanded=True):
        ltv_results, loan_items, sum_dh, sum_sm = handle_ltv_ui_and_calculation(st, raw_price_input, deduction)

    # ➡ 결과 내용 (값 없으면 자동 생략)
    with st.expander("📋 결과 내용", expanded=True):
        text_to_copy = ""

        if owner_number:
            text_to_copy += f"고객명: {owner_number}\n"
        if address_input:
            text_to_copy += f"주소: {address_input}\n"

        if raw_price_input or area_input or deduction > 0:
            type_of_price = "📉 하안가" if floor_num and floor_num <= 2 else "📈 일반가"
            text_to_copy += f"{type_of_price} |"
            if raw_price_input:
                text_to_copy += f" KB시세: {raw_price_input}만 |"
            if area_input:
                text_to_copy += f" 전용면적: {area_input} |"
            if deduction > 0:
                text_to_copy += f" 방공제 금액: {deduction:,}만"
            text_to_copy += "\n"

        if ltv_results:
            for res in ltv_results:
                text_to_copy += res + "\n"

        valid_loan_items = [item for item in loan_items if "|" in item and "0" not in item.split("|")[1].strip()]
        if valid_loan_items:
            text_to_copy += "\n📋 대출 항목\n"
            for item in valid_loan_items:
                text_to_copy += f"{item}\n"

        if sum_dh > 0 or sum_sm > 0:
            text_to_copy += "\n[진행구분별 원금 합계]\n"
            if sum_dh > 0:
                text_to_copy += f"대환: {sum_dh:,}만\n"
            if sum_sm > 0:
                text_to_copy += f"선말소: {sum_sm:,}만\n"

        st.text_area("", value=text_to_copy.strip(), height=400)

    # ➡ 수수료 계산 (앱 최하단)
    with st.expander("💰 수수료 계산", expanded=True):
        handle_fee_ui_and_calculation(st)

if __name__ == "__main__":
    run_ltv_app()
