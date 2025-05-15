import re
import fitz

def extract_address_area_floor_from_text(text):
    try:
        address = re.search(r"\[집합건물\]\s*([^\n]+)", text).group(1).strip() if re.search(r"\[집합건물\]\s*([^\n]+)", text) else ""
        area_match = re.findall(r"(\d+\.\d+)\s*㎡", text)
        area_val = f"{area_match[-1]}㎡" if area_match else ""
        floor_match = re.findall(r"제(\d+)층", address)
        floor_num = int(floor_match[-1]) if floor_match else None
        return address, area_val, floor_num
    except Exception as e:
        return "", "", None

def extract_owner_number_from_summary(text):
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
        return ""

def pdf_to_image(file_path, page_num):
    doc = fitz.open(file_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    img = pix.tobytes("png")
    return img
