import re
import fitz
import streamlit as st

def extract_owner_number_from_summary(text):
    """
    📋 주요 등기사항 요약 or 전체에서 고객명(소유자) + 주민등록번호(가림처리) 추출
    - 요약 영역 못찾으면 전체에서 백업 검색
    - 주민등록번호 마스킹 패턴 다양 대응
    - 줄바꿈, 공백 오류 최소화
    """
    try:
        owners = []

        # 1차: 주요사항 요약 블럭 먼저 시도
        summary_match = re.search(r"주요 등기사항 요약[\s\S]+?\[ 참 고 사 항 \]", text)
        target_text = summary_match.group() if summary_match else text

        # OCR 오류 대비: 불필요한 줄바꿈 정리
        target_text_clean = re.sub(r"\n+", "\n", target_text)

        # 2차: 주민번호 포맷 강화 (마스킹 혼합 대응)
        owner_matches = re.findall(r"등기명의인.*?\n([^\s\(]+)\s+\(소유자\)\s+(\d{6}-[^\s\n]+)", target_text_clean)
        if not owner_matches:
            # 3차: 전체에서 직접 스캔
            owner_matches = re.findall(r"등기명의인.*?\n([^\s\(]+)\s+\(소유자\)\s+(\d{6}-[^\s\n]+)", text)

        if owner_matches:
            for name, reg_no in owner_matches:
                owners.append(f"{name} {reg_no}")
        else:
            owners.append("❗ 소유자/주민등록번호를 찾지 못했습니다.")

        return "\n".join(owners)
    except Exception as e:
        st.error(f"PDF 요약 처리 오류: {e}")
        return ""

def extract_address_area_floor_from_text(text):
    """
    🏠 집합건물 표제부 영역에서 주소, 면적, 층수 추출
    - 주소: '[집합건물]' 이후 한 줄
    - 면적: '㎡' 단위 마지막 값
    - 층수: '제N층' 마지막 매칭값
    """
    try:
        address = re.search(r"\[집합건물\]\s*([^\n]+)", text)
        address_val = address.group(1).strip() if address else ""
        area_match = re.findall(r"(\d+\.\d+)\s*㎡", text)
        area_val = f"{area_match[-1]}㎡" if area_match else ""
        floor_match = re.findall(r"제(\d+)층", address_val)
        floor_num = int(floor_match[-1]) if floor_match else None
        return address_val, area_val, floor_num
    except Exception as e:
        st.error(f"PDF 처리 오류: {e}")
        return "", "", None

def pdf_to_image(file_path, page_num):
    """
    📷 PDF 페이지를 PNG 이미지로 변환 (Streamlit에서 표시 가능)
    - PyMuPDF 사용
    """
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = pix.tobytes("png")
        return img
    except Exception as e:
        st.error(f"PDF 이미지 변환 오류: {e}")
        return None
