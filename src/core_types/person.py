from __future__ import annotations

from datetime import date
from .transaction import AdvancedTransaction # Import AdvancedTransaction

from src.data_structures.linked_list import LinkedList

# Đây là mô-đun chứa định nghĩa lớp Person.

class Person:
    """
    Đại diện cho một người (cá nhân hoặc tổ chức) tham gia vào các giao dịch nợ.
    Lưu trữ tên, số dư tổng hợp, và có thể tham chiếu đến các giao dịch liên quan.
    Các thuộc tính như earliest_due_date và highest_interest_rate được sử dụng cho các thuật toán ưu tiên.
    """
    def __init__(self, name: str):
        self.name: str = name
        self.balance: float = 0.0 # Số dư tổng hợp của người này, được cập nhật bởi các thuật toán đơn giản hóa.
                                  # Số dư âm nghĩa là nợ, số dư dương nghĩa là có.
        
        # Sử dụng chuỗi 'LinkedList[AdvancedTransaction]' cho type hint để tránh import vòng.
        # Sẽ được khởi tạo với một đối tượng LinkedList thực khi cần.
        self.transactions: 'LinkedList[AdvancedTransaction]' | None = None
        self.earliest_due_date: date | None = None # Ngày đến hạn sớm nhất của các khoản NỢ của người này.
        self.highest_interest_rate: float = 0.0 # Lãi suất cao nhất của các khoản NỢ của người này.

    def __str__(self) -> str:
        """Trả về biểu diễn chuỗi thân thiện của đối tượng Person."""
        return f"Person: {self.name}, Balance: {self.balance:.2f}"

    def __repr__(self) -> str:
        """Trả về biểu diễn chuỗi chính thức của đối tượng Person."""
        return f"Person(name='{self.name}')"

    def add_transaction_reference(self, transaction: AdvancedTransaction) -> None:
        """Thêm tham chiếu đến một giao dịch liên quan đến người này.
        Nếu người này là NGƯỜI MẮC NỢ trong giao dịch, cập nhật earliest_due_date và highest_interest_rate.
        """
        # Import LinkedList ở đây để tránh phụ thuộc vòng ở mức module.
        from src.data_structures.linked_list import LinkedList

        if self.transactions is None: # Khởi tạo LinkedList nếu nó chưa tồn tại
            self.transactions = LinkedList[AdvancedTransaction]()
        
        # Hiện tại, Person.transactions không được sử dụng nhiều trong logic chính sau khi tạo,
        # nhưng được giữ lại cho các mở rộng tiềm năng hoặc gỡ lỗi.

        # Chỉ cập nhật thông tin nếu người này là NGƯỜI MẮC NỢ trong giao dịch.
        if transaction.debtor == self.name:
            if self.earliest_due_date is None or transaction.due_date < self.earliest_due_date:
                self.earliest_due_date = transaction.due_date
            
            if transaction.interest_rate > self.highest_interest_rate:
                self.highest_interest_rate = transaction.interest_rate

    def update_balance(self, amount: float) -> None:
        """Cập nhật số dư của người này.
        `amount`: số tiền để thay đổi số dư (dương để tăng, âm để giảm).
        """
        self.balance += amount 