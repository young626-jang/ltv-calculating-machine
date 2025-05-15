import streamlit as st
import fitz
from utils_pdf import extract_address_area_floor_from_text, extract_owner_number_from_summary
from utils_pdfviewer import pdf_viewer_with_navigation
from utils_deduction import get_deduction_ui
from utils_ltv import handle_ltv_ui_and_calculation, parse_korean_number
from utils_fees import handle_fee_ui_and_calculation
from utils_css import inject_custom_css

def run_ltv_app():
    """💻 LTV 계산기 메인 앱 실행 함수"""
    inject_custom_css(st)
    st.title("🏠 LTV 계산기 (주소+면적추출)")

    # ✅ PDF 업로드
    uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])

    # ✅ 초기값 선언
    extracted_address = ""
    extracted_area = ""
    floor_num = None
    owner_number = ""

    if uploaded_file:
        # 파일 저장
        path = f"./{uploaded_file.name}"
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # PDF 파싱
        with fitz.open(path) as doc:
            full_text = "".join(page.get_text() for page in doc)
            total_pages = doc.page_count
            extracted_address, extracted_area, floor_num = extract_address_area_floor_from_text(full_text)
            owner_number = extract_owner_number_from_summary(full_text)

        # 고객명 & 주민번호
        st.markdown("### 👤 고객명 & 주민번호")
        st.info(owner_number)

        # PDF Viewer 표시
        pdf_viewer_with_navigation(st, path, total_pages)

    # ✅ 주소 & 시세 입력
    with st.expander("📂 주소 & 시세 입력 (접기)", expanded=True):
        address_input = st.text_input("주소", value=extracted_address, key="address_input")

        if st.button("🔎 KB 시세 조회"):
            url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"
            st.components.v1.html(f"<script>window.open('{url}','_blank')</script>", height=0)

        st.markdown("<div style='margin-top: 10px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        raw_price_input = col1.text_input("KB 시세 (만원)", key="raw_price")
        area_input = col2.text_input("전용면적 (㎡)", value=extracted_area, key="area_input")

    # ✅ 방공제 입력
    deduction = get_deduction_ui(st)

    # ✅ 대출 항목 + LTV 계산
    with st.expander("💳 대출 항목 + LTV 계산", expanded=True):
        ltv_results, loan_items, sum_dh, sum_sm = handle_ltv_ui_and_calculation(st, raw_price_input, deduction)

    # ✅ 메모 입력
    with st.expander("📝 메모 입력 (선택)", expanded=True):
        memo_text = st.text_area("메모 입력", height=150)

    # ✅ 수수료 계산
    with st.expander("💰 수수료 계산", expanded=True):
        consulting_fee, bridge_fee, total_fee = handle_fee_ui_and_calculation(st)

    # ✅ 결과 내용 자동 생성
    st.markdown("### 📋 결과 내용 (자동 생성)")
    text_to_copy = f"고객명: {owner_number}\n주소: {address_input}\n"
    type_of_price = "📉 하안가" if floor_num and floor_num <= 2 else "📈 일반가"
    text_to_copy += f"{type_of_price} | KB시세: {raw_price_input}만 | 전용면적: {area_input} | 방공제 금액: {deduction:,}만\n"

    for res in ltv_results:
        text_to_copy += res + "\n"

    if loan_items:
        text_to_copy += "\n📋 대출 항목\n"
        for item in loan_items:
            text_to_copy += f"{item}\n"

    text_to_copy += "\n[진행구분별 원금 합계]\n"
    if sum_dh > 0:
        text_to_copy += f"대환: {sum_dh:,}만\n"
    if sum_sm > 0:
        text_to_copy += f"선말소: {sum_sm:,}만\n"

    text_to_copy += f"\n컨설팅 수수료: {int(consulting_fee):,}만\n"
    text_to_copy += f"브릿지 수수료: {int(bridge_fee):,}만\n"
    text_to_copy += f"총 수수료: {int(total_fee):,}만\n"

    if memo_text:
        text_to_copy += f"\n[메모]\n{memo_text}"

    # ✅ 결과 복사 가능 영역 표시
    st.text_area("📋 결과 내용", value=text_to_copy, height=400)
