import streamlit as st
import re

def handle_fee_ui_and_calculation(st):
    """
    📋 컨설팅 및 브릿지 수수료 계산 UI + 계산 로직 (Streamlit UI)
    - 총 대출금액, 브릿지 금액 입력
    - 수수료율 입력
    - 결과 계산 및 표시
    """

    st.markdown("### 💰 컨설팅 및 브릿지 수수료 계산")

    # 💡 입력값을 '만' 단위로 계산하는 수수료 계산 함수
    def calculate_fees(amount, rate):
        if amount and re.sub(r"[^\d]", "", amount).isdigit():
            return int(re.sub(r"[^\d]", "", amount)) * rate / 100
        return 0

    # 💡 입력값을 숫자만 남기고 쉼표 포맷팅 (입력 보정용)
    def format_with_comma(key):
        raw = st.session_state.get(key, "")
        clean = re.sub(r"[^\d]", "", raw)
        if clean.isdigit():
            st.session_state[key] = "{:,}".format(int(clean))
        else:
            st.session_state[key] = ""

    # ➡ UI: 총 대출금, 브릿지 금액 입력
    col1, col2 = st.columns(2)
    col1.text_input("총 대출금액 (만)", key="total_loan", on_change=format_with_comma, args=("total_loan",))
    col2.text_input("브릿지 금액 (만)", key="bridge_amount", on_change=format_with_comma, args=("bridge_amount",))

    # ➡ UI: 수수료율 입력
    col3, col4 = st.columns(2)
    consulting_rate = col3.number_input("컨설팅 수수료율 (%)", value=1.5, step=0.1)
    bridge_rate = col4.number_input("브릿지 수수료율 (%)", value=0.7, step=0.1)

    # ➡ 계산
    consulting_fee = calculate_fees(st.session_state.get("total_loan", ""), consulting_rate)
    bridge_fee = calculate_fees(st.session_state.get("bridge_amount", ""), bridge_rate)
    total_fee = consulting_fee + bridge_fee

    # ➡ 결과 출력
    st.markdown(f"**컨설팅 비용:** {int(consulting_fee):,}만")
    st.markdown(f"**브릿지 비용:** {int(bridge_fee):,}만")
    st.markdown(f"🔗 **총 비용:** {int(total_fee):,}만")
