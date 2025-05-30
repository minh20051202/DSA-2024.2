from datetime import date
from src.core_types import Transaction
from src.data_structures import LinkedList
from src.utils.money_utils import round_money

# Bộ Dữ liệu Mẫu 1
# Ngày hiện tại cho mô phỏng có thể là, ví dụ, Date(15, 6, 2024)

def create_sample_transactions_1() -> LinkedList[Transaction]:
    """Create a list of sample transactions for testing."""
    transactions = LinkedList[Transaction]()
    
    # Test case 1: Simple transactions
    transactions.append(Transaction(
        debtor="Alice",
        creditor="Bob",
        amount=round_money(100.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 2)
    ))
    transactions.append(Transaction(
        debtor="Bob",
        creditor="Charlie",
        amount=round_money(150.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 3)
    ))
    transactions.append(Transaction(
        debtor="Charlie",
        creditor="David",
        amount=round_money(200.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 4)
    ))
    
    # Test case 2: Multiple transactions between same people
    transactions.append(Transaction(
        debtor="David",
        creditor="Eve",
        amount=round_money(50.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 5)
    ))
    transactions.append(Transaction(
        debtor="David",
        creditor="Eve",
        amount=round_money(75.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 6)
    ))
    
    # Test case 3: Circular transactions
    transactions.append(Transaction(
        debtor="Eve",
        creditor="Frank",
        amount=round_money(125.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 7)
    ))
    transactions.append(Transaction(
        debtor="Frank",
        creditor="Grace",
        amount=round_money(125.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 8)
    ))
    transactions.append(Transaction(
        debtor="Grace",
        creditor="Eve",
        amount=round_money(125.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 9)
    ))
    
    return transactions

if __name__ == '__main__':
    sample_data = create_sample_transactions_1()
    print(f"Đã tạo {sample_data.get_length()} giao dịch mẫu.")
    node = sample_data.head
    while node:
        print(node.data)
        node = node.next 