from __future__ import annotations
from datetime import date
from src.data_structures.hash_table import HashTable
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
    def calculate_interest(principal: float,
                          interest_rate: float,
                          start_date: date,
                          end_date: date,
                          interest_type: InterestType = InterestType.COMPOUND_DAILY) -> float:
        """
        Tính lãi suất theo nhiều phương thức khác nhau.
        
        Args:
            principal: Số tiền gốc
            interest_rate: Lãi suất (dạng thập phân, ví dụ: 0.05 cho 5%)
            start_date: Ngày bắt đầu tính lãi
            end_date: Ngày kết thúc tính lãi
            interest_type: Loại lãi suất
            
        Returns:
            float: Số tiền lãi
        """
        if interest_rate <= 0 or principal <= 0:
            return 0.0
            
        days = (end_date - start_date).days
        if days <= 0:
            return 0.0
        
        if interest_type == InterestType.SIMPLE:
            # Lãi suất đơn: Interest = Principal * Rate * Time
            return round_money(principal * interest_rate * days / 365)
            
        elif interest_type == InterestType.COMPOUND_DAILY:
            # Lãi kép hàng ngày: A = P(1 + r)^t
            daily_rate = interest_rate / 365
            final_amount = principal * ((1 + daily_rate) ** days)
            return round_money(final_amount - principal)
            
        elif interest_type == InterestType.COMPOUND_MONTHLY:
            # Lãi kép hàng tháng
            months = days / 30.44  # Trung bình ngày/tháng
            monthly_rate = interest_rate / 12
            final_amount = principal * ((1 + monthly_rate) ** months)
            return round_money(final_amount - principal)
            
        elif interest_type == InterestType.COMPOUND_YEARLY:
            # Lãi kép hàng năm
            years = days / 365
            final_amount = principal * ((1 + interest_rate) ** years)
            return round_money(final_amount - principal)
            
        return 0.0

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
            
        return 0.0

    @staticmethod
    def calculate_total_debt(principal: float,
                           interest_rate: float,
                           penalty_rate: float,
                           borrow_date: date,
                           due_date: date,
                           current_date: date,
                           interest_type: InterestType = InterestType.COMPOUND_DAILY,
                           penalty_type: PenaltyType = PenaltyType.FIXED) -> HashTable[str, float]:
        """
        Tính tổng nợ bao gồm gốc, lãi và phí phạt.
        
        Returns:
            HashTable chứa breakdown chi tiết:
            {
                'principal': số tiền gốc,
                'interest': tiền lãi,
                'penalty': phí phạt,
                'total': tổng cộng
            }
        """
        interest = FinancialCalculator.calculate_interest(
            principal, interest_rate, borrow_date, current_date, interest_type
        )
        
        penalty = FinancialCalculator.calculate_penalty(
            principal, penalty_rate, due_date, current_date, penalty_type
        )
        
        total = round_money(principal + interest + penalty)
        
        return {
            'principal': round_money(principal),
            'interest': interest,
            'penalty': penalty,
            'total': total
        }

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