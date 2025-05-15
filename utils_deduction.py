import re
from ltv_map import region_map

def get_deduction_ui(st):
    # 두 개의 열로 UI 구성
    col1, col2 = st.columns(2)

    # 방공제 지역 선택
    region = col1.selectbox("방공제 지역 선택", [""] + list(region_map.keys()), help="방공제 지역을 선택하세요.")
    default_deduction = region_map.get(region, 0)

    # 방공제 금액 입력
    manual_deduction = col2.text_input(
        "방공제 금액 (만)",
        value=f"{default_deduction:,}",
        placeholder="숫자를 입력하세요.",
        help="방공제 금액을 직접 입력하거나 지역 선택에 따른 기본값을 사용할 수 있습니다."
    )

    # 입력값 검증 및 최종 방공제 금액 계산
    try:
        deduction = int(re.sub(r"[^\d]", "", manual_deduction)) if manual_deduction else default_deduction
    except ValueError:
        deduction = default_deduction
        st.warning("유효한 숫자를 입력하세요.")

    return deduction