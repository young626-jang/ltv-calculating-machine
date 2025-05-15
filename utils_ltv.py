def calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=True):
    """
    LTV 계산 함수
    Args:
        total_value (int): 총 자산 가치
        deduction (int): 방공제 금액
        senior_principal_sum (int): 선순위 원금 합계
        maintain_maxamt_sum (int): 유지 채권최고액 합계
        ltv (float): LTV 비율
        is_senior (bool): 선순위 여부 (True: 선순위, False: 후순위)
    Returns:
        tuple: (limit, available) 대출 한도와 가용 금액
    """
    try:
        if is_senior:
            limit = int(total_value * (ltv / 100) - deduction)
            available = int(limit - senior_principal_sum)
        else:
            limit = int(total_value * (ltv / 100) - maintain_maxamt_sum - deduction)
            available = int(limit - senior_principal_sum)

        # 10 단위로 내림 처리
        limit = floor_to_unit(limit, 10)
        available = floor_to_unit(available, 10)

        return limit, available
    except Exception as e:
        raise ValueError(f"LTV 계산 중 오류가 발생했습니다: {e}")


def floor_to_unit(value, unit=100):
    """
    주어진 값을 특정 단위로 내림 처리
    Args:
        value (int): 처리할 값
        unit (int): 단위 (기본값: 100)
    Returns:
        int: 단위로 내림 처리된 값
    """
    try:
        return value // unit * unit
    except Exception as e:
        raise ValueError(f"값을 단위로 내림 처리하는 중 오류가 발생했습니다: {e}")