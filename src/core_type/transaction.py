from __future__ import annotations

from datetime import date
from src.data_structures.hash_table import HashTable
from src.utils.financial_calculator import FinancialCalculator, InterestType, PenaltyType
# Đây là mô-đun chứa định nghĩa lớp Transaction.

class AdvancedTransaction:
    """
    Đại diện cho một giao dịch nợ nâng cao với đầy đủ thông tin tài chính.
    Sử dụng FinancialCalculator để xử lý các tính toán phức tạp.
    """
    
    def __init__(self, 
                 debtor: str,
                 creditor: str,
                 amount: float,
                 borrow_date: date,
                 due_date: date,
                 interest_rate: float = 0.0,
                 penalty_rate: float = 0.0,
                 interest_type: InterestType = InterestType.COMPOUND_DAILY,
                 penalty_type: PenaltyType = PenaltyType.FIXED):
        
        if amount <= 1e-9:
            raise ValueError("Số tiền giao dịch phải lớn hơn 0.")
        if interest_rate < 0:
            raise ValueError("Lãi suất không thể âm.")
        if penalty_rate < 0:
            raise ValueError("Phí phạt không thể âm.")
        if due_date < borrow_date:
            raise ValueError("Ngày đến hạn không thể trước ngày vay.")
            
        self.debtor = debtor
        self.creditor = creditor
        self.amount = amount
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.interest_rate = interest_rate
        self.penalty_rate = penalty_rate
        self.interest_type = interest_type
        self.penalty_type = penalty_type

    def get_debt_breakdown(self, current_date: date) -> dict:
        return FinancialCalculator.calculate_total_debt(
            self.amount, self.interest_rate, self.penalty_rate,
            self.borrow_date, self.due_date, current_date,
            self.interest_type, self.penalty_type
        )

    def calculate_total_debt(self, current_date: date) -> float:
        """
        Tính tổng nợ thực tế tại thời điểm hiện tại.
        
        Args:
            current_date: Ngày hiện tại để tính toán
            
        Returns:
            float: Tổng số tiền nợ thực tế
        """
        breakdown = self.get_debt_breakdown(current_date)
        return breakdown['total']

    def get_priority_score(self, current_date: date) -> float:
        """
        Tính điểm ưu tiên cho giao dịch này.
        
        Returns:
            float: Điểm ưu tiên (càng cao càng được ưu tiên)
        """
        return FinancialCalculator.calculate_priority_score(
            self.amount, self.interest_rate, self.penalty_rate,
            self.borrow_date, self.due_date, current_date,
            self.interest_type, self.penalty_type
        )

    def is_overdue(self, current_date: date) -> bool:
        """Kiểm tra xem giao dịch có quá hạn không."""
        return current_date > self.due_date

    def days_overdue(self, current_date: date) -> int:
        """Tính số ngày quá hạn."""
        if not self.is_overdue(current_date):
            return 0
        return (current_date - self.due_date).days


class BasicTransaction:
    """
    Đại diện cho một giao dịch nợ cơ bản giữa hai bên.
    Bao gồm thông tin về người mắc nợ, người cho vay, số tiền
    """
    def __init__(self, 
                 debtor: str,         # Tên người nợ
                 creditor: str,       # Tên người cho vay
                 amount: float):      # Số tiền của giao dịch
        
        if amount <= 1e-9: # Sử dụng ngưỡng nhỏ cho số tiền dương
            raise ValueError("Số tiền giao dịch phải lớn hơn 0.")
            
        self.debtor = debtor
        self.creditor = creditor
        self.amount = amount