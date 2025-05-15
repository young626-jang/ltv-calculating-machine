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
        col1, col2, col3, col4 = st.columns(4)

        # ✅ 설정자 입력
        lender = col1.text_input(f"설정자 {i+1}", key=f"lender_{i}", placeholder="예: 국민은행")

        # ✅ 채권최고액 입력
        max_amt_str = col2.text_input(f"채권최고액 (만) {i+1}", key=f"max_amt_{i}", placeholder="예: 100,000")

        # ✅ 설정비율 입력 (고정 초기값 120%)
        ratio_str = col3.text_input(f"설정비율 (%) {i+1}", key=f"ratio_{i}", value="120")

        # ✅ 진행구분 선택
        progress = col4.selectbox(f"진행구분 {i+1}", ["대환", "선말소", "유지"], key=f"progress_{i}")

        # 💡 채권최고액, 설정비율 값 변환 (예외 처리 포함)
        try:
            max_amt = int(max_amt_str.replace(",", "").strip())
        except:
            max_amt = 0

        try:
            ratio = int(ratio_str.replace(",", "").strip())
        except:
            ratio = 120

        # 💀 원금 필드: 세션 상태 관리 (value 대신 state 사용)
        principal_key = f"principal_{i}"
        if principal_key not in st.session_state:
            try:
                principal_amt = int(max_amt / (ratio / 100))
            except:
                principal_amt = 0
            st.session_state[principal_key] = f"{principal_amt:,}"

        # ✅ 원금 입력 (Session State만 사용)
        cols[3].text_input("원금", key=principal_key, placeholder="자동 계산 (필요시 수정 가능)")

        # 💡 설정자와 채권최고액 필수 입력 검증 후 loan_items에 추가
        if lender.strip() and max_amt > 0:
            loan_items.append(
                f"{lender} | 채권최고액: {max_amt:,} | 비율: {ratio}% | 원금: {st.session_state[principal_key]} | {progress}"
            )

            # 💡 진행구분별 합계 계산
            try:
                clean_principal_amt = int(st.session_state[principal_key].replace(",", "").strip())
            except:
                clean_principal_amt = 0

            if progress == "대환":
                sum_dh += clean_principal_amt
            elif progress == "선말소":
                sum_sm += clean_principal_amt

    # 💡 LTV 계산 (예외 처리 포함)
    if raw_price_input:
        try:
            price = int(raw_price_input.replace(",", ""))
            net_price = price - deduction
            ltv = (sum_dh + sum_sm) / net_price * 100 if net_price > 0 else 0
            ltv_results.append(f"LTV: {ltv:.2f}% (대환+선말소)")
        except:
            ltv_results.append("LTV 계산 불가")

    return ltv_results, loan_items, sum_dh, sum_sm
