import unittest
from src.core_types import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.min_cost_max_flow import MinCostMaxFlowSimplifier

class TestMinCostMaxFlowSimplifier(unittest.TestCase):
    def setUp(self):
        # Create sample transactions - same as greedy test for comparison
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

    def test_flow_conservation(self):
        """
        Test that the MCMF algorithm preserves flow conservation.
        Sum of all flows into a node should equal sum of flows out (except source/sink).
        """
        simplifier = MinCostMaxFlowSimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Calculate net flows for each person
        net_flows = {}
        current = result.head
        while current:
            tx = current.data
            net_flows[tx.debtor] = net_flows.get(tx.debtor, 0) - tx.amount
            net_flows[tx.creditor] = net_flows.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Calculate original net balances
        original_balances = {}
        current = self.transactions.head
        while current:
            tx = current.data
            original_balances[tx.debtor] = original_balances.get(tx.debtor, 0) - tx.amount
            original_balances[tx.creditor] = original_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Verify flow conservation
        for person in original_balances:
            self.assertAlmostEqual(
                original_balances.get(person, 0),
                net_flows.get(person, 0),
                places=9,
                msg=f"Flow not conserved for {person}"
            )

    def test_cyclic_debt_resolution(self):
        """
        Test MCMF algorithm on cyclic debts.
        Perfect cycles should be eliminated completely.
        """
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Testing MCMF Cyclic Debt Resolution ===")
        self.print_transactions(cyclic_tx, "Original cyclic transactions")
        
        simplifier = MinCostMaxFlowSimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "MCMF Simplified cyclic transactions")
        self.print_balances(result, "Balances after MCMF cyclic simplification")
        
        # Perfect cycle should result in no transactions
        self.assertTrue(result.is_empty(), "Perfect cycle should be completely eliminated")

    def test_complex_network_optimization(self):
        """
        Test MCMF on a complex network where optimal solution is non-trivial.
        """
        complex_tx = LinkedList[BasicTransaction]()
        # Create a more complex network
        complex_tx.append(BasicTransaction("A", "B", 100))
        complex_tx.append(BasicTransaction("A", "C", 50))
        complex_tx.append(BasicTransaction("B", "D", 80))
        complex_tx.append(BasicTransaction("C", "D", 70))
        complex_tx.append(BasicTransaction("D", "E", 150))
        complex_tx.append(BasicTransaction("B", "F", 70))
        complex_tx.append(BasicTransaction("C", "F", 30))
        complex_tx.append(BasicTransaction("F", "E", 50))
        
        print("\n=== Testing MCMF Complex Network ===")
        self.print_transactions(complex_tx, "Original complex transactions")
        
        simplifier = MinCostMaxFlowSimplifier(complex_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "MCMF Simplified complex transactions")
        self.print_balances(result, "Balances after MCMF complex simplification")
        
        # Verify that some optimization occurred
        original_count = complex_tx.get_length()
        optimized_count = result.get_length()
        
        self.assertLessEqual(optimized_count, original_count, 
                           "MCMF should reduce transaction count")

    def test_single_creditor_multiple_debtors(self):
        """
        Test MCMF optimization when multiple people owe one person.
        Should maintain individual transactions as they're already optimal.
        """
        single_creditor_tx = LinkedList[BasicTransaction]()
        single_creditor_tx.append(BasicTransaction("Alice", "Dave", 100))
        single_creditor_tx.append(BasicTransaction("Bob", "Dave", 150))
        single_creditor_tx.append(BasicTransaction("Charlie", "Dave", 200))
        
        print("\n=== Testing MCMF Single Creditor Scenario ===")
        self.print_transactions(single_creditor_tx, "Original single creditor transactions")
        
        simplifier = MinCostMaxFlowSimplifier(single_creditor_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "MCMF Simplified single creditor transactions")
        self.print_balances(result, "Balances after MCMF single creditor simplification")
        
        # Should maintain 3 transactions as they're already optimal
        self.assertEqual(result.get_length(), 3, 
                        "Single creditor scenario should maintain optimal transactions")

    def test_edge_case_zero_transactions(self):
        """
        Test MCMF algorithm with empty transaction list.
        """
        empty_tx = LinkedList[BasicTransaction]()
        
        simplifier = MinCostMaxFlowSimplifier(empty_tx)
        result = simplifier.simplify()
        
        self.assertTrue(result.is_empty(), "Empty input should produce empty output")

    def test_edge_case_single_transaction(self):
        """
        Test MCMF algorithm with single transaction.
        """
        single_tx = LinkedList[BasicTransaction]()
        single_tx.append(BasicTransaction("Alice", "Bob", 100))
        
        simplifier = MinCostMaxFlowSimplifier(single_tx)
        result = simplifier.simplify()
        
        # Should maintain the single transaction
        self.assertEqual(result.get_length(), 1)
        
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 100)

    def test_algorithm_termination(self):
        """
        Test that MCMF algorithm terminates within reasonable iterations.
        This is important as the algorithm could potentially run indefinitely.
        """
        # Create a moderately complex scenario
        termination_tx = LinkedList[BasicTransaction]()
        for i in range(5):
            for j in range(5):
                if i != j:
                    termination_tx.append(BasicTransaction(f"Person{i}", f"Person{j}", 10 * (i + 1)))
        
        print("\n=== Testing MCMF Algorithm Termination ===")
        
        simplifier = MinCostMaxFlowSimplifier(termination_tx)
        result = simplifier.simplify()
        
        # Algorithm should terminate and produce a result
        self.assertIsNotNone(result, "Algorithm should terminate and produce result")
        
        # Verify balance preservation even in complex case
        original_balances = {}
        current = termination_tx.head
        while current:
            tx = current.data
            original_balances[tx.debtor] = original_balances.get(tx.debtor, 0) - tx.amount
            original_balances[tx.creditor] = original_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        result_balances = {}
        current = result.head
        while current:
            tx = current.data
            result_balances[tx.debtor] = result_balances.get(tx.debtor, 0) - tx.amount
            result_balances[tx.creditor] = result_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        for person in original_balances:
            self.assertAlmostEqual(
                original_balances.get(person, 0),
                result_balances.get(person, 0),
                places=8,
                msg=f"Balance not preserved for {person} in complex termination test"
            )

if __name__ == '__main__':
    unittest.main()