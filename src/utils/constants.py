EPSILON = 1e-9

def round_money(amount: float) -> float:
    """
    Làm tròn số tiền đến 2 chữ số thập phân.
    
    Args:
        amount: Số tiền cần làm tròn
        
    Returns:
        float: Số tiền đã được làm tròn
    """
    return round(amount, 2)