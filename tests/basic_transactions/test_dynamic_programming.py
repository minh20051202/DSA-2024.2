import unittest
from src.core_type import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier

class TestDynamicProgrammingSimplifier(unittest.TestCase):
    def setUp(self):
        # Tạo danh sách giao dịch mẫu
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
        """Kiểm thử giao dịch được đơn giản hóa đúng bằng phương pháp lập trình động."""
        print("\n=== Kiểm thử Bộ đơn giản hóa Lập trình Động ===")
        self.print_transactions(self.transactions, "Giao dịch gốc")
        
        simplifier = DynamicProgrammingSimplifier(self.transactions)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch sau khi đơn giản hóa")
        self.print_balances(result, "Số dư sau đơn giản hóa")
        
        # Kiểm tra kết quả không rỗng
        self.assertFalse(result.is_empty())
        
        # Kiểm tra tất cả giao dịch hợp lệ
        current = result.head
        while current:
            tx = current.data
            self.assertIsInstance(tx, BasicTransaction)
            self.assertGreater(tx.amount, 0)
            self.assertNotEqual(tx.debtor, tx.creditor)
            current = current.next

    def test_balance_conservation(self):
        """Kiểm tra bảo toàn số dư ròng sau khi đơn giản hóa."""
        simplifier = DynamicProgrammingSimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Tính số dư ròng mỗi người
        balances = {}
        current = result.head
        while current:
            tx = current.data
            balances[tx.debtor] = balances.get(tx.debtor, 0) - tx.amount
            balances[tx.creditor] = balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Kiểm tra tổng số dư bằng 0
        total_balance = 0
        for balance in balances.values():
            total_balance += balance
        self.assertAlmostEqual(total_balance, 0, places=10)

    def test_single_transaction(self):
        """Kiểm thử một giao dịch duy nhất không thay đổi."""
        single_tx = LinkedList[BasicTransaction]()
        single_tx.append(BasicTransaction("Alice", "Bob", 100))
        
        print("\n=== Kiểm thử Giao dịch Đơn ===")
        self.print_transactions(single_tx, "Giao dịch gốc")
        
        simplifier = DynamicProgrammingSimplifier(single_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch sau đơn giản hóa")
        self.print_balances(result, "Số dư sau đơn giản hóa")
        
        self.assertEqual(len(result), 1)
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 100)

    def test_cyclic_transactions(self):
        """Kiểm thử giao dịch vòng tròn được đơn giản hóa đúng bằng lập trình động."""
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Kiểm thử Giao dịch Vòng tròn ===")
        self.print_transactions(cyclic_tx, "Giao dịch gốc")
        
        simplifier = DynamicProgrammingSimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch sau đơn giản hóa")
        self.print_balances(result, "Số dư sau đơn giản hóa")
        
        # Kết quả nên rỗng vì các khoản nợ triệt tiêu nhau
        self.assertTrue(result.is_empty())

    def test_multiple_paths(self):
        """Kiểm thử nhiều đường đi giữa hai người được đơn giản hóa đúng."""
        paths_tx = LinkedList[BasicTransaction]()
        # Đường trực tiếp: A->B
        paths_tx.append(BasicTransaction("Alice", "Bob", 100))
        # Đường gián tiếp: A->C->B và A->D->B
        paths_tx.append(BasicTransaction("Alice", "Charlie", 50))
        paths_tx.append(BasicTransaction("Charlie", "Bob", 50))
        paths_tx.append(BasicTransaction("Alice", "David", 50))
        paths_tx.append(BasicTransaction("David", "Bob", 50))
        
        print("\n=== Kiểm thử Nhiều Đường đi ===")
        self.print_transactions(paths_tx, "Giao dịch gốc")
        
        simplifier = DynamicProgrammingSimplifier(paths_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch sau đơn giản hóa")
        self.print_balances(result, "Số dư sau đơn giản hóa")
        
        # Phải có ít nhất một giao dịch
        self.assertFalse(result.is_empty())
        
        # Kiểm tra tổng số tiền không đổi
        total_amount = 0
        current = result.head
        while current:
            total_amount += current.data.amount
            current = current.next
            
        # Với lập trình động, thuật toán sẽ tìm giải pháp tối ưu
        # giảm thiểu số giao dịch trong khi giữ tổng số tiền
        # Ở đây tổng số tiền = 100 + 50 + 50 = 200
        expected_total = 200
        self.assertEqual(total_amount, expected_total)
        
        # Kiểm tra giải pháp là tối ưu (số giao dịch tối thiểu)
        # Giải pháp tối ưu là một giao dịch duy nhất từ Alice đến Bob
        self.assertEqual(len(result), 1)
        
        # Kiểm tra giao dịch đúng
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 200)

if __name__ == '__main__':
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)