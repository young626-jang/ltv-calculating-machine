import re
import streamlit as st

def handle_ltv_ui_and_calculation(st, raw_price_input, deduction):
    """
    📋 대출 항목 입력 + LTV 계산 UI + 결과 표시 (Streamlit UI)
    - 입력된 KB 시세, 방공제 금액 기준으로
    - 대출 항목 입력 → 선순위/후순위 LTV 계산
    """
    # 입력값 파싱 함수 (한글 숫자 포함)
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

    # 🔢 숫자 입력 포맷팅 (쉼표 추가)
    def format_with_comma(key):
        raw = st.session_state.get(key, "")
        clean = re.sub(r"[^\d]", "", raw)
        if clean.isdigit():
            st.session_state[key] = "{:,}".format(int(clean))
        else:
            st.session_state[key] = ""

    # 💰 LTV 계산 함수
    def calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=True):
        if is_senior:
            limit = int(total_value * (ltv / 100) - deduction)
            available = int(limit - senior_principal_sum)
        else:
            limit = int(total_value * (ltv / 100) - maintain_maxamt_sum - deduction)
            available = int(limit - senior_principal_sum)
        limit = (limit // 10) * 10
        available = (available // 10) * 10
        return limit, available

    # UI 시작
    st.markdown("### 📝 대출 항목 입력")

    # LTV 비율 입력 UI
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

    # 대출 항목 입력 UI
    rows = st.number_input("항목 개수", min_value=1, max_value=10, value=3)
    items = []
    for i in range(int(rows)):
        cols = st.columns(5)
        lender = cols[0].text_input("설정자", key=f"lender_{i}")
        max_amt_key = f"maxamt_{i}"
        cols[1].text_input("채권최고액 (만)", key=max_amt_key, on_change=format_with_comma, args=(max_amt_key,))
        ratio = cols[2].text_input("설정비율 (%)", "120", key=f"ratio_{i}")
        try:
            calc = int(re.sub(r"[^\d]", "", st.session_state.get(max_amt_key, "0")) or 0) * 100 // int(ratio or 100)
        except:
            calc = 0
        principal_key = f"principal_{i}"
        cols[3].text_input("원금", key=principal_key, value=f"{calc:,}", on_change=format_with_comma, args=(principal_key,))
        status = cols[4].selectbox("진행구분", ["유지", "대환", "선말소"], key=f"status_{i}")
        items.append({
            "설정자": lender,
            "채권최고액": st.session_state.get(max_amt_key, ""),
            "설정비율": ratio,
            "원금": st.session_state.get(principal_key, ""),
            "진행구분": status
        })

    # 입력값 계산
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
            st.markdown(f"✅ 선순위 LTV {ltv}%: 대출가능 {limit_senior:,}만 | 가용 {avail_senior:,}만")
        if has_maintain:
            maintain_maxamt_sum = sum(
                int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
                for item in items if item["진행구분"] == "유지"
            )
            limit_sub, avail_sub = calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=False)
            st.markdown(f"✅ 후순위 LTV {ltv}%: 대출가능 {limit_sub:,}만 | 가용 {avail_sub:,}만")
