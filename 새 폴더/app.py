import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="LTV 계산기", layout="wide")

# 페이지 최상단에 제목 한 번만 표시
st.title("🏠 LTV 계산기 (Streamlit + PDF 자동 추출)")

# 텍스트 추출 및 주소/면적 분석 함수
def extract_address_and_area(file_path):
    extracted_address = ""
    extracted_area = ""
    
    try:
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()

        # 주소 추출 (집합건물 주소 패턴을 추출)
        addr_match = re.search(r"\[집합건물\]\s*([^\n]+)", text)
        if addr_match:
            extracted_address = addr_match.group(1).strip()
        
        # 전용면적 추출 (단위 m²을 포함하는 숫자 추출)
        area_match = re.findall(r"([\d.,]+)\s*㎡", text)
        if area_match:
            extracted_area = area_match[-1].replace(",", "").strip() + "㎡"

        return extracted_address, extracted_area

    except Exception as e:
        st.error(f"PDF 처리 오류: {e}")
        return extracted_address, extracted_area

# PDF 업로드 및 처리
uploaded_file = st.file_uploader("📄 등기부등본 PDF 업로드", type=["pdf"])

extracted_address = ""
extracted_area = ""

if uploaded_file is not None:
    # 파일 저장 (임시 경로)
    file_path = f"./{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 주소 및 전용면적 추출
    extracted_address, extracted_area = extract_address_and_area(file_path)
    
    # 추출된 주소 및 전용면적 표시
    st.text_input("주소", extracted_address, key="address_input")
    st.text_input("전용면적 (㎡)", extracted_area, key="area_input")

# 숫자 포맷팅 함수
def format_number(value: str) -> str:
    try:
        cleaned = re.sub(r"[^\d]", "", value)
        number = int(cleaned)
        return f"{number:,}"
    except:
        return value

# 한글 숫자 단위 처리 함수 (ex. 8억 3,500만 → 835000)
def parse_korean_number(text: str) -> int:
    text = text.replace(",", "").strip()
    total = 0
    ok = False

    match = re.search(r"(\d+)\s*억", text)
    if match:
        total += int(match.group(1)) * 10000
        ok = True

    match = re.search(r"(\d+)\s*만", text)
    if match:
        total += int(match.group(1))
        ok = True

    if not ok:
        try:
            total = int(text)
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

# 화면 배치
col1 = st.columns([1])[0]  # 한 칼럼으로 배치하여 왼쪽 정렬

# 왼쪽 칼럼 내용

with col1:
    # KB 시세 입력란
    raw_market_price = st.text_input("KB 시세 (만원)", value="0", key="market_price_input")

    # 층수 선택
    floor = st.selectbox("해당 층수", ["1층", "2층", "3층 이상"], key="floor_select")

    # 시세 기준 안내
    if floor in ["1층", "2층"]:
        st.markdown('<span style="color:#990011;">📉 하안가</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#0063B2;">📈 일반가</span>', unsafe_allow_html=True)

    # ——— 이 아래 코드를 if/else 바깥으로 내립니다 ———

    # 방공제 지역 선택 (항상 표시)
    region = st.selectbox("방공제 지역 선택", [""] + list(region_map.keys()), key="region_selectbox")
    default_deduction = region_map.get(region, 0)

    # 방공제 수동 입력 (콤마 포함)
    manual_deduction_raw = st.text_input(
        "방공제 금액 (만원)",
        value=f"{default_deduction:,}",
        key="deduction_input"
    )
    try:
        deduction = int(re.sub(r"[^\d]", "", manual_deduction_raw))
    except:
        deduction = default_deduction
    st.write(f"➕ 적용된 방공제 금액: **{deduction:,}만원**")

import re, urllib.parse

# ▶ KB 시세 자동 검색 버튼
if st.button("🔎 KB 시세 자동 검색"):
    # extracted_address는 PDF에서 추출한 전체 주소 (예: "서울특별시 강남구 삼성동 31")
    if extracted_address:
        # “OO동 NNN” 형태만 추출
        m = re.search(r"([가-힣]+동)\s*(\d+[-\d]*)", extracted_address)
        query = f"{m.group(1)} {m.group(2)}" if m else extracted_address
        qs = urllib.parse.quote_plus(query)
        url = f"https://kbland.kr/land/search?keyword={qs}"
    else:
        # 주소 없으면 기본 맵 열기
        url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"

    # 새 탭으로 열기
    st.components.v1.html(
        f"""<script>window.open("{url}", "_blank")</script>""",
        height=0
    )


# LTV 비율 슬라이더
ltv = st.slider("LTV 비율 (%)", 50, 90, 80, step=5)

# 대출 항목 입력
st.markdown("### 대출 항목 입력")
rows = st.number_input("항목 개수", min_value=1, max_value=10, value=3)

data = []
for i in range(int(rows)):
    cols = st.columns(5)

    with cols[0]:
        lender = st.text_input(f"설정자", key=f"lender_{i}")

    with cols[1]:
        raw_maxamt = st.text_input(f"채권최고액", key=f"maxamt_{i}")
        max_amt = format_number(raw_maxamt)

    with cols[2]:
        ratio = st.text_input(f"설정비율 (%)", value="120", key=f"ratio_{i}")

    with cols[3]:
        try:
            calc = int(int(max_amt.replace(",", "")) * 100 / int(ratio))
        except:
            calc = 0
        raw_principal = st.text_input(f"원금", value=f"{calc:,}", key=f"principal_{i}")
        principal = format_number(raw_principal)

    with cols[4]:
        status = st.selectbox(f"진행구분", ["유지", "대환", "선말소"], key=f"status_{i}")

    data.append({
        "설정자": lender,
        "채권최고액": max_amt,
        "설정비율": ratio,
        "원금": principal,
        "진행구분": status
    })

# LTV 한도 계산
ltv_limit = (parse_korean_number(raw_market_price) * ltv / 100) - deduction
st.write(f"📊 LTV 한도: {ltv_limit:,.0f}만원")

# 가용 금액 계산
available_amount = ltv_limit
for item in data:
    if item["진행구분"] == "대환" or item["진행구분"] == "선말소":
        available_amount -= int(item["원금"].replace(",", ""))
st.write(f"💰 가용 금액: {available_amount:,.0f}만원")



# LTV 컨설팅 및 브릿지 비용 계산기
st.markdown("### LTV 컨설팅 및 브릿지 비용 계산기")

# 변수 초기화
total_loan = st.text_input("총 대출금액 입력", value="")
consulting_rate = st.number_input("컨설팅 수수료율 (%)", value=1.5, step=0.1)
bridge_amount = st.text_input("브릿지 금액 입력", value="")
bridge_rate = st.number_input("브릿지 수수료율 (%)", value=0.7, step=0.1)

# 컨설팅 수수료 계산
if total_loan:
    try:
        total_loan_value = float(total_loan.replace(",", "")) if total_loan else 0
        consulting_fee = (total_loan_value * consulting_rate) / 100
        consulting_fee_formatted = f"{consulting_fee:,.0f}만원"
    except ValueError:
        consulting_fee_formatted = "잘못된 입력"
else:
    consulting_fee_formatted = ""

# 브릿지 수수료 계산
if bridge_amount:
    try:
        bridge_amount_value = float(bridge_amount.replace(",", "")) if bridge_amount else 0
        bridge_fee = (bridge_amount_value * bridge_rate) / 100
        bridge_fee_formatted = f"{bridge_fee:,.0f}만원"
    except ValueError:
        bridge_fee_formatted = "잘못된 입력"
else:
    bridge_fee_formatted = ""

# 결과 출력
st.subheader("계산 결과")
st.write(f"컨설팅 비용: {consulting_fee_formatted}")
st.write(f"브릿지 비용: {bridge_fee_formatted}")
