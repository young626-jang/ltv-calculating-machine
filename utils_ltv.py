import streamlit as st
from utils_format import format_input_with_comma

def handle_ltv_ui_and_calculation(st, raw_price_input, deduction):
    loan_items = []
    ltv_results = []
    sum_dh = 0
    sum_sm = 0

    num_loans = st.number_input("대출 항목 수", min_value=1, max_value=5, value=3, step=1)

    for i in range(num_loans):
        st.write(f"📋 대출 항목 {i + 1}")
        cols = st.columns(5)

        lender_key = f"lender_{i}"
        max_amt_key = f"max_amt_{i}"
        ratio_key = f"ratio_{i}"
        principal_key = f"principal_{i}"
        progress_key = f"progress_{i}"

        # 채권최고액 입력
        cols[0].text_input("설정자", key=lender_key, placeholder="")
        cols[1].text_input("채권최고액 (만)", key=max_amt_key, on_change=format_input_with_comma, args=(max_amt_key, st), placeholder="숫자 입력")

        # ✅ 설정비율 변경 시 원금 자동 계산 (원금은 수동 입력도 가능)
        def update_principal_from_ratio():
            try:
                current_max = int(st.session_state.get(max_amt_key, "0").replace(",", "").strip())
                current_ratio = int(st.session_state.get(ratio_key, "120").replace(",", "").strip())
                if current_ratio > 0:
                    st.session_state[principal_key] = "{:,}".format(int(current_max / (current_ratio / 100)))
            except:
                st.session_state[principal_key] = "0"

        cols[2].text_input("설정비율 (%)", key=ratio_key, on_change=update_principal_from_ratio, placeholder="비율 입력", value="120")

        # ✅ 원금 필드는 자동 계산 후에도 사용자가 직접 덮어쓰기 가능
        if principal_key not in st.session_state:
            try:
                initial_max = int(st.session_state.get(max_amt_key, "0").replace(",", "").strip())
                initial_ratio = int(st.session_state.get(ratio_key, "120").replace(",", "").strip())
                st.session_state[principal_key] = "{:,}".format(int(initial_max / (initial_ratio / 100))) if initial_ratio else "0"
            except:
                st.session_state[principal_key] = "0"

        cols[3].text_input("원금", key=principal_key, on_change=format_input_with_comma, args=(principal_key, st), placeholder="자동 계산 (필요시 직접 수정)")
        cols[4].selectbox("진행구분", ["대환", "선말소", "유지"], key=progress_key)

        lender = st.session_state.get(lender_key, "")
        progress = st.session_state.get(progress_key, "대환")

        try:
            max_amt = int(st.session_state.get(max_amt_key, "0").replace(",", "").strip())
        except:
            max_amt = 0

        try:
            ratio = int(st.session_state.get(ratio_key, "120").replace(",", "").strip())
        except:
            ratio = 120

        try:
            clean_principal_amt = int(st.session_state[principal_key].replace(",", "").strip())
        except:
            clean_principal_amt = 0

        if lender.strip() and max_amt > 0:
            loan_items.append(
                f"{lender} | 채권최고액: {max_amt:,} | 비율: {ratio}% | 원금: {st.session_state[principal_key]} | {progress}"
            )

            if progress == "대환":
                sum_dh += clean_principal_amt
            elif progress == "선말소":
                sum_sm += clean_principal_amt

    if raw_price_input:
        try:
            price = int(raw_price_input.replace(",", "").strip())
            net_price = price - deduction
            ltv = (sum_dh + sum_sm) / net_price * 100 if net_price > 0 else 0
            ltv_results.append(f"LTV: {ltv:.2f}% (대환+선말소)")
        except:
            ltv_results.append("LTV 계산 불가")

    return ltv_results, loan_items, sum_dh, sum_sm
