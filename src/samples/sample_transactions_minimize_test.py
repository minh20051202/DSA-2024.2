from datetime import date
from src.core_types import Transaction
from src.data_structures import LinkedList
from src.utils.money_utils import round_money

def create_minimize_test_transactions() -> LinkedList[Transaction]:
    """Create a list of transactions specifically designed to test transaction minimization algorithms."""
    transactions = LinkedList[Transaction]()
    
    # Test case 1: Simple chain of transactions
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
        amount=round_money(100.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 3)
    ))
    transactions.append(Transaction(
        debtor="Charlie",
        creditor="David",
        amount=round_money(100.0),
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
        amount=round_money(50.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 6)
    ))
    
    # Test case 3: Circular transactions
    transactions.append(Transaction(
        debtor="Eve",
        creditor="Frank",
        amount=round_money(200.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 7)
    ))
    transactions.append(Transaction(
        debtor="Frank",
        creditor="Grace",
        amount=round_money(200.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 8)
    ))
    transactions.append(Transaction(
        debtor="Grace",
        creditor="Eve",
        amount=round_money(200.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 9)
    ))
    
    # Test case 4: Complex network
    transactions.append(Transaction(
        debtor="Hank",
        creditor="Ivy",
        amount=round_money(150.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 10)
    ))
    transactions.append(Transaction(
        debtor="Ivy",
        creditor="Jack",
        amount=round_money(150.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 11)
    ))
    transactions.append(Transaction(
        debtor="Jack",
        creditor="Hank",
        amount=round_money(150.0),
        borrow_date=date(2024, 1, 1),
        due_date=date(2024, 1, 12)
    ))
    
    return transactions

__all__ = ['create_minimize_test_transactions'] 