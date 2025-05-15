import streamlit as st

st.set_page_config(page_title="LTV 계산기", layout="wide")

import fitz  # PyMuPDF
import re
import urllib.parse

# 여기서부터 본문 시작
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
    # 만약 위에서 못 잡으면 그냥 숫자 처리
    if total == 0:
        try:
            total = int(txt)
        except:
            total = 0
    return total

# 파일 업로드
uploaded_file = st.file_uploader("등기부등본 PDF 업로드", type=["pdf"], key="file_upload_main")

# PDF 페이지를 이미지로 변환하여 반환하는 함수
def pdf_to_image(file_path, page_num):
    doc = fitz.open(file_path)
    page = doc.load_page(page_num)  # 페이지 로드
    pix = page.get_pixmap()  # 페이지를 이미지로 변환
    img = pix.tobytes("png")  # PNG 형식으로 이미지 바이트로 변환
    return img

#  PDF에서 주소 및 면적 추출 함수
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

# PDF에서 소유자 주민번호 추출 함수
def extract_owner_number_from_file(file_path):
    try:
        text = "".join(page.get_text() for page in fitz.open(file_path))
        summary_match = re.search(r"주요 등기사항 요약[\s\S]+?\[ 참 고 사 항 \]", text)
        if summary_match:
            summary_text = summary_match.group()
            owner_matches = re.findall(r"등기명의인.*?\n([^\s]+)\s+\(소유자\)\s+(\d{6}-\*{7})", summary_text)
            if owner_matches:
                return "\n".join([f"{name} {reg_no}" for name, reg_no in owner_matches])
            else:
                return "❗ 요약본에는 등기명의인(소유자)이 없습니다."
        else:
            return "❗ 주요사항 요약 구간을 찾지 못했습니다."
    except Exception as e:
        return f"❗ PDF 처리 오류: {e}"

# 페이지 상태 저장
if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # PDF의 총 페이지 수 가져오기
    doc = fitz.open(path)
    total_pages = doc.page_count

    # Streamlit의 세션 상태를 사용하여 현재 페이지를 추적
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0  # 초기 페이지는 첫 번째 페이지

    # 현재 페이지의 이미지를 표시
    col1, col2 = st.columns(2)  # 두 열로 나누기
    with col1:
        if st.session_state["current_page"] < total_pages:
            img_left = pdf_to_image(path, st.session_state["current_page"])
            st.image(img_left, caption=f"Page {st.session_state['current_page'] + 1} of {total_pages}")

    with col2:
        if st.session_state["current_page"] + 1 < total_pages:
            img_right = pdf_to_image(path, st.session_state["current_page"] + 1) 
            st.image(img_right, caption=f"Page {st.session_state['current_page'] + 2} of {total_pages}")

    col1, col2, col3 = st.columns(3)

    with col2:
        col_left, col_right = st.columns(2)

        with col_left:
            if st.button("◀", key="prev_page"):
                if st.session_state["current_page"] > 0:
                    st.session_state["current_page"] -= 2

        with col_right:
            if st.button("▶", key="next_page"):
                if st.session_state["current_page"] < total_pages - 2:
                    st.session_state["current_page"] += 2

# 업로드한 등기를 다운로드받는 함수
if uploaded_file:
    path = f"./{uploaded_file.name}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with open(path, "rb") as f:
        st.download_button("업로드한 등기부등본 다운로드", f, uploaded_file.name, mime="application/pdf")
    extracted_address, extracted_area, floor_num = extract_address_area_floor(path)
else:
    extracted_address, extracted_area, floor_num = "", "", None

# KB 시세 입력값 포맷팅 함수 정의
def format_kb_price():
    raw = st.session_state.get("raw_price", "")
    clean = parse_korean_number(raw)  # 한글 단위 포함 처리
    if clean:
        st.session_state["raw_price"] = "{:,}".format(clean)
    else:
        st.session_state["raw_price"] = ""

# 전용면적 입력값 포맷팅 함수 정의
def format_area():
    raw = st.session_state.get("area_input", "")
    clean = re.sub(r"[^\d.]", "", raw)
    if clean and not raw.endswith("㎡"):
        st.session_state["area_input"] = f"{clean}㎡"

# 세션 초기값 선언
if "raw_price" not in st.session_state:
    st.session_state["raw_price"] = "0"

with st.expander("접기", expanded=True):
    address_input = st.text_input("주소", extracted_address, key="address_input")

    col1, col2 = st.columns(2)
    raw_price_input = col1.text_input("KB 시세 (만원)", key="raw_price", on_change=format_kb_price, args=())
    area_input = col2.text_input("전용면적 (㎡)", extracted_area, key="area_input", on_change=format_area, args=())

    floor_match = re.findall(r"제(\d+)층", address_input)
    floor_num = int(floor_match[-1]) if floor_match else None

    if floor_num is not None:
        if floor_num <= 2:
            st.markdown('<span style="color:red; font-weight:bold; font-size:18px">📉 하안가</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#007BFF; font-weight:bold; font-size:18px">📈 일반가</span>', unsafe_allow_html=True)

    if st.button("KB 시세 조회"):
        url = "https://kbland.kr/map?xy=37.5205559,126.9265729,17"
        st.components.v1.html(f"<script>window.open('{url}','_blank')</script>", height=0)

    # 👉 방공제 지역 & 방공제 금액 같은 줄에 붙이기
    col1, col2 = st.columns(2)
    region = col1.selectbox("방공제 지역 선택", [""] + list(region_map.keys()))
    default_d = region_map.get(region, 0)
    manual_d = col2.text_input("방공제 금액 (만)", f"{default_d:,}")
    deduction = int(re.sub(r"[^\d]", "", manual_d)) if manual_d else default_d

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

# 숫자 입력값을 쉼표로 포맷팅하는 함수
def format_with_comma(key):
    raw = st.session_state.get(key, "")
    clean = re.sub(r"[^\d]", "", raw)  # 숫자만 남기기
    if clean.isdigit():
        st.session_state[key] = "{:,}".format(int(clean))  # 쉼표 추가
    else:
        st.session_state[key] = ""  # 유효하지 않은 입력은 빈 문자열로 설정

# 대출 항목 입력
st.markdown("### 📝 대출 항목 입력")
rows = st.number_input("항목 개수", min_value=1, max_value=10, value=3)
items = []
for i in range(int(rows)):
    cols = st.columns(5)
    lender = cols[0].text_input("설정자", key=f"lender_{i}")
    max_amt_key = f"maxamt_{i}"
    cols[1].text_input(
        "채권최고액 (만)", 
        key=max_amt_key, 
        on_change=format_with_comma, 
        args=(max_amt_key,)
    )

    
    ratio = cols[2].text_input("설정비율 (%)", "120", key=f"ratio_{i}")
    try:
        calc = int(re.sub(r"[^\d]", "", st.session_state.get(max_amt_key, "0")) or 0) * 100 // int(ratio or 100)
    except:
        calc = 0
    principal_key = f"principal_{i}"
    cols[3].text_input(
        "원금", 
        key=principal_key, 
        value=f"{calc:,}",  # 기본값으로 계산된 값 표시
        on_change=format_with_comma, 
        args=(principal_key,)
    )
    status = cols[4].selectbox("진행구분", ["유지", "대환", "선말소"], key=f"status_{i}")
    items.append({
        "설정자": lender,
        "채권최고액": st.session_state.get(max_amt_key, ""),
        "설정비율": ratio,
        "원금": st.session_state.get(principal_key, ""),
        "진행구분": status
    })

# 계산
total_value = parse_korean_number(raw_price_input)
senior_principal_sum = sum(
    int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
    for item in items if item.get("진행구분") in ["대환", "선말소"]
)
sum_dh = sum(
    int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
    for item in items if item.get("진행구분") == "대환"
)
sum_sm = sum(
    int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
    for item in items if item.get("진행구분") == "선말소"
)

# 결과내용
text_to_copy = ""

owner_number = extract_owner_number_from_file(path)

text_to_copy = f"고객명: {owner_number}\n"
text_to_copy = f"주소: {address_input}\n" + text_to_copy

# 📍 일반가 / 하안가 여부 + KB시세
type_of_price = "📉 하안가" if floor_num and floor_num <= 2 else "📈 일반가"
text_to_copy += f"{type_of_price} | KB시세: {raw_price_input}만 | 전용면적: {area_input} | 방공제 금액: {deduction:,}만\n"

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
    text_to_copy += "\n📋 대출 항목\n"
    for item in valid_items:
        max_amt = int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
        principal_amt = int(re.sub(r"[^\d]", "", item.get("원금", "") or "0"))
        text_to_copy += f"{item['설정자']} | 채권최고액: {max_amt:,} | 비율: {item.get('설정비율', '0')}% | 원금: {principal_amt:,} | {item['진행구분']}\n"

# LTV 계산 함수 정의
def calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=True):
    if is_senior:
        # 선순위 계산
        limit = int(total_value * (ltv / 100) - deduction)
        available = int(limit - senior_principal_sum)
    else:
        # 후순위 계산
        limit = int(total_value * (ltv / 100) - maintain_maxamt_sum - deduction)
        available = int(limit - senior_principal_sum)
    
    # 10만 단위로 반올림
    limit = (limit // 10) * 10
    available = (available // 10) * 10
    return limit, available

# "유지"와 관련된 조건 미리 계산
has_maintain = any(item["진행구분"] == "유지" for item in items)
has_senior = any(item["진행구분"] in ["대환", "선말소"] for item in items)

# 💡 100 단위로 내림 처리하는 함수
def floor_to_unit(value, unit=100):
    return value // unit * unit

# ✅ 선순위 및 후순위 출력
for ltv in ltv_selected:
    # ✅ 선순위는 "유지"가 없을 때만 계산
    if has_senior and not has_maintain:
        limit_senior, avail_senior = calculate_ltv(
            total_value, deduction, senior_principal_sum, 0, ltv, is_senior=True
        )

        # ⬇️ 여기서 100단위로 버림
        limit_senior = floor_to_unit(limit_senior)
        avail_senior = floor_to_unit(avail_senior)

        text_to_copy += f"\n✅ 선순위 LTV {ltv}% ☞ 대출가능금액 {limit_senior:,} 가용 {avail_senior:,}"

    # ✅ 후순위는 "유지"가 있을 때만 계산
    if has_maintain:
        maintain_maxamt_sum = sum(
            int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
            for item in items if item["진행구분"] == "유지"
        )
        limit_sub, avail_sub = calculate_ltv(
            total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=False
        )

        # ⬇️ 여기서도 100단위로 버림
        limit_sub = floor_to_unit(limit_sub)
        avail_sub = floor_to_unit(avail_sub)

        text_to_copy += f"\n✅ 후순위 LTV {ltv}% ☞ 대출가능금액 {limit_sub:,} 가용 {avail_sub:,}"

# 📍 진행구분별 원금 합계
text_to_copy += "\n[진행구분별 원금 합계]\n"
if sum_dh > 0:
    text_to_copy += f"대환: {sum_dh:,}만\n"
if sum_sm > 0:
    text_to_copy += f"선말소: {sum_sm:,}만\n"

st.text_area("📋 결과 내용", value=text_to_copy, height=300)

# Streamlit UI
st.markdown("### 💰 컨설팅 및 브릿지 수수료 계산")

# ✅ 수수료 계산 함수 (입력과 결과 모두 '만' 단위 기준)
def calculate_fees(amount, rate):
    if amount and re.sub(r"[^\d]", "", amount).isdigit():
        # 입력값 숫자만 추출 → 만 단위 그대로 % 계산
        return int(re.sub(r"[^\d]", "", amount)) * rate / 100
    return 0

# ✅ 숫자 입력값을 쉼표로 포맷팅하는 함수 ('만' 단위 입력을 보기 좋게)
def format_with_comma(key):
    raw = st.session_state.get(key, "")
    clean = re.sub(r"[^\d]", "", raw)
    if clean.isdigit():
        st.session_state[key] = "{:,}".format(int(clean))
    else:
        st.session_state[key] = ""

# ✅ 입력 UI (명확하게 '만' 단위 입력)
col1, col2 = st.columns(2)
with col1:
    st.text_input("총 대출금액 (만)", key="total_loan", on_change=format_with_comma, args=("total_loan",))
with col2:
    consulting_rate = st.number_input("컨설팅 수수료율 (%)", value=1.5, step=0.1)

col3, col4 = st.columns(2)
with col3:
    st.text_input("브릿지 금액 (만)", key="bridge_amount", on_change=format_with_comma, args=("bridge_amount",))
with col4:
    bridge_rate = st.number_input("브릿지 수수료율 (%)", value=0.7, step=0.1)

# ✅ 계산 (세션에서 값을 꺼내 만 단위 계산)
consulting_fee = calculate_fees(st.session_state.get("total_loan", ""), consulting_rate)
bridge_fee = calculate_fees(st.session_state.get("bridge_amount", ""), bridge_rate)
total_fee = consulting_fee + bridge_fee

# ✅ 출력 (결과도 '만' 단위)
st.markdown(f"**컨설팅 비용:** {int(consulting_fee):,}만")
st.markdown(f"**브릿지 비용:** {int(bridge_fee):,}만")
st.markdown(f"🔗 **총 비용:** {int(total_fee):,}만")

# CSS를 활용한 UI 스타일 개선
st.markdown(
    """
    <style>
    /* 🎨 전체 앱 배경색 설정 */
    .stApp {
        background-color: #C7D3D4  /* 연한 회색-블루 배경 */
    }

    /* ✏️ 기본 입력 필드 (input, select, textarea) 스타일 */
    input, select, textarea {
        background-color: #F2EDD7                /* 흰 배경 */
        border: 1px solid #02343F               /* 연한 회색 테두리 */
        border-radius: 8px;                      /* 둥근 모서리 */
        padding: 10px;                           /* 내부 여백 */
        font-size: 14px;                         /* 글자 크기 */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);/* 아주 약한 그림자 */
        transition: border-color 0.3s ease, box-shadow 0.3s ease;  /* 포커스 시 부드러운 효과 */
    }

     # 입력 필드 포커스 시 스타일
    input:focus, select:focus, textarea:focus {
        border-color: #FCF6F5 /* 진한 파랑 */
        box-shadow: 0 0 8px rgba(0, 123, 255, 0.3); /* 파란 그림자 효과 */
    }

    /* 🔵 Streamlit 버튼 기본 스타일 */
    .stButton > button {
        background-color: #1F64FF;  /* 진하고 자연스러운 파랑 */
        color: white; /* 버튼 글자색 */
        border: 1px solid #1F64FF; /* 버튼 테두리 */
        border-radius: 6px; /* 둥근 모서리 */
        padding: 6px 14px; # 버튼 내부 여백
        font-size: 12px; # 글자 크기
        font-weight: 500; # 글자 두께
        cursor: pointer; # 마우스 커서 포인터로 변경
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 약한 그림자 */
        transition: background-color 0.2s ease, box-shadow 0.2s ease; /* 부드러운 효과 */
    }

    /* 🖱️ 버튼 위에 마우스 올렸을 때 */
    .stButton > button:hover {
        background: linear-gradient(90deg, #0056b3, #00539C);  # 버튼 색상 변화
        color: white; /* 버튼 글자색 */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);              /* 그림자 강조 */
    }

    /* ⬇️ 버튼 클릭 시 */
    .stButton > button:active { # 클릭 시 효과
        transform: scale(0.98);                /* 살짝 줄어드는 효과 */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);  /* 그림자 줄이기 */
    }
    </style>
    """,
    unsafe_allow_html=True
)
