from __future__ import annotations

from datetime import date

# Đây là mô-đun chứa định nghĩa lớp Transaction.

class AdvancedTransaction:
    """
    Represents a debt transaction between two parties.
    Includes information about the debtor, creditor, amount, borrow date, due date,
    interest rate, penalty fee, and transaction status.
    """
    def __init__(self, 
                 debtor: str,         # Debtor's name
                 creditor: str,       # Creditor's name
                 amount: float,       # Principal amount of the transaction
                 borrow_date: date,   # Borrow date
                 due_date: date,      # Due date
                 interest_rate: float = 0.0,  # Daily interest rate (e.g., 0.01 for 1%/day), defaults to 0
                 penalty_fee: float = 0.0,    # One-time penalty fee if overdue, defaults to 0
                 status: str = "pending"): # Transaction status: "pending", "paid", "overdue"
        
        if amount <= 1e-9: # Use a small threshold for positive amount
            raise ValueError("Transaction amount must be greater than 0.")
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative.")
        if penalty_fee < 0:
            raise ValueError("Penalty fee cannot be negative.")
        if due_date < borrow_date:
            raise ValueError("Due date cannot be before borrow date.")
            
        self.debtor = debtor
        self.creditor = creditor
        self.amount = amount
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.interest_rate = interest_rate 
        self.penalty_fee = penalty_fee
        self.status = status 

    def __str__(self) -> str:
        """Returns a friendly string representation of the transaction."""
        return (f"Transaction: {self.debtor} -> {self.creditor}, Amount: {self.amount:.2f}, "
                f"Borrowed: {self.borrow_date}, Due: {self.due_date}, Interest: {self.interest_rate*100:.2f}%/day, "
                f"Penalty: {self.penalty_fee:.2f}, Status: {self.status}")

    def __repr__(self) -> str:
        """Returns an official string representation of the Transaction object."""
        return (f"Transaction(debtor='{self.debtor}', creditor='{self.creditor}', amount={self.amount}, "
                f"borrow_date={repr(self.borrow_date)}, due_date={repr(self.due_date)}, "
                f"interest_rate={self.interest_rate}, penalty_fee={self.penalty_fee}, status='{self.status}')")

    def calculate_total_due(self, current_date: date) -> float:
        """Calculates the total amount due (including principal, interest, and penalty) on a given date (current_date).
        
        Calculation assumptions:
        - Interest (interest_rate) is simple interest, calculated daily on the principal amount.
        - Interest is calculated from borrow_date to the earlier of current_date and due_date.
        - Penalty fee (penalty_fee) is a fixed one-time fee, applied if current_date is after due_date
          and this transaction is not marked as "paid".
        """
        if not isinstance(current_date, date):
            raise TypeError("current_date argument must be a date object.")

        total_due_amount = self.amount
        # Use actual values for interest rate and penalty fee; if None or 0, assume none.
        actual_interest_rate = self.interest_rate if self.interest_rate is not None else 0.0
        actual_penalty_fee = self.penalty_fee if self.penalty_fee is not None else 0.0

        # Calculate interest
        if actual_interest_rate > 1e-9 and current_date > self.borrow_date:
            # Last day for interest calculation is the earlier of current_date and due_date
            interest_calculation_end_date = self.due_date
            if current_date < self.due_date:
                interest_calculation_end_date = current_date
            
            # Number of days for interest (only if interest calculation end date is after borrow date)
            if interest_calculation_end_date > self.borrow_date:
                num_days_for_interest = (interest_calculation_end_date - self.borrow_date).days
                # days_between returns positive if interest_calculation_end_date is after borrow_date
                if num_days_for_interest > 0:
                    interest_amount_calculated = self.amount * actual_interest_rate * num_days_for_interest
                    total_due_amount += interest_amount_calculated
        
        # Calculate penalty fee
        # Penalty fee applies once if overdue and transaction is not yet paid.
        is_overdue_currently = current_date > self.due_date
        if self.status != "paid" and is_overdue_currently and actual_penalty_fee > 1e-9:
            total_due_amount += actual_penalty_fee
        
        return total_due_amount 

class BasicTransaction:
    """
    A basic version of Transaction that only contains the essential fields:
    - debtor: The person who owes money
    - creditor: The person who is owed money
    - amount: The amount of money owed
    """
    def __init__(self, 
                 debtor: str,         # Debtor's name
                 creditor: str,       # Creditor's name
                 amount: float):      # Amount of the transaction
        
        if amount <= 1e-9: # Use a small threshold for positive amount
            raise ValueError("Transaction amount must be greater than 0.")
            
        self.debtor = debtor
        self.creditor = creditor
        self.amount = amount

    def __str__(self) -> str:
        """Returns a friendly string representation of the basic transaction."""
        return f"BasicTransaction: {self.debtor} -> {self.creditor}, Amount: {self.amount:.2f}"

    def __repr__(self) -> str:
        """Returns an official string representation of the BasicTransaction object."""
        return f"BasicTransaction(debtor='{self.debtor}', creditor='{self.creditor}', amount={self.amount})" 