import re

def format_input_with_comma(key, st):
    """
    사용자가 입력한 금액 필드에 자동 콤마 적용
    """
    raw = st.session_state.get(key, "")
    clean = re.sub(r"[^\d]", "", raw)
    if clean:
        st.session_state[key] = "{:,}".format(int(clean))
    else:
        st.session_state[key] = ""
