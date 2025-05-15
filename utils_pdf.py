import re
import fitz

def extract_address_area_floor_from_text(text):
    """
    PDF 텍스트에서 주소, 면적, 층수를 추출하는 함수
    Args:
        text (str): PDF에서 추출된 텍스트
    Returns:
        tuple: (address, area_val, floor_num)
    """
    try:
        address_match = re.search(r"\[집합건물\]\s*([^\n]+)", text)
        address = address_match.group(1).strip() if address_match else ""

        area_match = re.findall(r"(\d+\.\d+)\s*㎡", text)
        area_val = f"{area_match[-1]}㎡" if area_match else ""

        floor_match = re.findall(r"제(\d+)층", address)
        floor_num = int(floor_match[-1]) if floor_match else None

        return address, area_val, floor_num
    except Exception as e:
        # 디버깅을 위한 에러 메시지 출력
        print(f"Error in extract_address_area_floor_from_text: {e}")
        return "", "", None

def extract_owner_number_from_summary(text):
    """
    PDF 텍스트에서 소유자 이름과 주민등록번호를 추출하는 함수
    Args:
        text (str): PDF에서 추출된 텍스트
    Returns:
        str: 소유자 정보 문자열
    """
    try:
        owners = []
        summary_match = re.search(r"주요 등기사항 요약[\s\S]+?\[ 참 고 사 항 \]", text)
        if summary_match:
            summary_text = summary_match.group()
            owner_matches = re.findall(r"등기명의인.*?\n([^\s]+)\s+\(소유자\)\s+(\d{6}-\*{7})", summary_text)
            for name, reg_no in owner_matches:
                owners.append(f"{name} {reg_no}")
        return "\n".join(owners) if owners else "❗ 주요사항 요약에서 소유자/주민등록번호를 찾지 못했습니다."
    except Exception as e:
        # 디버깅을 위한 에러 메시지 출력
        print(f"Error in extract_owner_number_from_summary: {e}")
        return ""

def pdf_to_image(file_path, page_num):
    """
    PDF 페이지를 이미지로 변환하는 함수
    Args:
        file_path (str): PDF 파일 경로
        page_num (int): 변환할 페이지 번호 (0부터 시작)
    Returns:
        bytes: PNG 이미지 데이터
    """
    try:
        with fitz.open(file_path) as doc:
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = pix.tobytes("png")
        return img
    except Exception as e:
        # 디버깅을 위한 에러 메시지 출력
        print(f"Error in pdf_to_image: {e}")
        return None