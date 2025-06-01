import unittest
from src.core_type import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.greedy import GreedySimplifier

class TestGreedySimplifier(unittest.TestCase):
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

    def test_minimize_transactions(self):
        """
        Kiểm tra thuật toán greedy giảm thiểu số giao dịch.
        Với bộ giao dịch đã cho, chúng ta mong đợi:
        - Fred -> Ema: 60 (gộp các khoản nợ của Fred cho Ema và người khác)
        - Gabe -> Charlie: 40 (gộp các khoản nợ của Gabe)
        - David -> Charlie: 10 (số dư còn lại)
        """
        print("\n=== Kiểm tra Giảm thiểu Giao dịch ===")
        self.print_transactions(self.transactions, "Giao dịch gốc")
        
        simplifier = GreedySimplifier(self.transactions)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Xác nhận số giao dịch tối thiểu
        self.assertEqual(len(result), 3)  # Phải có đúng 3 giao dịch
        
        # Xác nhận các khoản tiền giao dịch
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
        Kiểm tra thuật toán greedy giữ nguyên số dư ròng cho mỗi người.
        Tổng các giao dịch liên quan đến một người phải bằng số dư ròng của họ.
        """
        simplifier = GreedySimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Tính số dư ròng từ các giao dịch gốc
        original_balances = {}
        current = self.transactions.head
        while current:
            tx = current.data
            original_balances[tx.debtor] = original_balances.get(tx.debtor, 0) - tx.amount
            original_balances[tx.creditor] = original_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Tính số dư ròng từ các giao dịch đã đơn giản hóa
        simplified_balances = {}
        current = result.head
        while current:
            tx = current.data
            simplified_balances[tx.debtor] = simplified_balances.get(tx.debtor, 0) - tx.amount
            simplified_balances[tx.creditor] = simplified_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Xác nhận số dư ròng được bảo toàn
        for person in original_balances:
            self.assertAlmostEqual(
                original_balances.get(person, 0),
                simplified_balances.get(person, 0),
                places=10,
                msg=f"Số dư ròng không được bảo toàn cho {person}"
            )

    def test_cyclic_transactions(self):
        """
        Kiểm tra các giao dịch có chu kỳ được đơn giản hóa đúng.
        Một chu kỳ hoàn hảo nên không còn giao dịch nào.
        """
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Kiểm tra Giao dịch Có Chu kỳ ===")
        self.print_transactions(cyclic_tx, "Giao dịch gốc")
        
        simplifier = GreedySimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Kết quả nên rỗng vì các khoản nợ triệt tiêu nhau
        self.assertTrue(result.is_empty())

    def test_multiple_paths(self):
        """
        Kiểm tra thuật toán greedy xử lý đúng nhiều đường đi
        bằng cách gộp chúng thành một giao dịch duy nhất khi có thể.
        """
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
        
        simplifier = GreedySimplifier(paths_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Phải có đúng một giao dịch
        self.assertEqual(len(result), 1)
        
        # Xác nhận giao dịch
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 200)  # Gộp tất cả các đường đi

    def test_disconnected_graph(self):
        """
        Kiểm tra thuật toán greedy xử lý đúng các thành phần rời rạc.
        Mỗi thành phần được đơn giản hóa độc lập.
        """
        disconnected_tx = LinkedList[BasicTransaction]()
        # Thành phần 1: A->B->C
        disconnected_tx.append(BasicTransaction("Alice", "Bob", 100))
        disconnected_tx.append(BasicTransaction("Bob", "Charlie", 100))
        # Thành phần 2: D->E->F
        disconnected_tx.append(BasicTransaction("David", "Ema", 50))
        disconnected_tx.append(BasicTransaction("Ema", "Fred", 50))
        
        print("\n=== Kiểm tra Đồ thị Rời rạc ===")
        self.print_transactions(disconnected_tx, "Giao dịch gốc")
        
        simplifier = GreedySimplifier(disconnected_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch đã đơn giản hóa")
        self.print_balances(result, "Cân bằng sau khi đơn giản hóa")
        
        # Phải có đúng hai giao dịch
        self.assertEqual(len(result), 2)
        
        # Xác nhận các giao dịch
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
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)
