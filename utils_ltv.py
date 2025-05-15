import re
import streamlit as st

def parse_korean_number(text: str) -> int:
    """
    🔢 한글 숫자 문자열 파싱
    - '3억 500만' ➡ 30500
    - '2500만' ➡ 2500
    - '1,000' ➡ 1000
    """
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

def handle_ltv_ui_and_calculation(st, raw_price_input, deduction):
    """
    💰 대출 항목 입력 + LTV 계산 UI 및 결과 반환
    - 입력: raw_price_input, deduction
    - UI: 대출 항목, LTV 비율
    - 출력: LTV 결과 리스트, 대출 항목 리스트, 대환 원금 합계, 선말소 원금 합계
    """
    def format_with_comma(key):
        raw = st.session_state.get(key, "")
        clean = re.sub(r"[^\d]", "", raw)
        if clean.isdigit():
            st.session_state[key] = "{:,}".format(int(clean))
        else:
            st.session_state[key] = ""

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

    st.markdown("### 📝 대출 항목 입력")

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

    total_value = parse_korean_number(raw_price_input)
    senior_principal_sum = sum(
        int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
        for item in items if item.get("진행구분") in ["대환", "선말소"]
    )

    has_maintain = any(item["진행구분"] == "유지" for item in items)
    has_senior = any(item["진행구분"] in ["대환", "선말소"] for item in items)

    ltv_results = []
    loan_items = []
    sum_dh = sum(
        int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
        for item in items if item.get("진행구분") == "대환"
    )
    sum_sm = sum(
        int(re.sub(r"[^\d]", "", item.get("원금", "0")) or 0)
        for item in items if item.get("진행구분") == "선말소"
    )

    for ltv in ltv_selected:
        if has_senior and not has_maintain:
            limit_senior, avail_senior = calculate_ltv(total_value, deduction, senior_principal_sum, 0, ltv, is_senior=True)
            ltv_results.append(f"✅ 선순위 LTV {ltv}% ☞ 대출가능금액 {limit_senior:,}만 | 가용 {avail_senior:,}만")
        if has_maintain:
            maintain_maxamt_sum = sum(
                int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
                for item in items if item["진행구분"] == "유지"
            )
            limit_sub, avail_sub = calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=False)
            ltv_results.append(f"✅ 후순위 LTV {ltv}% ☞ 대출가능금액 {limit_sub:,}만 | 가용 {avail_sub:,}만")

    for item in items:
        max_amt = int(re.sub(r"[^\d]", "", item.get("채권최고액", "") or "0"))
        principal_amt = int(re.sub(r"[^\d]", "", item.get("원금", "") or "0"))
        loan_items.append(f"{item['설정자']} | 채권최고액: {max_amt:,} | 비율: {item.get('설정비율', '0')}% | 원금: {principal_amt:,} | {item['진행구분']}")

    return ltv_results, loan_items, sum_dh, sum_sm
