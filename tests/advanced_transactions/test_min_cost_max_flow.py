import unittest
from datetime import date
from src.core_types import AdvancedTransaction
from src.data_structures import LinkedList, Graph
from src.algorithms.advanced_transactions.min_cost_max_flow import AdvancedMinCostMaxFlowSimplifier
from src.utils.time_interest_calculator import TimeInterestCalculator
from src.utils.money_utils import round_money

class TestMinCostMaxFlowSimplifier(unittest.TestCase):
    def setUp(self):
        """Set up test cases with transactions including interest and dates."""
        self.transactions = LinkedList[AdvancedTransaction]()
        self.current_date = date(2024, 1, 1)  # Set current date for all tests
        self.interest_calculator = TimeInterestCalculator()
        
        # Test case 1: Simple transactions with interest
        self.transactions.append(AdvancedTransaction(
            debtor="Alice",
            creditor="Bob",
            amount=round_money(100.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 2),
            interest_rate=0.01  # 1% per day
        ))
        
        self.transactions.append(AdvancedTransaction(
            debtor="Bob",
            creditor="Charlie",
            amount=round_money(150.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 3),
            interest_rate=0.02  # 2% per day
        ))
        
        self.transactions.append(AdvancedTransaction(
            debtor="Charlie",
            creditor="Alice",
            amount=round_money(200.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 4),
            interest_rate=0.015  # 1.5% per day
        ))

    def calculate_total_with_interest(self, transactions):
        """Calculate total amount including interest for all transactions."""
        total = 0
        for tx in transactions:
            total_amount = TimeInterestCalculator.calculate_total_amount_with_interest(
                tx.amount,
                tx.interest_rate,
                tx.borrow_date,
                tx.due_date
            )
            total += round_money(total_amount)
        return round_money(total)  # Ensure final total is rounded to 2 decimal places

    def test_flow_optimization_with_interest(self):
        """Test flow optimization with interest rates."""
        simplifier = AdvancedMinCostMaxFlowSimplifier(self.transactions, self.current_date)
        simplified = simplifier.simplify()
        
        # Verify the number of transactions is reduced
        self.assertLess(len(simplified), len(self.transactions))
        
        # Verify total amounts with interest are preserved
        original_total = self.calculate_total_with_interest(self.transactions)
        simplified_total = self.calculate_total_with_interest(simplified)
        self.assertEqual(original_total, simplified_total)  # Exact comparison for 2 decimal places
        
        # Verify interest rates are properly adjusted
        for tx in simplified:
            self.assertGreaterEqual(tx.interest_rate, 0)
            self.assertLessEqual(tx.interest_rate, 0.02)  # Max interest rate from original

    def test_network_flow_with_dates(self):
        """Test network flow with different dates and interest rates."""
        # Add more complex transactions
        self.transactions.append(AdvancedTransaction(
            debtor="David",
            creditor="Eve",
            amount=round_money(300.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 5),
            interest_rate=0.025  # 2.5% per day
        ))
        
        self.transactions.append(AdvancedTransaction(
            debtor="Eve",
            creditor="Alice",
            amount=round_money(250.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 6),
            interest_rate=0.018  # 1.8% per day
        ))
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(self.transactions, self.current_date)
        simplified = simplifier.simplify()
        
        # Verify simplification
        self.assertLess(len(simplified), len(self.transactions))
        
        # Verify total amounts with interest are preserved
        original_total = self.calculate_total_with_interest(self.transactions)
        simplified_total = self.calculate_total_with_interest(simplified)
        self.assertEqual(original_total, simplified_total)  # Exact comparison for 2 decimal places
        
        # Verify dates are properly weighted
        for tx in simplified:
            self.assertGreaterEqual(tx.borrow_date, date(2024, 1, 1))
            self.assertLessEqual(tx.due_date, date(2024, 1, 6))

    def test_penalty_fees_in_flow(self):
        """Test handling penalty fees in flow optimization."""
        # Add transactions with penalty fees
        self.transactions.append(AdvancedTransaction(
            debtor="Frank",
            creditor="Grace",
            amount=round_money(400.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 7),
            interest_rate=0.02,
            penalty_fee=round_money(50.0)
        ))
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(self.transactions, self.current_date)
        simplified = simplifier.simplify()
        
        # Verify total amounts with interest and penalties are preserved
        original_total = self.calculate_total_with_interest(self.transactions)
        simplified_total = self.calculate_total_with_interest(simplified)
        self.assertEqual(original_total, simplified_total)  # Exact comparison for 2 decimal places
        
        # Verify penalty fees are considered in flow
        for tx in simplified:
            if tx.penalty_fee > 0:
                self.assertGreaterEqual(tx.amount, tx.penalty_fee)

    def test_empty_transactions(self):
        """Test handling empty transaction list."""
        empty_transactions = LinkedList[AdvancedTransaction]()
        simplifier = AdvancedMinCostMaxFlowSimplifier(empty_transactions, self.current_date)
        simplified = simplifier.simplify()
        
        self.assertEqual(len(simplified), 0)

    def test_single_transaction(self):
        """Test handling single transaction."""
        single_transaction = LinkedList[AdvancedTransaction]()
        single_transaction.append(AdvancedTransaction(
            debtor="Alice",
            creditor="Bob",
            amount=round_money(100.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 2),
            interest_rate=0.01
        ))
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(single_transaction, self.current_date)
        simplified = simplifier.simplify()
        
        self.assertEqual(len(simplified), 1)
        # Calculate total with interest for comparison
        original_total = self.calculate_total_with_interest(single_transaction)
        simplified_total = self.calculate_total_with_interest(simplified)
        self.assertEqual(original_total, simplified_total)  # Exact comparison for 2 decimal places

    def test_large_network_flow(self):
        """Test flow optimization with large network."""
        large_transactions = LinkedList[AdvancedTransaction]()
        
        # Create 100 transactions
        for i in range(100):
            large_transactions.append(AdvancedTransaction(
                debtor=f"Person{i}",
                creditor=f"Person{(i+1)%100}",
                amount=round_money(100.0 + i),
                borrow_date=date(2024, 1, 1),
                due_date=date(2024, 1, 2),
                interest_rate=0.01
            ))
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(large_transactions, self.current_date)
        simplified = simplifier.simplify()
        
        # Verify simplification
        self.assertLess(len(simplified), len(large_transactions))
        
        # Verify total amounts with interest are preserved
        original_total = self.calculate_total_with_interest(large_transactions)
        simplified_total = self.calculate_total_with_interest(simplified)
        self.assertEqual(original_total, simplified_total)  # Exact comparison for 2 decimal places

    def test_flow_capacity_constraints(self):
        """Test flow optimization with capacity constraints."""
        # Add transactions with varying amounts
        self.transactions.append(AdvancedTransaction(
            debtor="Hank",
            creditor="Ivy",
            amount=round_money(500.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 8),
            interest_rate=0.02
        ))
        
        self.transactions.append(AdvancedTransaction(
            debtor="Ivy",
            creditor="Jack",
            amount=round_money(300.0),
            borrow_date=date(2024, 1, 1),
            due_date=date(2024, 1, 9),
            interest_rate=0.015
        ))
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(self.transactions, self.current_date)
        simplified = simplifier.simplify()
        
        # Verify total amounts with interest are preserved
        original_total = self.calculate_total_with_interest(self.transactions)
        simplified_total = self.calculate_total_with_interest(simplified)
        self.assertEqual(original_total, simplified_total)  # Exact comparison for 2 decimal places
        
        # Verify flow capacity constraints
        for tx in simplified:
            self.assertGreaterEqual(tx.amount, 0)
            self.assertLessEqual(tx.amount, round_money(500.0))  # Max amount from original

if __name__ == '__main__':
    unittest.main() 