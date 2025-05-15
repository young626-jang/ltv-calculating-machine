import re

def calculate_fees(amount, rate):
    if amount and re.sub(r"[^\d]", "", amount).isdigit():
        return int(re.sub(r"[^\d]", "", amount)) * rate / 100
    return 0

def format_with_comma(st, key):
    raw = st.session_state.get(key, "")
    clean = re.sub(r"[^\d]", "", raw)
    if clean.isdigit():
        st.session_state[key] = "{:,}".format(int(clean))
    else:
        st.session_state[key] = ""
