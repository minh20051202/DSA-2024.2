from __future__ import annotations
import unittest

from src.data_structures import LinkedList
from src.core_type import BasicTransaction
from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

class TestDynamicProgrammingSimplifier(unittest.TestCase):
    """Bộ kiểm thử cho DynamicProgrammingSimplifier."""

    def assertTransactionsMatch(self, actual_tx_list: LinkedList[BasicTransaction], 
                                expected_txs: list[tuple[str, str, float]]):
        """
        Hàm trợ giúp để so sánh danh sách giao dịch thực tế với danh sách kỳ vọng.
        Kiểm tra số lượng giao dịch và nội dung của chúng.
        Sử dụng một map để không phụ thuộc vào thứ tự của các giao dịch được trả về.
        """
        self.assertEqual(len(actual_tx_list), len(expected_txs), 
                         f"Số lượng giao dịch không khớp. Kỳ vọng: {len(expected_txs)}, Thực tế: {len(actual_tx_list)}")

        # Chuyển đổi expected_txs thành một dạng dễ so sánh hơn (map)
        expected_map = {}
        for d, c, amt in expected_txs:
            # Làm tròn số tiền kỳ vọng để so sánh nhất quán
            expected_map[tuple(sorted((d, c)))] = round_money(amt)

        actual_map = {}
        current = actual_tx_list.head
        while current:
            tx = current.data
            # Làm tròn số tiền thực tế
            actual_map[tuple(sorted((tx.debtor, tx.creditor)))] = round_money(tx.amount)
            current = current.next
        
        for key_pair, expected_amt in expected_map.items():
            actual_amt = actual_map.get(key_pair)
            self.assertIsNotNone(actual_amt, f"Thiếu giao dịch kỳ vọng giữa {key_pair[0]} và {key_pair[1]}")
            self.assertAlmostEqual(actual_amt, expected_amt, delta=EPSILON,
                                   msg=f"Số tiền giao dịch giữa {key_pair[0]} và {key_pair[1]} không khớp. Kỳ vọng: {expected_amt}, Thực tế: {actual_amt}")

    def test_empty_transactions_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Danh sách giao dịch rỗng")
        print("=" * 60)
        transactions = LinkedList[BasicTransaction]()
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()
        self.assertTrue(simplified.is_empty())
        print("✅ DP Kiểm thử danh sách giao dịch rỗng thành công")

    def test_single_transaction_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Giao dịch đơn lẻ")
        print("=" * 60)
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("Alice", "Bob", 100.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()
        
        expected = [("Alice", "Bob", 100.0)]
        self.assertTransactionsMatch(simplified, expected)
        print(f"💸 Kết quả: {simplified.head.data.debtor} → {simplified.head.data.creditor} = ${simplified.head.data.amount:.2f}")
        print("✅ DP Kiểm thử giao dịch đơn lẻ thành công")

    def test_direct_cancellation_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Bù trừ trực tiếp (A->B, B->A)")
        print("=" * 60)
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("Alice", "Bob", 100.0))
        transactions.append(BasicTransaction("Bob", "Alice", 70.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("Alice", "Bob", 30.0)]
        self.assertTransactionsMatch(simplified, expected)
        print(f"💸 Kết quả: {simplified.head.data.debtor} → {simplified.head.data.creditor} = ${simplified.head.data.amount:.2f}")
        print("✅ DP Kiểm thử bù trừ trực tiếp thành công")

    def test_three_party_cycle_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Chu trình 3 bên (A->B, B->C, C->A) - Triệt tiêu hoàn toàn")
        print("=" * 60)
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "B", 50.0))
        transactions.append(BasicTransaction("B", "C", 50.0))
        transactions.append(BasicTransaction("C", "A", 50.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        self.assertTrue(simplified.is_empty(), "Chu trình 3 bên bằng nhau nên triệt tiêu hết")
        print("💸 Kết quả: Không có giao dịch (đã triệt tiêu)")
        print("✅ DP Kiểm thử chu trình 3 bên triệt tiêu hoàn toàn thành công")

    def test_three_party_cycle_with_remaining_debt_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Chu trình 3 bên với nợ còn lại")
        print("=" * 60)
        # A -100-> B -70-> C -50-> A
        # Min in cycle = 50 (C->A)
        # Sau khi trừ 50: A->B: 50, B->C: 20, C->A: 0
        # Kết quả còn lại: A->B: 50, B->C: 20
        # Hoặc DP có thể tối ưu hơn: A->C: 20, A->B: 30 (vì A nợ tổng 50, B nhận 50-20=30, C nhận 20)
        # Net balances: A: -100+50 = -50; B: +100-70 = +30; C: +70-50 = +20
        # Expected: A->B: 30, A->C: 20
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "B", 100.0))
        transactions.append(BasicTransaction("B", "C", 70.0))
        transactions.append(BasicTransaction("C", "A", 50.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("A", "B", 30.0), ("A", "C", 20.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử chu trình 3 bên với nợ còn lại thành công")

    def test_four_party_chain_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Chuỗi 4 bên (A->B, B->C, C->D)")
        print("=" * 60)
        # A -100-> B -70-> C -50-> D
        # Net balances: A: -100, B: +100-70=+30, C: +70-50=+20, D: +50
        # DP có thể tìm ra: A->D: 50, A->C: 20, A->B: 30 (3 transactions)
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "B", 100.0))
        transactions.append(BasicTransaction("B", "C", 70.0))
        transactions.append(BasicTransaction("C", "D", 50.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("A", "D", 50.0), ("A", "C", 20.0), ("A", "B", 30.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử chuỗi 4 bên thành công")

    def test_four_party_cycle_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Chu trình 4 bên (P->Q, Q->R, R->S, S->P)")
        print("=" * 60)
        # P -40-> Q -35-> R -25-> S -20-> P
        # Min in cycle = 20 (S->P)
        # Net balances:
        # P: -40+20 = -20
        # Q: +40-35 = +5
        # R: +35-25 = +10
        # S: +25-20 = +5
        # Sum of positive = 5+10+5 = 20. Matches sum of negative.
        # Expected: P->R: 10, P->Q: 5, P->S: 5
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("P", "Q", 40.0))
        transactions.append(BasicTransaction("Q", "R", 35.0))
        transactions.append(BasicTransaction("R", "S", 25.0))
        transactions.append(BasicTransaction("S", "P", 20.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("P", "R", 10.0), ("P", "Q", 5.0), ("P", "S", 5.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử chu trình 4 bên thành công")

    def test_complex_case_multiple_paths_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Trường hợp phức tạp nhiều đường nợ")
        print("=" * 60)
        # A->B: 10, A->C: 10
        # B->D: 5, C->D: 5
        # Net Balances: A: -20, B: +10-5=+5, C: +10-5=+5, D: +5+5=+10
        # Expected: A->D: 10, A->B: 5, A->C: 5
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "B", 10.0))
        transactions.append(BasicTransaction("A", "C", 10.0))
        transactions.append(BasicTransaction("B", "D", 5.0))
        transactions.append(BasicTransaction("C", "D", 5.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("A", "D", 10.0), ("A", "B", 5.0), ("A", "C", 5.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử trường hợp phức tạp thành công")

    def test_one_debtor_multiple_creditors_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Một người nợ nhiều người")
        print("=" * 60)
        # A -> B: 30
        # A -> C: 40
        # A -> D: 50
        # Net Balances: A: -120, B: +30, C: +40, D: +50
        # Expected: A->B:30, A->C:40, A->D:50 (DP should keep these as optimal if no cycles)
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "B", 30.0))
        transactions.append(BasicTransaction("A", "C", 40.0))
        transactions.append(BasicTransaction("A", "D", 50.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("A", "B", 30.0), ("A", "C", 40.0), ("A", "D", 50.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử một người nợ nhiều người thành công")

    def test_multiple_debtors_one_creditor_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: Nhiều người nợ một người")
        print("=" * 60)
        # A -> D: 30
        # B -> D: 40
        # C -> D: 50
        # Net Balances: A: -30, B: -40, C: -50, D: +120
        # Expected: A->D:30, B->D:40, C->D:50
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "D", 30.0))
        transactions.append(BasicTransaction("B", "D", 40.0))
        transactions.append(BasicTransaction("C", "D", 50.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("A", "D", 30.0), ("B", "D", 40.0), ("C", "D", 50.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử nhiều người nợ một người thành công")

    def test_five_party_complex_cycle_and_chain_dp(self):
        print("\n" + "=" * 60)
        print("DP KIỂM THỬ: 5 bên, chu trình và chuỗi phức tạp")
        print("=" * 60)
        # A->B: 100
        # B->C: 80
        # C->A: 60 (Cycle A-B-C, min 60. A->B: 40, B->C: 20)
        # C->D: 70 (Sau cycle, C còn nợ D: 70)
        # D->E: 50
        #
        # Sau cycle A-B-C:
        # A->B: 40
        # B->C: 20
        # C->D: 70
        # D->E: 50
        #
        # Net Balances:
        # A: -40
        # B: +40-20 = +20
        # C: +20-70 = -50
        # D: +70-50 = +20
        # E: +50
        # Sum Neg: -40-50 = -90. Sum Pos: +20+20+50 = +90. OK.
        #
        # Expected (một khả năng tối ưu từ DP):
        # A->B: 20 (B cần 20)
        # A->D: 20 (D cần 20, A còn nợ 20)
        # C->E: 50 (C nợ 50, E cần 50)
        transactions = LinkedList[BasicTransaction]()
        transactions.append(BasicTransaction("A", "B", 100.0))
        transactions.append(BasicTransaction("B", "C", 80.0))
        transactions.append(BasicTransaction("C", "A", 60.0))
        transactions.append(BasicTransaction("C", "D", 70.0))
        transactions.append(BasicTransaction("D", "E", 50.0))
        simplifier = DynamicProgrammingSimplifier(transactions)
        simplified = simplifier.simplify()

        expected = [("A", "B", 20.0), ("A", "D", 20.0), ("C", "E", 50.0)]
        self.assertTransactionsMatch(simplified, expected)
        print("💸 Kết quả:")
        current = simplified.head
        while current: print(f"  {current.data.debtor} → {current.data.creditor} = ${current.data.amount:.2f}"); current = current.next
        print("✅ DP Kiểm thử 5 bên phức tạp thành công")

if __name__ == '__main__':
    unittest.main(verbosity=2)