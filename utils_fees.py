import re

def calculate_fees(amount, rate):
    """
    수수료 계산 함수
    Args:
        amount (str or int): 금액 (숫자 또는 쉼표 포함 문자열)
        rate (float): 수수료율 (%)
    Returns:
        float: 계산된 수수료
    """
    try:
        # 금액에서 숫자만 추출
        clean_amount = re.sub(r"[^\d]", "", str(amount))
        if clean_amount.isdigit():
            return int(clean_amount) * rate / 100
        return 0
    except Exception as e:
        raise ValueError(f"수수료 계산 중 오류가 발생했습니다: {e}")

def format_with_comma(st, key):
    """
    숫자 입력값을 쉼표로 포맷팅하는 함수
    Args:
        st (module): Streamlit 모듈
        key (str): 세션 상태 키
    """
    try:
        # 세션 상태에서 값 가져오기
        raw = st.session_state.get(key, "")
        clean = re.sub(r"[^\d]", "", raw)  # 숫자만 남기기
        if clean.isdigit():
            st.session_state[key] = "{:,}".format(int(clean))  # 쉼표 추가
        else:
            st.session_state[key] = ""  # 유효하지 않은 입력은 빈 문자열로 설정
    except Exception as e:
        raise ValueError(f"숫자 포맷팅 중 오류가 발생했습니다: {e}")