import unittest
from src.core_type import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.cycle_detector import DebtCycleSimplifier

class TestDebtCycleSimplifier(unittest.TestCase):
    def setUp(self):
        # Tạo các giao dịch mẫu
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
        print(f"  Tổng cộng: {total}")

    def test_simplify_transactions(self):
        """Kiểm tra việc đơn giản hóa giao dịch được thực hiện đúng và giữ cân bằng."""
        print("\n=== Kiểm tra Bộ giải quyết Chu kỳ Nợ ===")
        self.print_transactions(self.transactions, "Giao dịch gốc")
        
        simplifier = DebtCycleSimplifier(self.transactions)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Xác nhận kết quả không rỗng
        self.assertFalse(result.is_empty())
        
        # Xác nhận tất cả giao dịch hợp lệ
        current = result.head
        while current:
            tx = current.data
            self.assertIsInstance(tx, BasicTransaction)
            self.assertGreater(tx.amount, 0)
            self.assertNotEqual(tx.debtor, tx.creditor)
            current = current.next

    def test_balance_conservation(self):
        """Kiểm tra cân bằng số dư được bảo toàn sau khi đơn giản hóa."""
        simplifier = DebtCycleSimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Tính số dư ròng cho mỗi người
        balances = {}
        current = result.head
        while current:
            tx = current.data
            balances[tx.debtor] = balances.get(tx.debtor, 0) - tx.amount
            balances[tx.creditor] = balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Xác nhận tổng số dư gần bằng 0 (do sai số float)
        total_balance = 0
        for balance in balances.values():
            total_balance += balance
        self.assertAlmostEqual(total_balance, 0, places=10)

    def test_single_transaction(self):
        """Kiểm tra một giao dịch duy nhất không bị thay đổi."""
        single_tx = LinkedList[BasicTransaction]()
        single_tx.append(BasicTransaction("Alice", "Bob", 100))
        
        print("\n=== Kiểm tra Giao dịch Đơn ===")
        self.print_transactions(single_tx, "Giao dịch gốc")
        
        simplifier = DebtCycleSimplifier(single_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        self.assertEqual(len(result), 1)
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 100)

    def test_cyclic_transactions(self):
        """Kiểm tra các giao dịch có chu kỳ được đơn giản hóa đúng."""
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Kiểm tra Giao dịch Có Chu kỳ ===")
        self.print_transactions(cyclic_tx, "Giao dịch gốc")
        
        simplifier = DebtCycleSimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Kết quả nên rỗng vì nợ được triệt tiêu hết
        self.assertTrue(result.is_empty())

    def test_multiple_paths(self):
        """Kiểm tra nhiều đường đi giữa hai người được đơn giản hóa đúng."""
        paths_tx = LinkedList[BasicTransaction]()
        # Đường thẳng: A->B
        paths_tx.append(BasicTransaction("Alice", "Bob", 100))
        # Đường vòng: A->C->B và A->D->B
        paths_tx.append(BasicTransaction("Alice", "Charlie", 50))
        paths_tx.append(BasicTransaction("Charlie", "Bob", 50))
        paths_tx.append(BasicTransaction("Alice", "David", 50))
        paths_tx.append(BasicTransaction("David", "Bob", 50))
        
        print("\n=== Kiểm tra Nhiều Đường Đi ===")
        self.print_transactions(paths_tx, "Giao dịch gốc")
        
        simplifier = DebtCycleSimplifier(paths_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Kết quả không rỗng
        self.assertFalse(result.is_empty())
        
        # Xác nhận tổng số tiền được bảo toàn
        total_amount = 0
        current = result.head
        while current:
            total_amount += current.data.amount
            current = current.next
            
        # Tổng tiền phải bằng tổng các đường đi duy nhất
        # Ở đây: 100 (trực tiếp) + 50 (A->C->B) + 50 (A->D->B) = 200
        expected_total = 200
        self.assertEqual(total_amount, expected_total)

if __name__ == '__main__':
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)