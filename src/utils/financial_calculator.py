from __future__ import annotations
from datetime import date
from src.utils.money_utils import round_money
from enum import Enum

class InterestType(Enum):
    """Enum định nghĩa các loại lãi suất"""
    SIMPLE = "simple"           # Lãi suất đơn
    COMPOUND_DAILY = "compound_daily"     # Lãi suất kép theo ngày
    COMPOUND_MONTHLY = "compound_monthly" # Lãi suất kép theo tháng
    COMPOUND_YEARLY = "compound_yearly"   # Lãi suất kép theo năm


class PenaltyType(Enum):
    """Enum định nghĩa các loại phí phạt"""
    FIXED = "fixed"             # Phí phạt cố định một lần
    DAILY = "daily"             # Phí phạt theo ngày
    PERCENTAGE = "percentage"   # Phí phạt theo phần trăm của nợ gốc


class FinancialCalculator:
    """
    Class chuyên dụng để tính toán các yếu tố tài chính:
    - Lãi suất (đơn, kép theo các chu kỳ khác nhau)
    - Phí phạt (cố định, theo ngày, theo phần trăm)
    - Điểm ưu tiên dựa trên các yếu tố tài chính
    
    Class này có thể được tái sử dụng trong nhiều thuật toán khác nhau.
    """
    
    @staticmethod
    def calculate_interest(amount, interest_rate, borrow_date, current_date, interest_type):
        days = (current_date - borrow_date).days
        months = (current_date.year - borrow_date.year) * 12 + (current_date.month - borrow_date.month)
        if interest_type == InterestType.SIMPLE:
            years = days / 365
            return amount * interest_rate * years

        elif interest_type == InterestType.COMPOUND_MONTHLY:
            # lãi kép hàng tháng
            return amount * ((1 + interest_rate / 12) ** months - 1)

        elif interest_type == InterestType.COMPOUND_DAILY:
            return amount * ((1 + interest_rate / 365) ** days - 1)

        else:
            return 0.0

    @staticmethod
    def calculate_penalty(amount, penalty_rate, due_date, current_date, penalty_type):
        if current_date <= due_date:
            return 0.0
        if penalty_type == PenaltyType.FIXED:
            return penalty_rate
        elif penalty_type == PenaltyType.PERCENTAGE:
            return amount * penalty_rate
        else:
            return 0.0

    @staticmethod
    def calculate_total_debt(amount, interest_rate, penalty_rate, borrow_date, due_date, current_date, interest_type, penalty_type):
        interest = FinancialCalculator.calculate_interest(amount, interest_rate, borrow_date, current_date, interest_type)
        penalty = FinancialCalculator.calculate_penalty(amount, penalty_rate, due_date, current_date, penalty_type)
        total = amount + interest + penalty
        return {
            'principal': amount,
            'interest': interest,
            'penalty': penalty,
            'total': total
        }


    @staticmethod
    def calculate_penalty(principal: float,
                         penalty_rate: float,
                         due_date: date,
                         current_date: date,
                         penalty_type: PenaltyType = PenaltyType.FIXED) -> float:
        """
        Tính phí phạt theo nhiều phương thức khác nhau.
        
        Args:
            principal: Số tiền gốc
            penalty_rate: Mức phí phạt
            due_date: Ngày đến hạn
            current_date: Ngày hiện tại
            penalty_type: Loại phí phạt
            
        Returns:
            float: Số tiền phí phạt
        """
        if current_date <= due_date:
            return 0.0  # Chưa quá hạn
            
        overdue_days = (current_date - due_date).days
        
        if penalty_type == PenaltyType.FIXED:
            # Phí phạt cố định một lần
            return round_money(penalty_rate)
            
        elif penalty_type == PenaltyType.DAILY:
            # Phí phạt theo ngày quá hạn
            return round_money(penalty_rate * overdue_days)
            
        elif penalty_type == PenaltyType.PERCENTAGE:
            # Phí phạt theo phần trăm của số tiền gốc
            return round_money(principal * penalty_rate)

    @staticmethod
    def calculate_priority_score(principal: float,
                               interest_rate: float,
                               penalty_rate: float,
                               borrow_date: date,
                               due_date: date,
                               current_date: date,
                               interest_type: InterestType = InterestType.COMPOUND_DAILY,
                               penalty_type: PenaltyType = PenaltyType.FIXED) -> float:
        """
        Tính điểm ưu tiên cho giao dịch dựa trên các yếu tố tài chính.
        
        Các yếu tố ảnh hưởng:
        - Tổng nợ thực tế (cao hơn = ưu tiên cao hơn)
        - Độ gần với ngày đến hạn
        - Tốc độ tăng trưởng lãi suất
        - Mức độ phí phạt
        
        Returns:
            float: Điểm ưu tiên (càng cao càng được ưu tiên xử lý trước)
        """
        debt_breakdown = FinancialCalculator.calculate_total_debt(
            principal, interest_rate, penalty_rate, borrow_date, due_date, 
            current_date, interest_type, penalty_type
        )
        
        # Trọng số cơ bản dựa trên tổng nợ
        base_weight = debt_breakdown['total']
        
        # Trọng số thời gian (càng gần đến hạn hoặc đã quá hạn càng cao)
        days_to_due = (due_date - current_date).days
        if days_to_due <= 0:
            # Đã quá hạn - ưu tiên rất cao
            time_weight = 2.0 + min(abs(days_to_due) / 30, 5.0)  # Tối đa 7x
        else:
            # Chưa đến hạn - ưu tiên dựa trên độ gần
            time_weight = max(0.5, 2.0 / max(1, days_to_due / 30))
        
        # Trọng số lãi suất (lãi suất cao = ưu tiên cao)
        interest_weight = 1.0 + interest_rate * 10  # Chuyển đổi thành hệ số
        
        # Trọng số phí phạt
        penalty_weight = 1.0
        if penalty_type != PenaltyType.FIXED and penalty_rate > 0:
            penalty_weight = 1.0 + penalty_rate * 5
        
        # Điểm ưu tiên tổng hợp
        priority_score = base_weight * time_weight * interest_weight * penalty_weight
        
        return round_money(priority_score)
    