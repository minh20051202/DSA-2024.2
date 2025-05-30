from typing import TYPE_CHECKING
from datetime import date
from src.core_types import AdvancedTransaction
from src.data_structures import Array
from src.utils.money_utils import round_money

class TimeInterestCalculator:
    """
    A utility class for calculating time and interest for simplified transactions.
    Implements methods from documentation: Weighted Average and Interest Rate Adjustment.
    """

    @staticmethod
    def calculate_weighted_due_date(transactions: Array[AdvancedTransaction]) -> date:
        """
        Method 1: Calculate due date using weighted average by amount.
        Formula: New Due Date = Σ(Amount × Original Due Date) / Total Amount
        """
        if len(transactions) == 0:
            return date(2000, 1, 1)  # Epoch date

        total_weighted_days = 0.0
        total_amount = 0.0

        for tx in transactions:
            if tx.amount > 1e-9:  # Only consider significant transactions
                due_date_days = TimeInterestCalculator._date_to_days(tx.due_date)
                total_weighted_days += tx.amount * due_date_days
                total_amount += tx.amount

        if total_amount < 1e-9:  # Avoid division by zero
            return date(2000, 1, 1)  # Epoch date

        weighted_average_days = total_weighted_days / total_amount
        return TimeInterestCalculator._days_to_date(round(weighted_average_days))  # Use round instead of int

    @staticmethod
    def calculate_adjusted_interest_rate(original_transactions: Array[AdvancedTransaction],
                                       new_borrow_date: date,
                                       new_due_date: date) -> float:
        """
        Method 2: Adjust interest rate based on time ratio.
        Formula: New Rate = Old Rate × (New Time / Old Time)
        """
        if len(original_transactions) == 0:
            return 0.0

        total_weighted_interest = 0.0
        total_amount = 0.0
        total_weighted_original_days = 0.0

        for tx in original_transactions:
            if tx.amount > 1e-9:
                original_days = TimeInterestCalculator._calculate_days_between(tx.borrow_date, tx.due_date)
                if original_days > 0:
                    total_weighted_interest += tx.amount * tx.interest_rate
                    total_weighted_original_days += tx.amount * original_days
                    total_amount += tx.amount

        if total_amount < 1e-9:
            return 0.0

        average_original_interest = total_weighted_interest / total_amount
        average_original_days = total_weighted_original_days / total_amount
        new_days = TimeInterestCalculator._calculate_days_between(new_borrow_date, new_due_date)

        if average_original_days < 1e-9 or new_days < 1e-9:
            return 0.0

        # Limit the adjusted interest rate to 100% (1.0)
        adjusted_interest_rate = min(
            average_original_interest * (new_days / average_original_days),
            1.0
        )
        return round_money(adjusted_interest_rate)  # Round to 2 decimal places

    @staticmethod
    def calculate_total_amount_with_interest(principal: float,
                                           interest_rate: float,
                                           borrow_date: date,
                                           due_date: date) -> float:
        """
        Calculate total amount including interest.
        Formula: Total = Principal + (Principal × Daily Interest Rate × Days)
        """
        if principal < 1e-9:
            return 0.0

        days = TimeInterestCalculator._calculate_days_between(borrow_date, due_date)
        if days <= 0:
            return round_money(principal)  # No interest if no time period

        daily_interest_rate = interest_rate / 365.0
        interest_amount = principal * daily_interest_rate * days

        return round_money(principal + interest_amount)  # Round final result

    @staticmethod
    def _date_to_days(d: date) -> int:
        """Convert date to days from epoch (1/1/2000)."""
        epoch = date(2000, 1, 1)
        return (d - epoch).days

    @staticmethod
    def _days_to_date(days: int) -> date:
        """Convert days from epoch to date."""
        epoch = date(2000, 1, 1)
        return epoch + date.resolution * days

    @staticmethod
    def _calculate_days_between(start_date: date, end_date: date) -> int:
        """Calculate number of days between two dates."""
        return (end_date - start_date).days 