import re
from ltv_map import region_map

def get_deduction_ui(st):
    col1, col2 = st.columns(2)
    region = col1.selectbox("방공제 지역 선택", [""] + list(region_map.keys()))
    default_d = region_map.get(region, 0)
    manual_d = col2.text_input("방공제 금액 (만)", f"{default_d:,}")
    deduction = int(re.sub(r"[^\d]", "", manual_d)) if manual_d else default_d
    return deduction
