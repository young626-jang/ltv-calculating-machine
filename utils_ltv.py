import streamlit as st

def handle_ltv_ui_and_calculation(st, raw_price_input, deduction):
    loan_items = []
    ltv_results = []
    sum_dh = 0
    sum_sm = 0

    num_loans = st.number_input("대출 항목 수", min_value=1, max_value=5, value=1, step=1)

    for i in range(num_loans):
        st.write(f"📋 대출 항목 {i + 1}")
        cols = st.columns(4)
        lender = cols[0].text_input(f"설정자 {i+1}", key=f"lender_{i}", placeholder="예: 국민은행")
        max_amt_str = cols[1].text_input(f"채권최고액 (만) {i+1}", key=f"max_amt_{i}", placeholder="예: 100,000")
        ratio_str = cols[2].text_input(f"설정비율 (%) {i+1}", key=f"ratio_{i}", value="120")

        try:
            max_amt = int(max_amt_str.replace(",", "").strip())
        except:
            max_amt = 0

        try:
            ratio = int(ratio_str.replace(",", "").strip())
        except:
            ratio = 120

        principal_key = f"principal_{i}"
        if principal_key not in st.session_state:
            try:
                principal_amt = int(max_amt / (ratio / 100))
            except:
                principal_amt = 0
            st.session_state[principal_key] = f"{principal_amt:,}"

        cols[3].text_input("원금", key=principal_key, placeholder="자동 계산 (필요시 수정 가능)")

        # 진행구분은 별도의 줄에서 깔끔하게
        progress = st.selectbox(f"진행구분 {i+1}", ["대환", "선말소", "유지"], key=f"progress_{i}")

        if lender.strip() and max_amt > 0:
            loan_items.append(
                f"{lender} | 채권최고액: {max_amt:,} | 비율: {ratio}% | 원금: {st.session_state[principal_key]} | {progress}"
            )
            try:
                clean_principal_amt = int(st.session_state[principal_key].replace(",", "").strip())
            except:
                clean_principal_amt = 0

            if progress == "대환":
                sum_dh += clean_principal_amt
            elif progress == "선말소":
                sum_sm += clean_principal_amt

    if raw_price_input:
        try:
            price = int(raw_price_input.replace(",", ""))
            net_price = price - deduction
            ltv = (sum_dh + sum_sm) / net_price * 100 if net_price > 0 else 0
            ltv_results.append(f"LTV: {ltv:.2f}% (대환+선말소)")
        except:
            ltv_results.append("LTV 계산 불가")

    return ltv_results, loan_items, sum_dh, sum_sm
