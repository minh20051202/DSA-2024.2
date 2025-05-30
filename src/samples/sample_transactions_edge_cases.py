"""
Dữ liệu giao dịch mẫu cho các trường hợp biên và kịch bản cụ thể,
dành cho việc kiểm thử các thuật toán giảm thiểu số lượng giao dịch.
"""
from datetime import date
from src.core_types import Transaction
from src.data_structures import LinkedList
from src.utils.money_utils import round_money

# Một ngày cố định cho các giao dịch mẫu này để đơn giản
fixed_date = Date(1, 1, 2025)

def get_no_transactions() -> LinkedList[Transaction]:
    """Trả về một danh sách rỗng các giao dịch."""
    return LinkedList[Transaction]()

def get_one_transaction() -> LinkedList[Transaction]:
    """Trả về một danh sách với một giao dịch duy nhất."""
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Alice", "Bob", 100.0, fixed_date, fixed_date, status="Đơn lẻ"))
    return transactions

def get_direct_cancel_out_transactions() -> LinkedList[Transaction]:
    """Giao dịch trực tiếp triệt tiêu lẫn nhau (A->B 50, B->A 50)."""
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Charlie", "David", 50.0, fixed_date, fixed_date, status="Triệt tiêu 1"))
    transactions.append(Transaction("David", "Charlie", 50.0, fixed_date, fixed_date, status="Triệt tiêu 2"))
    return transactions

def get_direct_partial_settlement_transactions() -> LinkedList[Transaction]:
    """Giao dịch trực tiếp quyết toán một phần (A->B 50, B->A 30 => A->B 20)."""
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Eve", "Frank", 50.0, fixed_date, fixed_date, status="Một phần 1"))
    transactions.append(Transaction("Frank", "Eve", 30.0, fixed_date, fixed_date, status="Một phần 2"))
    return transactions
    
def get_simple_cycle_transactions() -> LinkedList[Transaction]:
    """Một chu trình đơn giản (A->B 20, B->C 20, C->A 20) => 0 giao dịch."""
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Gabe", "Hana", 20.0, fixed_date, fixed_date, status="Chu trình 1"))
    transactions.append(Transaction("Hana", "Ian", 20.0, fixed_date, fixed_date, status="Chu trình 2"))
    transactions.append(Transaction("Ian", "Gabe", 20.0, fixed_date, fixed_date, status="Chu trình 3"))
    return transactions

def get_simple_chain_transactions() -> LinkedList[Transaction]:
    """Một chuỗi đơn giản (A->B 10, B->C 10, C->D 10) => A->D 10 (nếu chỉ có 3 người và D là A), hoặc giữ nguyên nếu A,B,C,D riêng biệt."""
    # Với mục tiêu giảm thiểu giao dịch, A->B, B->C, C->D có thể không được đơn giản hóa thêm
    # trừ khi có sự chồng chéo chủ nợ/người nợ cuối cùng.
    # Nếu nó là A->B, B->C, C->A thì đó là một chu trình.
    # Nếu A,B,C,D là riêng biệt, và không có cách nào gộp lại, nó sẽ là 3 giao dịch.
    # Để cho rõ ràng, hãy tạo một trường hợp mà nó sẽ đơn giản hóa: A->B, B->C (=> A->C).
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Jack", "Kate", 10.0, fixed_date, fixed_date, status="Chuỗi 1"))
    transactions.append(Transaction("Kate", "Liam", 10.0, fixed_date, fixed_date, status="Chuỗi 2"))
    # Dự kiến: Jack -> Liam 10.0 (1 giao dịch)
    return transactions

def get_chain_leading_to_cycle_resolution() -> LinkedList[Transaction]:
    """ A->B, B->C, C->A (chu trình) và D->A (thêm 1) """
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Mono", "Nina", 30.0, fixed_date, fixed_date, status="Chu trình M-N"))
    transactions.append(Transaction("Nina", "Oscar", 30.0, fixed_date, fixed_date, status="Chu trình N-O"))
    transactions.append(Transaction("Oscar", "Mono", 30.0, fixed_date, fixed_date, status="Chu trình O-M")) # Chu trình này nên triệt tiêu
    transactions.append(Transaction("Pria", "Mono", 50.0, fixed_date, fixed_date, status="P-M")) 
    # Dự kiến: Pria -> Mono 50.0 (1 giao dịch)
    return transactions

def get_multiple_disjoint_settlements() -> LinkedList[Transaction]:
    """Hai cặp giao dịch riêng biệt, không liên quan (A->B, X->Y)."""
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("Quinn", "Rob", 70.0, fixed_date, fixed_date, status="Tách biệt 1"))
    transactions.append(Transaction("Sam", "Tom", 80.0, fixed_date, fixed_date, status="Tách biệt 2"))
    # Dự kiến: 2 giao dịch không thay đổi
    return transactions

def get_complex_case_1() -> LinkedList[Transaction]:
    """Một trường hợp phức tạp hơn một chút."""
    # A nợ B 10, B nợ C 20, C nợ A 5
    # A: -10 (cho B) + 5 (từ C) = -5
    # B: +10 (từ A) - 20 (cho C) = -10
    # C: +20 (từ B) - 5 (cho A) = +15
    # Kết quả: A -> C 5, B -> C 10 (2 giao dịch)
    transactions = LinkedList[Transaction]()
    transactions.append(Transaction("UserA", "UserB", 10.0, fixed_date, fixed_date))
    transactions.append(Transaction("UserB", "UserC", 20.0, fixed_date, fixed_date))
    transactions.append(Transaction("UserC", "UserA", 5.0, fixed_date, fixed_date))
    return transactions 