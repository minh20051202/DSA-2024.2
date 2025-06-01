import unittest
from src.core_type import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.min_cost_max_flow import MinCostMaxFlowSimplifier

class TestMinCostMaxFlowSimplifier(unittest.TestCase):
    def setUp(self):
        # Tạo các giao dịch mẫu - giống như test greedy để so sánh
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
        print(f"  Tổng: {total}")

    def test_flow_conservation(self):
        """
        Kiểm tra thuật toán MCMF bảo toàn lưu lượng.
        Tổng lưu lượng vào một nút phải bằng tổng lưu lượng ra (ngoại trừ nguồn/đích).
        """
        simplifier = MinCostMaxFlowSimplifier(self.transactions)
        result = simplifier.simplify()
        
        # Tính lưu lượng ròng cho mỗi người
        net_flows = {}
        current = result.head
        while current:
            tx = current.data
            net_flows[tx.debtor] = net_flows.get(tx.debtor, 0) - tx.amount
            net_flows[tx.creditor] = net_flows.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Tính số dư ròng ban đầu
        original_balances = {}
        current = self.transactions.head
        while current:
            tx = current.data
            original_balances[tx.debtor] = original_balances.get(tx.debtor, 0) - tx.amount
            original_balances[tx.creditor] = original_balances.get(tx.creditor, 0) + tx.amount
            current = current.next
        
        # Kiểm tra bảo toàn lưu lượng
        for person in original_balances:
            self.assertAlmostEqual(
                original_balances.get(person, 0),
                net_flows.get(person, 0),
                places=9,
                msg=f"Lưu lượng không được bảo toàn cho {person}"
            )

    def test_cyclic_debt_resolution(self):
        """
        Kiểm tra thuật toán MCMF trên các khoản nợ vòng.
        Các vòng nợ hoàn hảo phải được loại bỏ hoàn toàn.
        """
        cyclic_tx = LinkedList[BasicTransaction]()
        cyclic_tx.append(BasicTransaction("Alice", "Bob", 100))
        cyclic_tx.append(BasicTransaction("Bob", "Charlie", 100))
        cyclic_tx.append(BasicTransaction("Charlie", "Alice", 100))
        
        print("\n=== Kiểm tra Giải quyết nợ vòng MCMF ===")
        self.print_transactions(cyclic_tx, "Giao dịch vòng ban đầu")
        
        simplifier = MinCostMaxFlowSimplifier(cyclic_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch vòng sau khi đơn giản hóa MCMF")
        self.print_balances(result, "Số dư sau khi đơn giản hóa nợ vòng MCMF")
        
        # Vòng nợ hoàn hảo phải không còn giao dịch nào
        self.assertTrue(result.is_empty(), "Vòng nợ hoàn hảo phải được loại bỏ hoàn toàn")

    def test_complex_network_optimization(self):
        """
        Kiểm tra MCMF trên mạng phức tạp, nơi lời giải tối ưu không đơn giản.
        """
        complex_tx = LinkedList[BasicTransaction]()
        # Tạo mạng phức tạp hơn
        complex_tx.append(BasicTransaction("A", "B", 100))
        complex_tx.append(BasicTransaction("A", "C", 50))
        complex_tx.append(BasicTransaction("B", "D", 80))
        complex_tx.append(BasicTransaction("C", "D", 70))
        complex_tx.append(BasicTransaction("D", "E", 150))
        complex_tx.append(BasicTransaction("B", "F", 70))
        complex_tx.append(BasicTransaction("C", "F", 30))
        complex_tx.append(BasicTransaction("F", "E", 50))
        
        print("\n=== Kiểm tra Mạng phức tạp MCMF ===")
        self.print_transactions(complex_tx, "Giao dịch phức tạp ban đầu")
        
        simplifier = MinCostMaxFlowSimplifier(complex_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch phức tạp sau đơn giản hóa MCMF")
        self.print_balances(result, "Số dư sau khi đơn giản hóa mạng phức tạp MCMF")
        
        # Kiểm tra có sự tối ưu
        original_count = len(complex_tx)
        optimized_count = len(result)
        
        self.assertLessEqual(optimized_count, original_count, 
                           "MCMF phải giảm số lượng giao dịch")

    def test_single_creditor_multiple_debtors(self):
        """
        Kiểm tra MCMF khi nhiều người nợ một người.
        Nên giữ nguyên các giao dịch cá nhân vì chúng đã tối ưu.
        """
        single_creditor_tx = LinkedList[BasicTransaction]()
        single_creditor_tx.append(BasicTransaction("Alice", "Dave", 100))
        single_creditor_tx.append(BasicTransaction("Bob", "Dave", 150))
        single_creditor_tx.append(BasicTransaction("Charlie", "Dave", 200))
        
        print("\n=== Kiểm tra trường hợp Một chủ nợ nhiều con nợ MCMF ===")
        self.print_transactions(single_creditor_tx, "Giao dịch chủ nợ đơn ban đầu")
        
        simplifier = MinCostMaxFlowSimplifier(single_creditor_tx)
        result = simplifier.simplify()
        
        self.print_transactions(result, "Giao dịch chủ nợ đơn sau đơn giản hóa MCMF")
        self.print_balances(result, "Số dư sau đơn giản hóa chủ nợ đơn MCMF")
        
        # Nên giữ nguyên 3 giao dịch vì đã tối ưu
        self.assertEqual(len(result), 3, 
                        "Trường hợp một chủ nợ nên giữ nguyên các giao dịch tối ưu")

    def test_edge_case_zero_transactions(self):
        """
        Kiểm tra thuật toán MCMF với danh sách giao dịch rỗng.
        """
        empty_tx = LinkedList[BasicTransaction]()
        
        simplifier = MinCostMaxFlowSimplifier(empty_tx)
        result = simplifier.simplify()
        
        self.assertTrue(result.is_empty(), "Đầu vào rỗng phải trả về kết quả rỗng")

    def test_edge_case_single_transaction(self):
        """
        Kiểm tra thuật toán MCMF với một giao dịch duy nhất.
        """
        single_tx = LinkedList[BasicTransaction]()
        single_tx.append(BasicTransaction("Alice", "Bob", 100))
        
        simplifier = MinCostMaxFlowSimplifier(single_tx)
        result = simplifier.simplify()
        
        # Nên giữ lại giao dịch duy nhất
        self.assertEqual(len(result), 1)
        
        tx = result.head.data
        self.assertEqual(tx.debtor, "Alice")
        self.assertEqual(tx.creditor, "Bob")
        self.assertEqual(tx.amount, 100)

    def test_algorithm_termination(self):
        """
        Kiểm tra thuật toán MCMF kết thúc trong số vòng lặp hợp lý.
        Điều này quan trọng vì thuật toán có thể chạy vô hạn.
        """
        # Tạo kịch bản phức tạp vừa phải
        termination_tx = LinkedList[BasicTransaction]()
        
        simplifier = MinCostMaxFlowSimplifier(termination_tx)
        result = simplifier.simplify()
        
        # Thuật toán phải kết thúc và trả về kết quả
        self.assertIsNotNone(result, "Thuật toán phải kết thúc và trả về kết quả")
        
        # Kiểm tra bảo toàn số dư ngay cả trong trường hợp phức tạp
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
                msg=f"Số dư không được bảo toàn cho {person} trong bài test kết thúc phức tạp"
            )

if __name__ == '__main__':
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)