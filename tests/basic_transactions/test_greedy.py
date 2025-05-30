import unittest
from src.core_types import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.greedy import GreedySimplifier

class TestGreedySimplifier(unittest.TestCase):
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

    def test_minimize_transactions(self):
        """
        Test that the greedy algorithm minimizes the number of transactions.
        For the given set of transactions, we expect:
        - Fred -> Ema: 60 (combines Fred's debts to Ema and others)
        - Gabe -> Charlie: 40 (combines Gabe's debts)
        - David -> Charlie: 10 (remaining balance)
        """
        print("\n=== Testing Transaction Minimization ===")
        self.print_transactions(self.transactions, "Original transactions")
        
        simplifier = GreedySimplifier(self.transactions)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Verify minimum number of transactions
        self.assertEqual(result.get_length(), 3)  # Should have exactly 3 transactions
        
        # Verify transaction amounts
        amounts = {}
        current = result.head
        while current:
            tx = current.data
            key = f"{tx.debtor}->{tx.creditor}"
            amounts[key] = tx.amount
            current = current.next

        self.assertEqual(amounts.get("Fred->Ema", 0), 60)
        self.assertEqual(amounts.get("Gabe->Charlie", 0), 40)
        self.assertEqual(amounts.get("David->Charlie", 0), 10)

    def test_net_balance_preservation(self):
        """
        Test that the greedy algorithm preserves net balances for each person.
        The sum of all transactions involving a person should equal their net balance.
        """
        simplifier = GreedySimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Calculate net balances from original transactions
        original_balances = {}
        current = self.transactions.head
        while current:
            tx = current.data
            original_balances[tx.debtor] = original_balances.get(tx.debtor, 0) - tx.amount
            original_balances[tx.creditor] = original_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Calculate net balances from simplified transactions
        simplified_balances = {}
        current = result.head
        while current:
            tx = current.data
            simplified_balances[tx.debtor] = simplified_balances.get(tx.debtor, 0) - tx.amount
            simplified_balances[tx.creditor] = simplified_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Verify that net balances are preserved
        for person in original_balances:
            self.assertAlmostEqual(
                original_balances.get(person, 0),
                simplified_balances.get(person, 0),
                places=10,
                msg=f"Net balance not preserved for {person}"
            )

    def test_cyclic_transactions(self):
        """
        Test that cyclic transactions are properly simplified.
        A perfect cycle should result in no transactions.
        """
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Testing Cyclic Transactions ===")
        self.print_transactions(cyclic_tx, "Original transactions")
        
        simplifier = GreedySimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Should be empty as all debts cancel out
        self.assertTrue(result.is_empty())

    def test_multiple_paths(self):
        """
        Test that the greedy algorithm correctly handles multiple paths
        by combining them into a single transaction when possible.
        """
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
        
        simplifier = GreedySimplifier(paths_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Should have exactly one transaction
        self.assertEqual(result.get_length(), 1)
        
        # Verify the transaction
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 200)  # All paths combined

    def test_disconnected_graph(self):
        """
        Test that the greedy algorithm handles disconnected components correctly.
        Each component should be simplified independently.
        """
        disconnected_tx = LinkedList[BasicTransaction]()
        # First component: A->B->C
        disconnected_tx.append(BasicTransaction("Alice", "Bob", 100))
        disconnected_tx.append(BasicTransaction("Bob", "Charlie", 100))
        # Second component: D->E->F
        disconnected_tx.append(BasicTransaction("David", "Ema", 50))
        disconnected_tx.append(BasicTransaction("Ema", "Fred", 50))
        
        print("\n=== Testing Disconnected Graph ===")
        self.print_transactions(disconnected_tx, "Original transactions")
        
        simplifier = GreedySimplifier(disconnected_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Simplified transactions")
        self.print_balances(result, "Balances after simplification")
        
        # Should have exactly two transactions
        self.assertEqual(result.get_length(), 2)
        
        # Verify the transactions
        amounts = {}
        current = result.head
        while current:
            tx = current.data
            key = f"{tx.debtor}->{tx.creditor}"
            amounts[key] = tx.amount
            current = current.next
        
        self.assertEqual(amounts.get("Alice->Charlie", 0), 100)
        self.assertEqual(amounts.get("David->Fred", 0), 50)

if __name__ == '__main__':
    unittest.main() 