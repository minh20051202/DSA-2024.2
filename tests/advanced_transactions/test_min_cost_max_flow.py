from __future__ import annotations
import unittest
from datetime import date, timedelta
import random

from src.data_structures import LinkedList
from src.core_type import AdvancedTransaction, BasicTransaction # Import BasicTransaction
from src.utils.financial_calculator import InterestType, PenaltyType, FinancialCalculator
from src.algorithms.advanced_transactions.min_cost_max_flow import AdvancedMinCostMaxFlowSimplifier
from src.utils.constants import EPSILON


class TestAdvancedMinCostMaxFlowSimplifier(unittest.TestCase):
    """Bộ test cho lớp AdvancedMinCostMaxFlowSimplifier"""

    def setUp(self):
        """Khởi tạo dữ liệu test cho mỗi trường hợp kiểm thử"""
        self.base_date = date(2024, 1, 1)
        self.current_date = date(2024, 6, 1)  # 5 tháng sau (152 ngày nếu 2024 là năm nhuận cho tháng 2)
        self.calculator = FinancialCalculator()

    # Helper function để tạo AdvancedTransaction
    def create_adv_tx(self, debtor: str, creditor: str, amount: float,
                      borrow_date: date, due_date: date,
                      interest_rate: float = 0.0, penalty_rate: float = 0.0,
                      interest_type: InterestType = InterestType.SIMPLE,
                      penalty_type: PenaltyType = PenaltyType.FIXED) -> AdvancedTransaction:
        return AdvancedTransaction(debtor, creditor, amount, borrow_date, due_date,
                                   interest_rate, penalty_rate, interest_type, penalty_type)
    
    def test_initialization(self):
        """Kiểm thử việc khởi tạo AdvancedMinCostMaxFlowSimplifier"""
        print("\n" + "="*60)
        print("KIỂM THỬ: Khởi tạo")
        print("="*60)
        transactions = LinkedList[AdvancedTransaction]()
        transactions.append(self.create_adv_tx("Alice", "Bob", 100, self.base_date, self.current_date + timedelta(days=30)))
        transactions.append(self.create_adv_tx("Bob", "Charlie", 80, self.base_date, self.current_date + timedelta(days=30)))
        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        self.assertIsNotNone(simplifier.people_balances)
        # ... (các assert khác của bạn) ...
        print("✅ Kiểm thử khởi tạo đã thành công")

    def test_simple_debt_no_cycle_no_interest_penalty(self): # Đổi tên cho rõ
        """Kiểm thử đơn giản hóa nợ đơn giản, không chu trình, không lãi/phạt"""
        print("\n" + "="*60)
        print("KIỂM THỬ: Đơn giản hóa, không chu trình, không lãi/phạt")
        print("="*60)
        transactions = LinkedList[AdvancedTransaction]()
        tx1 = self.create_adv_tx("Alice", "Bob", 100, self.base_date, self.current_date + timedelta(days=30))
        transactions.append(tx1)
        tx2 = self.create_adv_tx("Bob", "Charlie", 80, self.base_date, self.current_date + timedelta(days=30))
        transactions.append(tx2)
        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        simplified = simplifier.simplify() # Kết quả là LinkedList[BasicTransaction]

        original_count = 2
        simplified_count = len(simplified)
        print(f"📊 Số giao dịch ban đầu: {original_count}")
        print(f"📊 Số giao dịch sau khi đơn giản hóa: {simplified_count}")
        
        # Kỳ vọng: Alice -> Bob: 100, Bob -> Charlie: 80 (vì không có cách nào gộp)
        # Hoặc Alice -> Charlie: 80, Alice -> Bob: 20 (nếu thuật toán tối ưu theo dòng tiền tổng thể)
        # MinCostMaxFlow nên tìm ra cách tối ưu hơn là giữ nguyên
        # Net balances: Alice: -100, Bob: +100 - 80 = +20, Charlie: +80
        # Expected: Alice -> Charlie: 80, Alice -> Bob: 20
        self.assertEqual(simplified_count, 2, "Kỳ vọng 2 giao dịch được tối ưu")
        
        results_map = {}
        current = simplified.head
        tx_num = 1
        while current:
            tx = current.data
            print(f"💸 Giao dịch {tx_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            results_map[f"{tx.debtor}->{tx.creditor}"] = tx.amount
            tx_num += 1
            current = current.next
        
        self.assertAlmostEqual(results_map.get("Alice->Charlie", 0.0), 80.0, delta=EPSILON)
        self.assertAlmostEqual(results_map.get("Alice->Bob", 0.0), 20.0, delta=EPSILON)
        print("✅ Kiểm thử đơn giản hóa, không chu trình, không lãi/phạt thành công")

    def test_circular_debt_no_interest_penalty(self): # Đổi tên cho rõ
        """Kiểm thử giải quyết nợ có chu trình, không lãi/phạt"""
        print("\n" + "="*60)
        print("KIỂM THỬ: Giải quyết nợ chu trình, không lãi/phạt")
        print("="*60)
        transactions = LinkedList[AdvancedTransaction]()
        # A -> B: 300
        # B -> C: 250
        # C -> A: 200
        # Min cycle amount = 200.
        # After cycle: A->B: 100, B->C: 50. C->A: 0.
        # Expected: A->B: 100, B->C: 50 (2 transactions)
        # Hoặc A->C: 50, A->B: 50 (nếu tối ưu hơn)
        # Net balances: A: -300+200 = -100, B: +300-250 = +50, C: +250-200 = +50
        # Expected (optimal): A->B: 50, A->C: 50
        transactions.append(self.create_adv_tx("Alice", "Bob", 300, self.base_date, self.current_date + timedelta(days=30)))
        transactions.append(self.create_adv_tx("Bob", "Charlie", 250, self.base_date, self.current_date + timedelta(days=30)))
        transactions.append(self.create_adv_tx("Charlie", "Alice", 200, self.base_date, self.current_date + timedelta(days=30)))
        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        simplified = simplifier.simplify()

        simplified_count = len(simplified)
        print(f"📊 Số giao dịch chu trình ban đầu: 3")
        print(f"📊 Số giao dịch sau khi đơn giản hóa: {simplified_count}")
        self.assertEqual(simplified_count, 2, "Kỳ vọng 2 giao dịch sau khi giải quyết chu trình")

        results_map = {}
        current = simplified.head; tx_num=1
        while current:
            tx = current.data
            print(f"💸 Giao dịch {tx_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            results_map[f"{tx.debtor}->{tx.creditor}"] = tx.amount
            tx_num+=1; current = current.next
        
        self.assertAlmostEqual(results_map.get("Alice->Bob", 0.0), 50.0, delta=EPSILON)
        self.assertAlmostEqual(results_map.get("Alice->Charlie", 0.0), 50.0, delta=EPSILON)
        print("✅ Kiểm thử giải quyết nợ chu trình, không lãi/phạt thành công")

    def test_empty_transactions_list(self): # Đổi tên cho nhất quán
        """Kiểm thử với danh sách giao dịch rỗng"""
        print("\n" + "="*60)
        print("KIỂM THỬ: Danh sách giao dịch rỗng")
        print("="*60)
        empty_transactions = LinkedList[AdvancedTransaction]()
        simplifier = AdvancedMinCostMaxFlowSimplifier(empty_transactions, self.current_date)
        simplified = simplifier.simplify()
        self.assertTrue(simplified.is_empty())
        print("📊 Đã xử lý chính xác danh sách giao dịch rỗng")
        print("✅ Kiểm thử danh sách giao dịch rỗng thành công")


    def test_single_transaction_with_interest_and_penalty(self):
        """Kiểm thử một giao dịch đơn lẻ có lãi và phạt."""
        print("\n" + "="*60)
        print("KIỂM THỬ MỚI: Giao dịch đơn lẻ với lãi và phạt")
        print("="*60)
        
        due_date_tx = date(2024, 3, 1) 
        tx_params_for_creation = { # Params để tạo AdvancedTransaction
            "debtor": "David", "creditor": "Eve", "amount": 1000.0,
            "borrow_date": self.base_date, "due_date": due_date_tx,
            "interest_rate": 0.12, "penalty_rate": 50.0, 
            "interest_type": InterestType.COMPOUND_MONTHLY, "penalty_type": PenaltyType.FIXED
        }
        transactions = LinkedList[AdvancedTransaction]()
        transactions.append(self.create_adv_tx(**tx_params_for_creation))

        # TẠO DICTIONARY CHỈ CHỨA CÁC THAM SỐ CHO calculate_total_debt
        params_for_calculator = {
            "amount": tx_params_for_creation["amount"],
            "interest_rate": tx_params_for_creation["interest_rate"],
            "penalty_rate": tx_params_for_creation["penalty_rate"],
            "borrow_date": tx_params_for_creation["borrow_date"],
            "due_date": tx_params_for_creation["due_date"],
            "interest_type": tx_params_for_creation["interest_type"],
            "penalty_type": tx_params_for_creation["penalty_type"]
            # current_date sẽ được truyền riêng
        }

        expected_breakdown = self.calculator.calculate_total_debt(
            **params_for_calculator, # Unpack dictionary đã được lọc
            current_date=self.current_date
        )
        expected_total_debt = expected_breakdown["total"]
        print(f"  Tính toán kỳ vọng: Gốc={expected_breakdown['principal']:.2f}, Lãi={expected_breakdown['interest']:.2f}, Phạt={expected_breakdown['penalty']:.2f}, Tổng={expected_total_debt:.2f}")

        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        simplified = simplifier.simplify()

        self.assertEqual(len(simplified), 1, "Kỳ vọng 1 giao dịch")
        result_tx = simplified.head.data
        print(f"💸 Giao dịch đơn giản hóa: {result_tx.debtor} → {result_tx.creditor} = ${result_tx.amount:.2f}")

        self.assertEqual(result_tx.debtor, "David")
        self.assertEqual(result_tx.creditor, "Eve")
        self.assertAlmostEqual(result_tx.amount, expected_total_debt, delta=0.01)
        print("✅ Kiểm thử giao dịch đơn lẻ với lãi/phạt thành công")

    def test_two_transactions_cancel_out_with_finance(self):
        """Kiểm thử hai giao dịch ngược chiều có thể triệt tiêu một phần sau khi tính lãi/phạt."""
        print("\n" + "="*60)
        print("KIỂM THỬ MỚI: Hai giao dịch ngược chiều, triệt tiêu một phần với lãi/phạt")
        print("="*60)

        transactions = LinkedList[AdvancedTransaction]()
        
        tx1_params_for_creation = {
            "debtor": "Frank", "creditor": "Grace", "amount": 500.0,
            "borrow_date": self.base_date, "due_date": date(2024, 4, 1), 
            "interest_rate": 0.10, "penalty_rate": 0.05, 
            "interest_type": InterestType.SIMPLE, "penalty_type": PenaltyType.PERCENTAGE
        }
        transactions.append(self.create_adv_tx(**tx1_params_for_creation))
        
        tx2_params_for_creation = {
            "debtor": "Grace", "creditor": "Frank", "amount": 300.0,
            "borrow_date": date(2024, 2, 1), "due_date": date(2024, 5, 1), 
            "interest_rate": 0.08, "penalty_rate": 20.0, 
            "interest_type": InterestType.COMPOUND_DAILY, "penalty_type": PenaltyType.FIXED
        }
        transactions.append(self.create_adv_tx(**tx2_params_for_creation))

        # Helper function để trích xuất params cho calculator (có thể để ở setUp hoặc ngoài class)
        def get_calc_params_from_creation_dict(details_dict):
            return {
                "amount": details_dict["amount"],
                "interest_rate": details_dict["interest_rate"],
                "penalty_rate": details_dict["penalty_rate"],
                "borrow_date": details_dict["borrow_date"],
                "due_date": details_dict["due_date"],
                "interest_type": details_dict["interest_type"],
                "penalty_type": details_dict["penalty_type"]
            }

        val_tx1 = self.calculator.calculate_total_debt(
            **get_calc_params_from_creation_dict(tx1_params_for_creation), # Sử dụng dict đã lọc
            current_date=self.current_date
        )["total"]
        val_tx2 = self.calculator.calculate_total_debt(
            **get_calc_params_from_creation_dict(tx2_params_for_creation), # Sử dụng dict đã lọc
            current_date=self.current_date
        )["total"]
        
        print(f"  Giá trị thực tế TX1 (Frank->Grace): ${val_tx1:.2f}")
        print(f"  Giá trị thực tế TX2 (Grace->Frank): ${val_tx2:.2f}")
        
        # ... (phần còn lại của logic assert dựa trên val_tx1 và val_tx2) ...
        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        simplified = simplifier.simplify()

        if val_tx1 > val_tx2 + EPSILON:
            expected_debtor = "Frank"
            expected_creditor = "Grace"
            expected_amount = val_tx1 - val_tx2
            self.assertEqual(len(simplified), 1, "Kỳ vọng 1 giao dịch sau khi bù trừ")
            if not simplified.is_empty():
                result_tx = simplified.head.data
                print(f"💸 Giao dịch đơn giản hóa: {result_tx.debtor} → {result_tx.creditor} = ${result_tx.amount:.2f}")
                self.assertEqual(result_tx.debtor, expected_debtor)
                self.assertEqual(result_tx.creditor, expected_creditor)
                self.assertAlmostEqual(result_tx.amount, expected_amount, delta=0.01)
        elif val_tx2 > val_tx1 + EPSILON:
            expected_debtor = "Grace"
            expected_creditor = "Frank"
            expected_amount = val_tx2 - val_tx1
            self.assertEqual(len(simplified), 1, "Kỳ vọng 1 giao dịch sau khi bù trừ")
            if not simplified.is_empty():
                result_tx = simplified.head.data
                print(f"💸 Giao dịch đơn giản hóa: {result_tx.debtor} → {result_tx.creditor} = ${result_tx.amount:.2f}")
                self.assertEqual(result_tx.debtor, expected_debtor)
                self.assertEqual(result_tx.creditor, expected_creditor)
                self.assertAlmostEqual(result_tx.amount, expected_amount, delta=0.01)
        else: 
            print(f"💸 Giao dịch gần như triệt tiêu hoàn toàn.")
            self.assertTrue(simplified.is_empty() or simplified.head.data.amount < EPSILON * 100, 
                            "Kỳ vọng không có giao dịch hoặc giao dịch với số tiền rất nhỏ")

        print("✅ Kiểm thử hai giao dịch ngược chiều với lãi/phạt thành công")

    def test_complex_scenario_three_people_interest_penalty(self):
        """Kiểm thử kịch bản 3 người đã debug với AdvancedDebtCycleSimplifier."""
        print("\n" + "="*60)
        print("KIỂM THỬ MỚI: Kịch bản 3 người (Anna, Bob, Cathy) với lãi/phạt")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        tx1_details = {"debtor": "Anna", "creditor": "Bob", "amount": 100.00,
                       "borrow_date": self.base_date, "due_date": date(2024, 3, 1),
                       "interest_rate": 0.08, "penalty_rate": 15.00,
                       "interest_type": InterestType.COMPOUND_MONTHLY, "penalty_type": PenaltyType.FIXED}
        transactions.append(self.create_adv_tx(**tx1_details))

        tx2_details = {"debtor": "Bob", "creditor": "Cathy", "amount": 150.00,
                       "borrow_date": self.base_date, "due_date": date(2024, 4, 15),
                       "interest_rate": 0.05, "penalty_rate": 0.10, 
                       "interest_type": InterestType.SIMPLE, "penalty_type": PenaltyType.PERCENTAGE}
        transactions.append(self.create_adv_tx(**tx2_details))
        
        tx3_details = {"debtor": "Cathy", "creditor": "Anna", "amount": 90.00,
                       "borrow_date": self.base_date, "due_date": date(2024, 2, 10),
                       "interest_rate": 0.001, "penalty_rate": 20.00, 
                       "interest_type": InterestType.COMPOUND_DAILY, "penalty_type": PenaltyType.FIXED}
        transactions.append(self.create_adv_tx(**tx3_details))

        # Tính toán số dư ròng kỳ vọng (từ các lần debug trước)
        # Anna nợ ròng ~8.32-8.34
        # Bob nợ ròng ~49.75-49.76
        # Cathy được nhận ròng ~58.08-58.09
        # Kỳ vọng: Anna -> Cathy: ~8.34, Bob -> Cathy: ~49.75

        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        simplified = simplifier.simplify()

        self.assertEqual(len(simplified), 2, "Kỳ vọng 2 giao dịch sau khi đơn giản hóa kịch bản 3 người")

        print("💸 Các giao dịch đã được đơn giản hóa:")
        results_map = {}
        current = simplified.head; tx_num=1
        while current:
            tx = current.data
            print(f"  Giao dịch {tx_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            results_map[f"{tx.debtor}->{tx.creditor}"] = tx.amount
            tx_num+=1; current = current.next
            
        self.assertAlmostEqual(results_map.get("Anna->Cathy", 0.0), 8.34, delta=0.03)
        self.assertAlmostEqual(results_map.get("Bob->Cathy", 0.0), 49.75, delta=0.03)
        
        print("✅ Kiểm thử kịch bản 3 người với lãi/phạt thành công")

    def test_no_net_change_multiple_parties(self):
        """Kiểm thử trường hợp nhiều bên nhưng tổng nợ ròng bằng 0 cho mỗi người."""
        print("\n" + "="*60)
        print("KIỂM THỬ MỚI: Không thay đổi ròng, nhiều bên")
        print("="*60)
        transactions = LinkedList[AdvancedTransaction]()
        # A -> B: 100
        # B -> C: 100
        # C -> A: 100
        # (Không lãi/phạt, due date trong tương lai để tránh phạt)
        future_due = self.current_date + timedelta(days=30)
        transactions.append(self.create_adv_tx("A", "B", 100, self.base_date, future_due))
        transactions.append(self.create_adv_tx("B", "C", 100, self.base_date, future_due))
        transactions.append(self.create_adv_tx("C", "A", 100, self.base_date, future_due))
        # Thêm một cặp khác cũng tự triệt tiêu
        # D -> E: 50
        # E -> D: 50
        transactions.append(self.create_adv_tx("D", "E", 50, self.base_date, future_due))
        transactions.append(self.create_adv_tx("E", "D", 50, self.base_date, future_due))


        simplifier = AdvancedMinCostMaxFlowSimplifier(transactions, self.current_date)
        simplified = simplifier.simplify()

        print("💸 Các giao dịch đã được đơn giản hóa (kỳ vọng rỗng):")
        is_empty = True
        current = simplified.head
        while current:
            tx = current.data
            print(f"  Lỗi: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            is_empty = False
            current = current.next

        self.assertTrue(is_empty, "Kỳ vọng không có giao dịch nào sau khi đơn giản hóa")
        print("✅ Kiểm thử không thay đổi ròng, nhiều bên thành công")


if __name__ == '__main__':
    unittest.main(verbosity=2)