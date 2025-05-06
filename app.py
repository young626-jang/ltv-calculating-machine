import streamlit as st

st.set_page_config(page_title="LTV 계산기", layout="wide")

import fitz  # PyMuPDF
import re
import urllib.parse

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
raw_ltv2 = col2.text_input("LTV 비율 ②", "85")

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
rows = st.number_input("항목 개수", min_value=1, max_value=10, value=1)
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

text_to_copy = f"📍 주소: {address_input}\n" + text_to_copy
# 📍 일반가 / 하안가 여부 + KB시세
type_of_price = "📉 하안가" if floor_num and floor_num <= 2 else "📈 일반가"
text_to_copy += f"{type_of_price} | KB시세: {raw_price}원 | 방공제 금액: {deduction:,}만원\n"

# 대출 항목 조건 필터
valid_items = []
for item in items:
    # 숫자만 추출
    is_valid = any([
        item.get("설정자", "").strip(),
        re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0") != "0",
        re.sub(r"[^\d]", "", item.get("원금", "") or "0") != "0"
    ])
    if is_valid:
        valid_items.append(item)

# 대출 항목 출력
if valid_items:
    text_to_copy += "\n[대출 항목]\n"
    for item in valid_items:
        max_amt = int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
        principal_amt = int(re.sub(r"[^\d]", "", item.get("원금", "") or "0"))
        text_to_copy += f"{item['설정자']} | 채권최고액: {max_amt:,} | 비율: {item.get('설정비율', '0')}% | 원금: {principal_amt:,} | {item['진행구분']}\n"

# LTV 계산 함수 정의
def calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=True):
    if is_senior:
        # 선순위 계산
        limit = int(total_value * (ltv / 100) - deduction) // 10 * 10
        available = int(limit - senior_principal_sum) // 10 * 10
    else:
        # 후순위 계산
        limit = int(total_value * (ltv / 100) - maintain_maxamt_sum - deduction) // 10 * 10
        available = int(limit - senior_principal_sum) // 10 * 10
    return limit, available

# "유지"와 관련된 조건 미리 계산
has_maintain = any(item["진행구분"] == "유지" for item in items)
has_senior = any(item["진행구분"] in ["대환", "선말소"] for item in items)

for ltv in ltv_selected:
    # ✅ 선순위는 "유지"가 없을 때만
    if has_senior and not has_maintain:
        limit_senior, avail_senior = calculate_ltv(total_value, deduction, senior_principal_sum, 0, ltv, is_senior=True)
        text_to_copy += f"📌 선순위 LTV {ltv}% 대출가능금액: {limit_senior:,}만원 (가용금액: {avail_senior:,}만원)\n"

    # ✅ 후순위는 "유지"가 있을 때만
    if has_maintain:
        maintain_maxamt_sum = sum(
            int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
            for item in items if item["진행구분"] == "유지"
        )
        limit_sub, avail_sub = calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=False)
        text_to_copy += f"📌 후순위 LTV {ltv}% 대출가능금액: {limit_sub:,}만원 (가용금액: {avail_sub:,}만원)\n"

# 📍 진행구분별 원금 합계
text_to_copy += "\n[진행구분별 원금 합계]\n"
if sum_dh > 0:
    text_to_copy += f"대환: {sum_dh:,}만원\n"
if sum_sm > 0:
    text_to_copy += f"선말소: {sum_sm:,}만원\n"

st.text_area("📋 결과 내용", value=text_to_copy, height=350)

# 수수료 계산을 위한 재사용 가능한 함수 정의
def calculate_fees(amount, rate):
    if amount and re.sub(r"[^\d]", "", amount).isdigit():
        return int(re.sub(r"[^\d]", "", amount)) * rate / 100
    return 0

# Streamlit UI
st.markdown("### 컨설팅 및 브릿지 수수료 계산")

# 입력 필드
total_loan = st.text_input ("총 대출금액")
컨설팅_rate = st.number_input ("컨설팅 수수료율(%), 값=1.5, 단계=0.1)

브리지 양 = st.text_input ("브릿지 금액")
bridge_rate = st.number_input ("브릿지 수수료율(%), 값=0.7, 단계=0.1)

# 수수료 계산
컨설팅_fee = 계산_fees(총_loan, 컨설팅_요금)
bridge_fee = 계산_fees(bridge_금액, bridge_rate)
총_fee = 컨설팅_fee + 브리지_fee

# 결과 출력
st.write(f"컨설팅 비용): {int(consult_fee):,}만원")
st.write(f"브릿지 비용): {int(bridge_fee):,}만원")
st.write(f"🔗 총 비용: {int(총_fee):,}만원")

# CSS를 활용한 UI 스타일 개선
st.markdown(
    """
 <스타일>
 /* 전체 배경색 */
 .메인 {
 배경색: #FFDFB9;
 }

 /* 입력 필드 스타일 */
 .stTextInput, .stNumber입력, .stSelectbox {
 배경색: #FFFFF;
 경계: 1px 고체 #CCCCCCC;
 국경 radius: 5 px;
 패딩: 5 px;
 }

 /* 버튼 스타일 */
 .stButton>버튼 {
 배경색: #007BFF;
 색상: 흰색;
 경계: 없음;
 국경 radius: 5 px;
 패딩: 10 px 20 px;
 글꼴 크기: 16 px;
 커서: 포인터;
 }
 .stButton>버튼:호버 {
 배경색: #0056b3;
 }
 </스타일>
 """
 안전하지 않은_allow_html=True
)
