def calculate_ltv(total_value, deduction, senior_principal_sum, maintain_maxamt_sum, ltv, is_senior=True):
    if is_senior:
        limit = int(total_value * (ltv / 100) - deduction)
        available = int(limit - senior_principal_sum)
    else:
        limit = int(total_value * (ltv / 100) - maintain_maxamt_sum - deduction)
        available = int(limit - senior_principal_sum)
    limit = (limit // 10) * 10
    available = (available // 10) * 10
    return limit, available

def floor_to_unit(value, unit=100):
    return value // unit * unit
