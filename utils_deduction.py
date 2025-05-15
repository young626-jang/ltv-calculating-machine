import re
from ltv_map import region_map
from utils_format import format_input_with_comma

def get_deduction_ui(st):
    col1, col2 = st.columns(2)

    region = col1.selectbox("방공제 지역 선택", [""] + list(region_map.keys()), help="방공제 지역을 선택하세요.")
    default_deduction = region_map.get(region, 0)

    col2.text_input(
        "방공제 금액 (만)",
        key="manual_deduction",
        value=f"{default_deduction:,}",
        on_change=format_input_with_comma,
        args=("manual_deduction", st),
        placeholder="숫자를 입력하세요.",
    )

    deduction = int(re.sub(r"[^\d]", "", st.session_state.get("manual_deduction", ""))) if st.session_state.get("manual_deduction", "") else default_deduction

    return deduction
