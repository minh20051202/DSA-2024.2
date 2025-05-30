from __future__ import annotations

from datetime import date
from .transaction import AdvancedTransaction # Import AdvancedTransaction

from src.data_structures.linked_list import LinkedList

# Đây là mô-đun chứa định nghĩa lớp Person.

class Person:
    """
    Represents a person (individual or entity) involved in debt transactions.
    Stores name, aggregated balance, and can reference related transactions.
    Attributes like earliest_due_date and highest_interest_rate are used for prioritization algorithms.
    """
    def __init__(self, name: str):
        self.name: str = name
        self.balance: float = 0.0 # Aggregated balance of this person, updated by simplification algorithms.
                                  # Negative balance means debt, positive means credit.
        
        # Use string 'LinkedList[AdvancedTransaction]' for type hint to avoid circular import.
        # Will be initialized with a real LinkedList object when needed.
        self.transactions: 'LinkedList[AdvancedTransaction]' | None = None
        self.earliest_due_date: date | None = None # Earliest due date of this person's DEBTS.
        self.highest_interest_rate: float = 0.0 # Highest interest rate of this person's DEBTS.

    def __str__(self) -> str:
        """Returns a friendly string representation of the Person object."""
        return f"Person: {self.name}, Balance: {self.balance:.2f}"

    def __repr__(self) -> str:
        """Returns an official string representation of the Person object."""
        return f"Person(name='{self.name}')"

    def add_transaction_reference(self, transaction: AdvancedTransaction) -> None:
        """Adds a reference to a transaction related to this person.
        If this person is the DEBTOR in the transaction, update earliest_due_date and highest_interest_rate.
        """
        # Import LinkedList here to avoid module-level circular dependency.
        from src.data_structures.linked_list import LinkedList

        if self.transactions is None: # Initialize LinkedList if it doesn't exist
            self.transactions = LinkedList[AdvancedTransaction]()
        
        # Currently, Person.transactions is not heavily used in the main logic after creation,
        # but kept for potential extensions or debugging.

        # Update information only if this person is the DEBTOR in the transaction.
        if transaction.debtor == self.name:
            if self.earliest_due_date is None or transaction.due_date < self.earliest_due_date:
                self.earliest_due_date = transaction.due_date
            
            if transaction.interest_rate > self.highest_interest_rate:
                self.highest_interest_rate = transaction.interest_rate

    def update_balance(self, amount: float) -> None:
        """Updates the person's balance.
        `amount`: the amount to change the balance by (positive to increase, negative to decrease).
        """
        self.balance += amount 