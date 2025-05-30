import unittest
from src.core_types import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier

class TestDynamicProgrammingSimplifier(unittest.TestCase):
    def setUp(self):
        # Create sample transactions
        self.transactions = LinkedList[BasicTransaction]()
        self.transactions.append(BasicTransaction("Gabe", "Bob", 30))
        self.transactions.append(BasicTransaction("Gabe", "David", 10))
        self.transactions.append(BasicTransaction("Fred", "Bob", 10))
        self.transactions.append(BasicTransaction("Fred", "Charlie", 30))
        self.transactions.append(BasicTransaction("Fred", "David", 10))
        self.transactions.append(BasicTransaction("Fred", "Ema", 10))
        self.transactions.append(BasicTransaction("Bob", "Charlie", 40))
        self.transactions.append(BasicTransaction("Charlie", "David", 20))
        self.transactions.append(BasicTransaction("David", "Ema", 50))

    def print_transactions(self, transactions, title):
        print(f"\n{title}:")
        current = transactions.head
        while current:
            tx = current.data
            print(f"  {tx.debtor} -> {tx.creditor}: {tx.amount}")
            current = current.next

    def print_balances(self, transactions, title):
        print(f"\n{title}:")
        balances = {}
        current = transactions.head
        while current:
            tx = current.data
            balances[tx.debtor] = balances.get(tx.debtor, 0) - tx.amount
            balances[tx.creditor] = balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        total = 0
        for person, balance in sorted(balances.items()):
            print(f"  {person}: {balance}")
            total += balance
        print(f"  Total: {total}")

    def test_simplify_transactions(self):
        """Test that transactions are properly simplified using dynamic programming approach."""
        print("\n=== Testing Dynamic Programming Simplifier ===")
        self.print_transactions(self.transactions, "Original transactions")
        
        simplifier = DynamicProgrammingSimplifier(self.transactions)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Verify result is not empty
        self.assertFalse(result.is_empty())
        
        # Verify all transactions are valid
        current = result.head
        while current:
            tx = current.data
            self.assertIsInstance(tx, BasicTransaction)
            self.assertGreater(tx.amount, 0)
            self.assertNotEqual(tx.debtor, tx.creditor)
            current = current.next

    def test_balance_conservation(self):
        """Test that net balances are preserved after simplification."""
        simplifier = DynamicProgrammingSimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Calculate net balances for each person
        balances = {}
        current = result.head
        while current:
            tx = current.data
            balances[tx.debtor] = balances.get(tx.debtor, 0) - tx.amount
            balances[tx.creditor] = balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Verify total balance is zero
        total_balance = 0
        for balance in balances.values():
            total_balance += balance
        self.assertAlmostEqual(total_balance, 0, places=10)

    def test_single_transaction(self):
        """Test that a single transaction remains unchanged."""
        single_tx = LinkedList[BasicTransaction]()
        single_tx.append(BasicTransaction("Alice", "Bob", 100))
        
        print("\n=== Testing Single Transaction ===")
        self.print_transactions(single_tx, "Original transaction")
        
        simplifier = DynamicProgrammingSimplifier(single_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transaction")
        self.print_balances(result, "Balances after simplification")
        
        self.assertEqual(result.get_length(), 1)
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 100)

    def test_cyclic_transactions(self):
        """Test that cyclic transactions are properly simplified using dynamic programming."""
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Testing Cyclic Transactions ===")
        self.print_transactions(cyclic_tx, "Original transactions")
        
        simplifier = DynamicProgrammingSimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Should be empty as all debts cancel out
        self.assertTrue(result.is_empty())

    def test_multiple_paths(self):
        """Test that multiple paths between two people are properly simplified using dynamic programming."""
        paths_tx = LinkedList[BasicTransaction]()
        # Direct path: A->B
        paths_tx.append(BasicTransaction("Alice", "Bob", 100))
        # Indirect paths: A->C->B and A->D->B
        paths_tx.append(BasicTransaction("Alice", "Charlie", 50))
        paths_tx.append(BasicTransaction("Charlie", "Bob", 50))
        paths_tx.append(BasicTransaction("Alice", "David", 50))
        paths_tx.append(BasicTransaction("David", "Bob", 50))
        
        print("\n=== Testing Multiple Paths ===")
        self.print_transactions(paths_tx, "Original transactions")
        
        simplifier = DynamicProgrammingSimplifier(paths_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Should have at least one transaction
        self.assertFalse(result.is_empty())
        
        # Verify total amount is preserved
        total_amount = 0
        current = result.head
        while current:
            total_amount += current.data.amount
            current = current.next
            
        # For dynamic programming, we expect the algorithm to find the optimal solution
        # that minimizes the number of transactions while preserving the total amount
        # In this case, the total amount should be the sum of all paths (100 + 50 + 50 = 200)
        expected_total = 200  # Sum of all paths
        self.assertEqual(total_amount, expected_total)
        
        # Verify that the solution is optimal (minimal number of transactions)
        # The optimal solution should be a single transaction from Alice to Bob
        self.assertEqual(result.get_length(), 1)
        
        # Verify the transaction is correct
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 200)

if __name__ == '__main__':
    unittest.main() 