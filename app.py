import streamlit as st
import fitz  # PyMuPDF
import re
from ltv_map import region_map  # ✅ 외부 ltv_map.py에서 region_map 가져오기
from utils_css import inject_custom_css
from utils_pdfviewer import pdf_viewer_with_navigation

# PDF Viewer 호출 위치에서:
pdf_viewer_with_navigation(st, path, total_pages)

# 앱 시작 부분 (st.set_page_config 바로 아래)
inject_custom_css(st)

# ✅ 세션 초기값 선언
def init_session():
    if "raw_price" not in st.session_state:
        st.session_state["raw_price"] = "0"
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0
    if "total_loan" not in st.session_state:
        st.session_state["total_loan"] = ""
    if "bridge_amount" not in st.session_state:
        st.session_state["bridge_amount"] = ""

# ✅ 숫자 문자열을 한글 단위 포함 파싱
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

# ✅ 입력값 포맷 함수들
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

def format_with_comma(key):
    raw = st.session_state.get(key, "")
    clean = re.sub(r"[^\d]", "", raw)
    if clean.isdigit():
        st.session_state[key] = "{:,}".format(int(clean))
    else:
        st.session_state[key] = ""

# ✅ PDF 처리 함수들
def pdf_to_image(file_path, page_num):
    doc = fitz.open(file_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    img = pix.tobytes("png")
    return img

def extract_address_area_floor_from_text(text):
    try:
        address = re.search(r"\[집합건물\]\s*([^\n]+)", text)
        address = address.group(1).strip() if address else ""
        area_match = re.findall(r"(\d+\.\d+)\s*㎡", text)
        area_val = f"{area_match[-1]}㎡" if area_match else ""
        floor_match = re.findall(r"제(\d+)층", address)
        floor_num = int(floor_match[-1]) if floor_match else None
        return address, area_val, floor_num
    except Exception as e:
        st.error(f"PDF 처리 오류: {e}")
        return "", "", None

def extract_owner_number_from_summary(text):
    try:
        owners = []
        summary_match = re.search(r"주요 등기사항 요약[\s\S]+?\[ 참 고 사 항 \]", text)
        if summary_match:
            summary_text = summary_match.group()
            owner_matches = re.findall(r"등기명의인.*?\n([^\s]+)\s+\(소유자\)\s+(\d{6}-\*{7})", summary_text)
            if owner_matches:
                for name, reg_no in owner_matches:
                    owners.append(f"{name} {reg_no}")
        return "\n".join(owners) if owners else "❗ 주요사항 요약에서 소유자/주민등록번호를 찾지 못했습니다."
    except Exception as e:
        st.error(f"PDF 요약 처리 오류: {e}")
        return ""

# ✅ 메인 앱 실행 함수
def main():
    st.set_page_config(page_title="LTV 계산기", layout="wide")
    st.title("🏠 LTV 계산기 (주소+면적추출)")

    init_session()

    extracted_address, extracted_area = "", ""

    uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])

    if uploaded_file:
        path = f"./{uploaded_file.name}"
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with fitz.open(path) as doc:
            full_text = "".join(page.get_text() for page in doc)
            total_pages = doc.page_count

            # ✅ 추출
            extracted_address, extracted_area, floor_num = extract_address_area_floor_from_text(full_text)
            owner_number = extract_owner_number_from_summary(full_text)

            # ✅ 화면 출력
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state["current_page"] < total_pages:
                    img_left = pdf_to_image(path, st.session_state["current_page"])
                    st.image(img_left, caption=f"Page {st.session_state['current_page'] + 1} of {total_pages}")
            with col2:
                if st.session_state["current_page"] + 1 < total_pages:
                    img_right = pdf_to_image(path, st.session_state["current_page"] + 1)
                    st.image(img_right, caption=f"Page {st.session_state['current_page'] + 2} of {total_pages}")

            # ✅ 페이지 넘기기 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("◀ 이전 페이지"):
                    if st.session_state["current_page"] > 0:
                        st.session_state["current_page"] -= 1
            with col2:
                if st.button("다음 페이지 ▶"):
                    if st.session_state["current_page"] < total_pages - 1:
                        st.session_state["current_page"] += 1

            # ✅ 다운로드
            with open(path, "rb") as f:
                st.download_button("업로드한 등기부등본 다운로드", f, uploaded_file.name, mime="application/pdf")

            # ✅ 추출된 정보 표시
            st.markdown(f"**고객명:** {owner_number}")
            st.markdown(f"**주소:** {extracted_address}")
            st.markdown(f"**전용면적:** {extracted_area}")
            if floor_num:
                st.markdown(f"**층수:** 제{floor_num}층")

    else:
        st.warning("PDF 파일을 업로드하세요.")

    # ✅ LTV 계산 및 대출 항목 입력 UI 포함 (여기서 계속)
    # ⬇️ 다음에 계속 추가됩니다

# ✅ 앱 실행
if __name__ == "__main__":
    main()
