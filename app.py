import streamlit as st
import fitz  # PyMuPDF
import re
import urllib.parse

# 페이지 설정
st.set_page_config(page_title="LTV 계산기", layout="wide")
st.title("🏠 LTV 계산기 (주소+면적추출)")

# 방공제 지역 맵
region_map = {
    "서울특별시": 5500,
    "인천광역시 서구": 2800,
    "인천광역시 대곡동 불로동 마전동 금곡동 오류동": 2800,
    "인천광역시 왕길동 당하동 원당동": 2800,
    "인천경제자유구역 남동국가산업단지": 2800,
    "인천광역시 강화군 옹진군": 2500,
    "경기도 의정부시 구리시 하남시 고양시 수원시 성남시": 4800,
    "경기도 안양시 부천시 광명시 과천시 의왕시 군포시 용인시": 4800,
    "경기도 화성시 세종시 김포시": 2800,
    "경기도 안산시 광주시 파주시 이천시 평택시": 2800,
    "경기도 시흥시 반월특수지역": 2500,
    "경기도 시흥시 그밖의 지역": 4800,
    "경기도 남양주시 호평동 평내동 금곡동 일패동 이패동 삼패동 가운동 수석동 지금동 도농동": 4800,
    "경기도 남양주시 그밖의 지역": 2500,
    "광주 대구 대전 부산 울산 군지역": 2500,
    "광주 대구 대전 부산 울산 군지역 외": 2800,
    "그밖의 지역": 2500,
    "방공제없음": 0
}

# 주소 및 면적 추출 함수
def extract_address_area_floor(file_path):
    try:
        text = "".join(page.get_text() for page in fitz.open(file_path))
        address = re.search(r"\[집합건물\]\s*([^\n]+)", text).group(1).strip() if re.search(r"\[집합건물\]\s*([^\n]+)", text) else ""
        area_match = re.findall(r"(\d+\.\d+)\s*㎡", text)
        area_val = f"{area_match[-1]}㎡" if area_match else ""
        floor_match = re.findall(r"제(\d+)층", address)
        floor_num = int(floor_match[-1]) if floor_match else None
        return address, area_val, floor_num
    except Exception as e:
        st.error(f"PDF 처리 오류: {e}")
        return "", "", None

def parse_korean_number(text: str) -> int:
    txt = text.replace(",", "").strip()
    total = 0
    m = re.search(r"(\d+)\s*억", txt)
    if m:
        total += int(m.group(1)) * 10000
    m = re.search(r"(\d+)\s*만", txt)
    if m:
        total += int(m.group(1))
    if total == 0:
        try:
            total = int(txt)
        except:
            total = 0
    return total

# 파일 업로드
uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"])

if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with open(path, "rb") as f:
        st.download_button("업로드한 등기부등본 다운로드", f, uploaded_file.name, mime="application/pdf")
    extracted_address, extracted_area, floor_num = extract_address_area_floor(path)
else:
    extracted_address, extracted_area, floor_num = "", "", None

# 입력 항목
address_input = st.text_input("주소", extracted_address)
area_input = st.text_input("전용면적 (㎡)", extracted_area)

if floor_num:
    st.markdown("📉 하안가" if floor_num <= 2 else "📈 일반가")

if st.button("KB 시세 조회"):
    url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"
    st.components.v1.html(f"<script>window.open('{url}','_blank')</script>", height=0)

# 버튼 아래에 시세 입력창
raw_price = st.text_input("KB 시세 (만원)", "0")

# 방공제 입력
region = st.selectbox("방공제 지역 선택", [""] + list(region_map.keys()))
default_d = region_map.get(region, 0)
manual_d = st.text_input("방공제 금액 (만원)", f"{default_d:,}")
deduction = int(re.sub(r"[^\d]", "", manual_d)) if manual_d else default_d
st.write(f"적용된 방공제 금액: {deduction:,}만원")

# LTV 입력 2개
col1, col2 = st.columns(2)
raw_ltv1 = col1.text_input("LTV 비율 ①", "80")
raw_ltv2 = col2.text_input("LTV 비율 ②", "")

ltv_selected = []
for val in [raw_ltv1, raw_ltv2]:
    try:
        v = int(val)
        if 1 <= v <= 100:
            ltv_selected.append(v)
    except:
        pass
ltv_selected = list(dict.fromkeys(ltv_selected))

# 대출 항목
st.markdown("### 대출 항목 입력")
rows = st.number_input("항목 개수", min_value=1, max_value=10, value=3)
items = []
for i in range(int(rows)):
    cols = st.columns(5)
    lender = cols[0].text_input("설정자", key=f"lender_{i}")
    max_amt = re.sub(r"[^\d]", "", cols[1].text_input("채권최고액 (만원)", key=f"maxamt_{i}"))
    ratio = cols[2].text_input("설정비율 (%)", "120", key=f"ratio_{i}")
    try:
        calc = int(max_amt or 0) * 100 // int(ratio or 100)
    except:
        calc = 0
    principal = re.sub(r"[^\d]", "", cols[3].text_input("원금", f"{calc:,}", key=f"principal_{i}"))
    status = cols[4].selectbox("진행구분", ["유지", "대환", "선말소"], key=f"status_{i}")
    items.append({
        "설정자": lender,
        "채권최고액": max_amt,
        "설정비율": ratio,
        "원금": principal,
        "진행구분": status
    })

# 계산
total_value = parse_korean_number(raw_price)
senior_principal_sum = sum(int(item["원금"] or 0) for item in items if item["진행구분"] in ["대환", "선말소"])
sum_dh = sum(int(item["원금"] or 0) for item in items if item["진행구분"] == "대환")
sum_sm = sum(int(item["원금"] or 0) for item in items if item["진행구분"] == "선말소")

text_to_copy = ""

# 📍 일반가 / 하안가 여부
type_of_price = "📉 하안가" if floor_num and floor_num <= 2 else "📈 일반가"
text_to_copy += f"{type_of_price}\n"

# 📍 진행구분별 원금 합계
text_to_copy += "\n[진행구분별 원금 합계]\n"
text_to_copy += "구분     | 합계 (만원)\n"
text_to_copy += "--------|--------------\n"
text_to_copy += f"대환     | {sum_dh:,.0f}\n"
text_to_copy += f"선말소   | {sum_sm:,.0f}\n"

# 📍 대출 항목 표
text_to_copy += "\n[대출 항목]\n"
text_to_copy += "설정자 / 채권최고액 (만원) / 설정비율 (%) / 원금 / 진행구분\n"
for item in items:
    max_amt = re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0")
    principal_amt = re.sub(r"[^\d]", "", item.get("원금", "") or "0")
    text_to_copy += f"{item['설정자']} / {int(max_amt):,} / {item['설정비율']} / {int(principal_amt):,} / {item['진행구분']}\n"

# 📍 LTV 계산 결과
for ltv in ltv_selected:
    text_to_copy += "-" * 56 + "\n"
    limit_senior = total_value * (ltv / 100) - deduction
    avail_senior = limit_senior - senior_principal_sum
    text_to_copy += f"📌 선순위 LTV {ltv}% 대출가능금액: {limit_senior:,.0f}만원\n"
    text_to_copy += f"💡 선순위 LTV {ltv}%가용금액: {avail_senior:,.0f}만원\n"

    if any(item["진행구분"] == "유지" for item in items):
        maintain_maxamt_sum = sum(
            int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
            for item in items if item["진행구분"] == "유지"
        )
        limit_sub = total_value * (ltv / 100) - maintain_maxamt_sum - deduction
        avail_sub = limit_sub - senior_principal_sum
        text_to_copy += f"📌 후순위 LTV {ltv}% 대출가능금액: {limit_sub:,.0f}만원\n"
        text_to_copy += f"💡 후순위 LTV {ltv}%가용금액: {avail_sub:,.0f}만원\n"

        
# 수수료
st.markdown("### 컨설팅 및 브릿지 수수료 계산")
total_loan = st.text_input("총 대출금액")
consulting_rate = st.number_input("컨설팅 수수료율 (%)", value=1.5, step=0.1)
bridge_amount = st.text_input("브릿지 금액")
bridge_rate = st.number_input("브릿지 수수료율 (%)", value=0.7, step=0.1)
consulting_fee = int(total_loan.replace(",", "")) * consulting_rate / 100 if total_loan else 0
bridge_fee = int(bridge_amount.replace(",", "")) * bridge_rate / 100 if bridge_amount else 0
total_fee = consulting_fee + bridge_fee

st.write(f"컨설팅 비용: {consulting_fee:,.0f}만원")
st.write(f"브릿지 비용: {bridge_fee:,.0f}만원")
st.write(f"🔗 총 비용: {total_fee:,.0f}만원")

text_to_copy += f"\n컨설팅 비용: {consulting_fee:,.0f}만원\n"
text_to_copy += f"브릿지 비용: {bridge_fee:,.0f}만원\n"
text_to_copy += f"🔗 총 비용: {total_fee:,.0f}만원"

def is_valid_item(item):
    return any([
        item["설정자"].strip(),
        re.sub(r"[^\d]", "", item["채권최고액"] or ""),
        re.sub(r"[^\d]", "", item["원금"] or "")
    ])

# 항상 표시
st.text_area("📋 복사해서 붙여넣기", value=text_to_copy, height=550)

# 버튼 누르면 강조해서 다시 보여주기
if st.button("🔗 복사할 내용 보기"):
    st.success("복사해서 붙여넣으세요!")

