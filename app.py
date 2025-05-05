import streamlit as st
import fitz  # PyMuPDF
import re
import urllib.parse

# 페이지 설정
st.set_page_config(page_title="LTV 계산기", layout="wide")
st.title("🏠 LTV 계산기 (주소+면적추출)")

# 주소 및 면적 추출 함수

def extract_address_area_floor(file_path):
    try:
        text = "".join(page.get_text() for page in fitz.open(file_path))

        # 주소 추출
        addr_match = re.search(r"\[집합건물\]\s*([^\n]+)", text)
        if addr_match:
            address = addr_match.group(1).strip()
        else:
            address = ""

        # 면적 추출
        area_match = re.findall(r"(\d+\.\d+)\s*㎡", text)
        if area_match:
            area_val = f"{area_match[-1]}㎡"
        else:
            area_val = ""

        # 층수 추출
        floor_match = re.findall(r"제(\d+)층", address)
        if floor_match:
            floor_num = int(floor_match[-1])
        else:
            floor_num = None

        return address, area_val, floor_num

    except Exception as e:
        st.error(f"PDF 처리 오류: {e}")
        return "", "", None


# PDF 업로드 받기
uploaded_file = st.file_uploader("📄 등기부등본 PDF 업로드", type=["pdf"])

# PDF 저장 및 다운로드 링크
if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with open(path, "rb") as f:
        st.download_button(
            label="📥 업로드한 등기부등본 다운로드",
            data=f,
            file_name=uploaded_file.name,
            mime="application/pdf"
        )

    # (이 아래에서 추출 함수 호출하면 됨)
    extracted_address, extracted_area, floor_num = extract_address_area_floor(path)

else:
    extracted_address, extracted_area, floor_num = "", "", None

# 메인 레이아웃: 단일 컬럼 선언 (여기 먼저 선언)
col1 = st.columns([1])[0]

with col1:
    # KB 시세 입력
    raw_price = st.text_input("KB 시세 (만원)", value="0", key="market_price_input")

    # 주소/면적 입력 (PDF 추출값 기본 반영)
    address_input = st.text_input("주소", extracted_address, key="address_input")
    area_input = st.text_input("전용면적 (㎡)", extracted_area, key="area_input")    

# 숫자 포맷팅 및 단위 파싱 함수
def format_number(val: str) -> str:
    nums = re.sub(r"[^\d]", "", val)
    return f"{int(nums):,}" if nums else ""

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

# LTV 비율 슬라이더
ltv = st.slider("LTV 비율 (%)", 50, 90, 80, step=5)
deduction = 0
    
# ─── 하안가 / 일반가 표시 ───

if floor_num is None:
    st.write("")
elif floor_num <= 2:
    st.markdown('<span style="color:#990011;">📉 하안가</span>', unsafe_allow_html=True)
else:
    st.markdown('<span style="color:#0063B2;">📈 일반가</span>', unsafe_allow_html=True)

    # ─── 버튼 위치 변경: 안내 바로 아래 ───
    if st.button("🔎 KB 시세 자동 검색"):
        if extracted_address:
            mm = re.search(r"([가-힣]+동)\s*(\d+[-\d]*)", extracted_address)
            q = f"{mm.group(1)} {mm.group(2)}" if mm else extracted_address
            url = f"https://kbland.kr/land/search?keyword={urllib.parse.quote_plus(q)}"
        else:
            url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"
        st.components.v1.html(f"<script>window.open('{url}','_blank')</script>", height=0)

    # 방공제 입력
    region = st.selectbox("방공제 지역 선택", [""] + list(region_map.keys()), key="region_selectbox")
    default_d = region_map.get(region, 0)
    manual_d = st.text_input("방공제 금액 (만원)", value=f"{default_d:,}", key="deduction_input")
    try:
        deduction = int(re.sub(r"[^\d]", "", manual_d))
    except:
        deduction = default_d
    st.write(f"➕ 적용된 방공제 금액: **{deduction:,}만원**")


# 대출 항목 입력 및 계산
st.markdown("### 대출 항목 입력")
rows = st.number_input("항목 개수", min_value=1, max_value=10, value=3)
items = []

for i in range(int(rows)):
    cols = st.columns(5)

    with cols[0]:
        lender = st.text_input("설정자", key=f"lender_{i}")

    with cols[1]:
        raw_maxamt = st.text_input("채권최고액 (만원)", key=f"maxamt_{i}")
        max_amt = format_number(raw_maxamt)

    with cols[2]:
        ratio = st.text_input("설정비율 (%)", value="120", key=f"ratio_{i}")

    with cols[3]:
        try:
            calc = int(max_amt.replace(",", "")) * 100 // int(ratio)
        except:
            calc = 0
        raw_principal = st.text_input("원금", value=f"{calc:,}", key=f"principal_{i}")
        principal = format_number(raw_principal)

    with cols[4]:
        status = st.selectbox("진행구분", ["유지", "대환", "선말소"], key=f"status_{i}")

    # items 리스트에 딕셔너리 형태로 저장
    items.append({
        "설정자": lender,
        "채권최고액": max_amt,
        "설정비율": ratio,
        "원금": principal,
        "진행구분": status
    })


# ── LTV 평가 및 가용 금액 계산 (동적 LTV) ──
total_value = parse_korean_number(raw_price)  # raw_price: KB 시세(총시세, 만원)
# 1) 선순위 LTV
limit_senior = total_value * (ltv / 100) - deduction
senior_principal_sum = sum(
    int(item["원금"].replace(",", ""))
    for item in items
    if item["진행구분"] in ["대환", "선말소"]
)
avail_senior = limit_senior - senior_principal_sum

st.write(f"📌 선순위 LTV {ltv}% 대출가능금액: {limit_senior:,.0f}만원")
st.write(f"💡 선순위 가용금액 (대환·선말소 차감 후): {avail_senior:,.0f}만원")

# 2) 후순위 LTV 계산 (유지 항목이 있을 경우)
if any(item["진행구분"] == "유지" for item in items):
    # 유지 항목의 채권최고액을 숫자만 뽑아 합산(빈값은 0)
    maintain_maxamt_sum = sum(
        int(digits) if (digits := re.sub(r"[^\d]", "", item.get("채권최고액", ""))) else 0
        for item in items
        if item["진행구분"] == "유지"
    )

    limit_sub = total_value * (ltv / 100) - maintain_maxamt_sum - deduction
    avail_sub = limit_sub - senior_principal_sum

    st.write(f"📌 후순위 LTV {ltv}% 대출가능금액: {limit_sub:,.0f}만원")
    st.write(f"💡 후순위 가용금액 (대환·선말소 차감 후): {avail_sub:,.0f}만원")


# ── 컨설팅 & 브릿지 비용 계산 ──
st.markdown("### LTV 컨설팅 및 브릿지 비용 계산기")
total_loan = st.text_input("총 대출금액 입력", "")
consulting_rate = st.number_input("컨설팅 수수료율 (%)", value=1.5, step=0.1)
bridge_amount = st.text_input("브릿지 금액 입력", "")
bridge_rate = st.number_input("브릿지 수수료율 (%)", value=0.7, step=0.1)

consulting_fee = 0.0
bridge_fee = 0.0

if total_loan:
    try:
        loan_val = float(total_loan.replace(",", ""))
        consulting_fee = loan_val * consulting_rate / 100
    except:
        consulting_fee = 0.0

if bridge_amount:
    try:
        bridge_val = float(bridge_amount.replace(",", ""))
        bridge_fee = bridge_val * bridge_rate / 100
    except:
        bridge_fee = 0.0

st.subheader("계산 결과")
st.write(f"컨설팅 비용: {consulting_fee:,.0f}만원")
st.write(f"브릿지 비용: {bridge_fee:,.0f}만원")
total_fee = consulting_fee + bridge_fee
st.write(f"🔗 총 비용 (컨설팅 + 브릿지): {total_fee:,.0f}만원")


# ── 복사 영역 표시 ──
import json
text_to_copy = (
    f"📌 선순위 LTV {ltv}% 대출가능금액: {limit_senior:,.0f}만원\n"
    f"💡 선순위 가용금액: {avail_senior:,.0f}만원\n"
    + (
        f"📌 후순위 LTV {ltv}% 대출가능금액: {limit_sub:,.0f}만원\n"
        f"💡 후순위 가용금액: {avail_sub:,.0f}만원\n"
        if 'limit_sub' in locals()
        else ""
    )
    + f"컨설팅 비용: {consulting_fee:,.0f}만원\n"
    + f"브릿지 비용: {bridge_fee:,.0f}만원\n"
    + f"🔗 총 비용: {total_fee:,.0f}만원"
)

if st.button("🔗 복사할 내용 보기"):
    st.text_area("📋 복사해서 붙여넣기", value=text_to_copy, height=200)
    
