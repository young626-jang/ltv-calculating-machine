import streamlit as st
import fitz
import re
from utils_deduction import get_deduction_ui
from utils_ltv import calculate_ltv, floor_to_unit
from utils_pdf import extract_address_area_floor_from_text, extract_owner_number_from_summary
from utils_pdfviewer import pdf_viewer_with_navigation
from utils_fees import calculate_fees, format_with_comma
from utils_css import inject_custom_css
from ltv_map import region_map

# Initialize
st.set_page_config(page_title="LTV 계산기", layout="wide")
inject_custom_css(st)

st.title("🏠 LTV 계산기 (주소+면적추출)")

# 세션 초기화
if "raw_price" not in st.session_state:
    st.session_state["raw_price"] = "0"

# 시세 입력 포맷팅
def parse_korean_number(text: str) -> int:
    txt = text.replace(",", "").strip()
    total = 0
    m = re.search(r"(\d+)\s*억", txt)
    if m:
        total += int(m.group(1)) * 10000
    m = re.search(r"(\d+)\s*천만", txt)
    if m:
        total += int(m.group(1)) * 1000
    m = re.search(r"(\d+)\s*만", txt)
    if m:
        total += int(m.group(1))
    if total == 0:
        try:
            total = int(txt)
        except:
            total = 0
    return total

def format_kb_price():
    raw = st.session_state.get("raw_price", "")
    clean = parse_korean_number(raw)
    if clean:
        st.session_state["raw_price"] = "{:,}".format(clean)
    else:
        st.session_state["raw_price"] = ""

def format_area():
    raw = st.session_state.get("area_input", "")
    clean = re.sub(r"[^\d.]", "", raw)
    if clean and not raw.endswith("㎡"):
        st.session_state["area_input"] = f"{clean}㎡"

# PDF Upload
uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])

if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with fitz.open(path) as doc:
        full_text = "".join(page.get_text() for page in doc)
        total_pages = doc.page_count

        extracted_address, extracted_area, floor_num = extract_address_area_floor_from_text(full_text)
        owner_number = extract_owner_number_from_summary(full_text)

        # 주소 및 시세 입력
        address_input = st.text_input("주소", extracted_address, key="address_input")
        col1, col2 = st.columns(2)
        raw_price_input = col1.text_input("KB 시세 (만원)", key="raw_price", on_change=format_kb_price)
        area_input = col2.text_input("전용면적 (㎡)", extracted_area, key="area_input", on_change=format_area)

        if floor_num is not None:
            st.markdown(f"<span style='color:red' if {floor_num}<=2 else 'color:#007BFF'; font-weight:bold; font-size:18px'>{'📉 하안가' if floor_num<=2 else '📈 일반가'}</span>", unsafe_allow_html=True)

        # PDF Viewer 호출 (모듈)
        pdf_viewer_with_navigation(st, path, total_pages)

        # 방공제 UI (모듈)
        deduction = get_deduction_ui(st)

        # LTV 비율 입력
        col1, col2 = st.columns(2)
        raw_ltv1 = col1.text_input("LTV 비율 ①", "80")
        raw_ltv2 = col2.text_input("LTV 비율 ②", "")
        ltv_selected = [int(val) for val in [raw_ltv1, raw_ltv2] if val.isdigit() and 1 <= int(val) <= 100]

        # 대출 항목 입력
        st.markdown("### 📝 대출 항목 입력")
        rows = st.number_input("항목 개수", min_value=1, max_value=10, value=3)
        items = []
        for i in range(int(rows)):
            cols = st.columns(5)
            lender = cols[0].text_input("설정자", key=f"lender_{i}")
            max_amt_key = f"maxamt_{i}"
            cols[1].text_input("채권최고액 (만)", key=max_amt_key, on_change=format_with_comma, args=(st, max_amt_key))
            ratio = cols[2].text_input("설정비율 (%)", "120", key=f"ratio_{i}")
            calc = int(re.sub(r"[^\d]", "", st.session_state.get(max_amt_key, "0")) or 0) * 100 // int(ratio or 100)
            principal_key = f"principal_{i}"
            cols[3].text_input("원금", key=principal_key, value=f"{calc:,}", on_change=format_with_comma, args=(st, principal_key))
            status = cols[4].selectbox("진행구분", ["유지", "대환", "선말소"], key=f"status_{i}")
            items.append({
                "설정자": lender,
                "채권최고액": st.session_state.get(max_amt_key, ""),
                "설정비율": ratio,
                "원금": st.session_state.get(principal_key, ""),
                "진행구분": status
            })

        # LTV 계산
        total_value = parse_korean_number(raw_price_input)
        senior_principal_sum = sum(
            int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
            for item in items if item.get("진행구분") in ["대환", "선말소"]
        )
        has_maintain = any(item["진행구분"] == "유지" for item in items)
        has_senior = any(item["진행구분"] in ["대환", "선말소"] for item in items)

        for ltv in ltv_selected:
            if has_senior and not has_maintain:
                limit_senior, avail_senior = calculate_ltv(total_value, deduction, senior_principal_sum, 0, ltv, is_senior=True)
                st.markdown(f"✅ 선순위 LTV {ltv}%: 대출가능 {floor_to_unit(limit_senior):,} | 가용 {floor_to_unit(avail_senior):,}")
            if has_maintain:
                maintain_maxamt_sum = sum(
                    int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
                    for item in items if item["진행구분"] == "유지"
                )
                limit_sub, avail_sub = calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=False)
                st.markdown(f"✅ 후순위 LTV {ltv}%: 대출가능 {floor_to_unit(limit_sub):,} | 가용 {floor_to_unit(avail_sub):,}")

        # 수수료 계산
        st.markdown("### 💰 수수료 계산")
        col1, col2 = st.columns(2)
        col1.text_input("총 대출금액 (만)", key="total_loan", on_change=format_with_comma, args=(st, "total_loan"))
        col2.text_input("브릿지 금액 (만)", key="bridge_amount", on_change=format_with_comma, args=(st, "bridge_amount"))
        consulting_rate = st.number_input("컨설팅 수수료율 (%)", value=1.5, step=0.1)
        bridge_rate = st.number_input("브릿지 수수료율 (%)", value=0.7, step=0.1)
        consulting_fee = calculate_fees(st.session_state.get("total_loan", ""), consulting_rate)
        bridge_fee = calculate_fees(st.session_state.get("bridge_amount", ""), bridge_rate)
        st.markdown(f"**컨설팅 비용:** {int(consulting_fee):,}만")
        st.markdown(f"**브릿지 비용:** {int(bridge_fee):,}만")
        st.markdown(f"🔗 **총 비용:** {int(consulting_fee + bridge_fee):,}만")

else:
    st.warning("PDF 파일을 업로드하세요.")
