import streamlit as st

def handle_ltv_ui_and_calculation(st, raw_price_input, deduction):
    # 📋 대출 항목 입력 & 계산 준비
    loan_items = []
    ltv_results = []
    sum_dh = 0
    sum_sm = 0

    # ➡ 대출 항목 개수 입력
    num_loans = st.number_input("대출 항목 수", min_value=1, max_value=5, value=1, step=1)

    for i in range(num_loans):
        st.write(f"📋 대출 항목 {i + 1}")

        # 💡 필수: 4열로 column 배치 (정확 선언)
        cols = st.columns(4)

        # ✅ 설정자 입력
        lender = cols[0].text_input(f"설정자 {i+1}", key=f"lender_{i}", placeholder="예: 국민은행")

        # ✅ 채권최고액 입력
        max_amt_str = cols[1].text_input(f"채권최고액 (만) {i+1}", key=f"max_amt_{i}", placeholder="예: 100,000")

        # ✅ 설정비율 입력
        ratio_str = cols[2].text_input(f"설정비율 (%) {i+1}", key=f"ratio_{i}", value="120")

        # 💡 값 검증 및 숫자 변환 (예외 처리)
        try:
            max_amt = int(max_amt_str.replace(",", "").strip())
        except:
            max_amt = 0

        try:
            ratio = int(ratio_str.replace(",", "").strip())
        except:
            ratio = 120

        # ✅ 원금 (Session State만 사용, value= 안 씀)
        principal_key = f"principal_{i}"
        if principal_key not in st.session_state:
            try:
                principal_amt = int(max_amt / (ratio / 100))
            except:
                principal_amt = 0
            st.session_state[principal_key] = f"{principal_amt:,}"

        cols[3].text_input("원금", key=principal_key, placeholder="자동 계산 (필요시 수정 가능)")

        # ✅ 진행구분 (selectbox)
        progress = cols[3].selectbox(f"진행구분 {i+1}", ["대환", "선말소", "유지"], key=f"progress_{i}")

        # 💡 설정자 + 채권최고액이 입력된 경우에만 항목 추가
        if lender.strip() and max_amt > 0:
            loan_items.append(
                f"{lender} | 채권최고액: {max_amt:,} | 비율: {ratio}% | 원금: {st.session_state[principal_key]} | {progress}"
            )

            # 💀 진행구분에 따라 합계 계산 (Session state 원금 사용)
            try:
                clean_principal_amt = int(st.session_state[principal_key].replace(",", "").strip())
            except:
                clean_principal_amt = 0

            if progress == "대환":
                sum_dh += clean_principal_amt
            elif progress == "선말소":
                sum_sm += clean_principal_amt

    # ➡ LTV 계산 (방공제 고려)
    if raw_price_input:
        try:
            price = int(raw_price_input.replace(",", ""))
            net_price = price - deduction
            ltv = (sum_dh + sum_sm) / net_price * 100 if net_price > 0 else 0
            ltv_results.append(f"LTV: {ltv:.2f}% (대환+선말소)")
        except:
            ltv_results.append("LTV 계산 불가")

    return ltv_results, loan_items, sum_dh, sum_sm
