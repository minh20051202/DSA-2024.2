from datetime import date
from src.core_types import Transaction
from src.data_structures import LinkedList
from src.utils.money_utils import round_money

# Bộ Dữ liệu Mẫu 2: Các kịch bản phức tạp hơn
# Ngày hiện tại cho mô phỏng có thể là, ví dụ, Date(15, 7, 2024)

def create_sample_transactions_2() -> LinkedList[Transaction]:
    """Create a list of sample transactions for testing."""
    transactions = LinkedList[Transaction]()

    # Test case 1: Multiple transactions between same people
    transactions.append(Transaction(
        debtor="Alice",
        creditor="Bob",
        amount=round_money(100.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 5)
    ))
    transactions.append(Transaction(
        debtor="Alice",
        creditor="Bob",
        amount=round_money(200.0),
        borrow_date=date(2024, 1, 2),
        due_date=date(2024, 1, 6)
    ))
    
    # Test case 2: Chain of transactions
    transactions.append(Transaction(
        debtor="Bob",
        creditor="Charlie",
        amount=round_money(150.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 7)
    ))
    transactions.append(Transaction(
        debtor="Charlie",
        creditor="David",
        amount=round_money(150.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 8)
    ))

    # Test case 3: Circular transactions
    transactions.append(Transaction(
        debtor="David",
        creditor="Eve",
        amount=round_money(300.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 9)
    ))
    transactions.append(Transaction(
        debtor="Eve",
        creditor="Frank",
        amount=round_money(300.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 10)
    ))
    transactions.append(Transaction(
        debtor="Frank",
        creditor="David",
        amount=round_money(300.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 11)
    ))

    return transactions

if __name__ == '__main__':
    sample_data = create_sample_transactions_2()
    print(f"Đã tạo {sample_data.get_length()} giao dịch mẫu trong bộ 2.")
    node = sample_data.head
    current_sim_date_for_due_calc = date(2024, 7, 15) # Ví dụ ngày mô phỏng
    total_principal = 0
    total_due_on_sim_date = 0
    while node:
        tx = node.data
        print(tx)
        total_principal += tx.amount
        total_due_on_sim_date += tx.calculate_total_due(current_sim_date_for_due_calc)
        node = node.next
    print(f"---")
    print(f"Tổng số tiền gốc: {total_principal:.2f}")
    print(f"Tổng số tiền phải trả vào ngày {current_sim_date_for_due_calc}: {total_due_on_sim_date:.2f}") 