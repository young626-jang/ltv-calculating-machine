import streamlit as st

def handle_ltv_ui_and_calculation(st, raw_price_input, deduction):
    loan_items = []
    sum_dh = 0
    sum_sm = 0

    num_loans = st.number_input("대출 항목 수", min_value=1, max_value=5, value=3, step=1)

    for i in range(num_loans):
        st.write("📋 대출 항목")

        lender = st.text_input("설정자", key=f"lender_{i}")
        max_amt_str = st.text_input("채권최고액 (만)", key=f"max_amt_{i}")
        ratio_str = st.text_input("설정비율 (%)", key=f"ratio_{i}", value="120")

        try:
            max_amt = int(max_amt_str.replace(",", "").strip())
        except:
            max_amt = 0

        try:
            ratio = int(ratio_str.replace(",", "").strip())
        except:
            ratio = 120

        try:
            principal_amt = int(max_amt / (ratio / 100))
            principal_amt_formatted = f"{principal_amt:,}"
        except:
            principal_amt_formatted = "0"

        principal_key = f"principal_{i}"
        if principal_key not in st.session_state:
            st.session_state[principal_key] = principal_amt_formatted

        # 비율/최고액 변경 시 자동 업데이트
        if st.session_state.get(f"max_amt_{i}") != max_amt_str or st.session_state.get(f"ratio_{i}") != ratio_str:
            st.session_state[principal_key] = principal_amt_formatted

        principal_user_input = st.text_input("원금", key=principal_key)
        progress = st.selectbox("진행구분", ["대환", "선말소", "유지"], key=f"progress_{i}")

        try:
            clean_principal_amt = int(principal_user_input.replace(",", "").strip())
        except:
            clean_principal_amt = 0

        if lender.strip() and max_amt > 0:
            loan_items.append(
                f"{lender} | 채권최고액: {max_amt:,} | 비율: {ratio}% | 원금: {principal_user_input} | {progress}"
            )

            if progress == "대환":
                sum_dh += clean_principal_amt
            elif progress == "선말소":
                sum_sm += clean_principal_amt

    return loan_items, sum_dh, sum_sm
