"""
Test Suite cho AdvancedDebtCycleSimplifier

"""

from __future__ import annotations
import unittest
from datetime import date, timedelta
import random
import time

from src.data_structures import LinkedList
from src.core_types import AdvancedTransaction
from src.algorithms.advanced_transactions.cycle_detector import AdvancedDebtCycleSimplifier
from src.utils.financial_calculator import InterestType, PenaltyType

class TestAdvancedDebtCycleSimplifier(unittest.TestCase):
    """Test suite cho thuật toán AdvancedDebtCycleSimplifier"""
    
    def setUp(self):
        """Khởi tạo dữ liệu test"""
        self.base_date = date(2024, 1, 1)
        self.current_date = date(2024, 6, 1)
        self.past_due_date = date(2024, 3, 1)
        
    def test_initialization(self):
        """Test khởi tạo AdvancedDebtCycleSimplifier"""
        print("\n" + "="*60)
        print("TEST: Advanced Debt Cycle Simplifier Initialization")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        self.assertIsNotNone(simplifier)
        self.assertEqual(simplifier.calculation_date, self.current_date)
        self.assertTrue(simplifier.advanced_transactions.is_empty())
        print("✅ Initialization test passed")
        
    def test_empty_transactions(self):
        """Test với danh sách giao dịch rỗng"""
        print("\n" + "="*60)
        print("TEST: Empty Transactions")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        result = simplifier.simplify_advanced()
        self.assertTrue(result.is_empty())
        print("📊 Empty transactions handled correctly")
        print("✅ Empty transactions test passed")
        
    def test_single_transaction(self):
        """Test với một giao dịch duy nhất"""
        print("\n" + "="*60)
        print("TEST: Single Advanced Transaction")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 100$ với lãi suất kép hàng tháng
        tx = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.05, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx)
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        result = simplifier.simplify_advanced()
        self.assertEqual(result.get_length(), 1)
        
        tx_result = result.head.data
        total_debt = tx.calculate_total_debt(self.current_date)
        print(f"💸 Result: {tx_result.debtor} → {tx_result.creditor} = ${tx_result.amount:.2f}")
        print(f"💰 Original debt with interest: ${total_debt:.2f}")
        print("✅ Single transaction test passed")

    def test_simple_cycle_elimination(self):
        """Test loại bỏ chu trình đơn giản"""
        print("\n" + "="*60)
        print("TEST: Simple Cycle Elimination")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Tạo chu trình: Alice → Bob → Charlie → Alice
        # Alice nợ Bob 100$ với lãi suất
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 80$ với lãi suất cao hơn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=80.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 60$ với phí phạt
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=60.0,
            borrow_date=self.base_date, due_date=self.past_due_date,
            interest_rate=0.01, penalty_rate=10.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        original_count = 3
        result = simplifier.simplify_advanced()
        
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {result.get_length()}")
        
        # Hiển thị kết quả
        transaction_num = 1
        current = result.head
        while current:
            tx = current.data
            print(f"💸 Transaction {transaction_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            transaction_num += 1
            current = current.next
        
        # Hiển thị báo cáo tài chính
        report = simplifier.get_detailed_report()
        print("\n📋 Financial Report:")
        print(report)
        
        print("✅ Simple cycle elimination test passed")

    def test_complex_financial_calculations(self):
        """Test tính toán tài chính phức tạp với lãi suất và phí phạt"""
        print("\n" + "="*60)
        print("TEST: Complex Financial Calculations")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob - quá hạn với phí phạt cao
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=50.0,
            borrow_date=self.base_date, due_date=self.past_due_date,
            interest_rate=0.08, penalty_rate=25.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie - lãi suất kép hàng tháng
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=200.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.06, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # David nợ Alice - priority cao
        tx3 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=300.0,
            borrow_date=self.base_date, due_date=date(2024, 8, 1),
            interest_rate=0.10, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        # Charlie nợ David - tạo thêm chu trình
        tx4 = AdvancedTransaction(
            debtor="Charlie", creditor="David", amount=150.0,
            borrow_date=date(2024, 2, 1), due_date=date(2024, 7, 1),
            interest_rate=0.04, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx4)
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        # Hiển thị tính toán tài chính trước khi đơn giản hóa
        print("💰 Financial calculations before simplification:")
        for tx_node in transactions:
            tx = tx_node.data
            total_debt = tx.calculate_total_debt(self.current_date)
            priority = tx.get_priority_score(self.current_date)
            breakdown = tx.get_debt_breakdown(self.current_date)
            
            print(f"   📄 {tx.debtor} → {tx.creditor}:")
            print(f"      💵 Original: ${tx.amount:.2f}")
            print(f"      💰 Total debt: ${total_debt:.2f}")
            print(f"      📈 Interest: ${breakdown['interest']:.2f}")
            print(f"      ⚠️  Penalty: ${breakdown['penalty']:.2f}")
            print(f"      ⭐ Priority: {priority:.2f}")
        
        # Thực hiện đơn giản hóa
        result = simplifier.simplify_advanced()
        
        print(f"\n📊 Original transactions: 4")
        print(f"📊 Simplified transactions: {result.get_length()}")
        
        # Hiển thị kết quả đơn giản hóa
        print("\n📋 Simplified transactions:")
        current = result.head
        total_flow = 0.0
        while current:
            tx = current.data
            print(f"💸 {tx.debtor} → {tx.creditor}: ${tx.amount:.2f}")
            total_flow += tx.amount
            current = current.next
        
        print(f"💵 Total flow: ${total_flow:.2f}")
        
        # Hiển thị báo cáo chi tiết
        report = simplifier.get_detailed_report()
        print("\n" + "="*40)
        print(report)
        
        print("✅ Complex financial calculations test passed")

    def test_priority_based_optimization(self):
        """Test tối ưu hóa dựa trên độ ưu tiên"""
        print("\n" + "="*60)
        print("TEST: Priority-Based Optimization")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Giao dịch priority cao - quá hạn lâu
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=date(2023, 6, 1), due_date=date(2023, 12, 1),
            interest_rate=0.12, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Giao dịch priority thấp - chưa đến hạn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=200.0,
            borrow_date=self.current_date, due_date=date(2024, 12, 1),
            interest_rate=0.01, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Giao dịch priority trung bình
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=150.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.05, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        # Hiển thị priority ranking
        print("🏆 Priority ranking:")
        priority_list = []
        for tx_node in transactions:
            tx = tx_node.data
            priority = tx.get_priority_score(self.current_date)
            priority_list.append((f"{tx.debtor}→{tx.creditor}", priority))
        
        priority_list.sort(key=lambda x: x[1], reverse=True)
        for i, (desc, priority) in enumerate(priority_list, 1):
            print(f"   {i}. {desc}: {priority:.2f}")
        
        result = simplifier.simplify_advanced()
        
        print(f"\n📊 Simplified transactions: {result.get_length()}")
        current = result.head
        while current:
            tx = current.data
            print(f"💸 {tx.debtor} → {tx.creditor}: ${tx.amount:.2f}")
            current = current.next
        
        print("✅ Priority-based optimization test passed")

    def test_multiple_cycles_elimination(self):
        """Test loại bỏ nhiều chu trình"""
        print("\n" + "="*60)
        print("TEST: Multiple Cycles Elimination")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Chu trình 1: A → B → C → A
        transactions.append(AdvancedTransaction("Alice", "Bob", 100.0, self.base_date, self.current_date, 0.02))
        transactions.append(AdvancedTransaction("Bob", "Charlie", 80.0, self.base_date, self.current_date, 0.03))
        transactions.append(AdvancedTransaction("Charlie", "Alice", 60.0, self.base_date, self.current_date, 0.01))
        
        # Chu trình 2: D → E → F → D
        transactions.append(AdvancedTransaction("David", "Eve", 150.0, self.base_date, self.current_date, 0.04))
        transactions.append(AdvancedTransaction("Eve", "Frank", 120.0, self.base_date, self.current_date, 0.02))
        transactions.append(AdvancedTransaction("Frank", "David", 90.0, self.base_date, self.current_date, 0.01))
        
        # Kết nối giữa các chu trình
        transactions.append(AdvancedTransaction("Alice", "David", 50.0, self.base_date, self.current_date, 0.01))
        transactions.append(AdvancedTransaction("Eve", "Bob", 30.0, self.base_date, self.current_date, 0.01))
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        original_count = transactions.get_length()
        result = simplifier.simplify_advanced()
        
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {result.get_length()}")
        print(f"📉 Reduction: {((original_count - result.get_length()) / original_count * 100):.1f}%")
        
        # Hiển thị báo cáo tài chính
        summary = simplifier.get_financial_summary()
        if not summary.is_empty():
            print(f"💰 Original debt total: ${summary.get('original_debt_total', 0):.2f}")
            print(f"💰 Simplified debt total: ${summary.get('simplified_debt_total', 0):.2f}")
            print(f"💵 Savings: ${summary.get('debt_reduction', 0):.2f}")
        
        print("✅ Multiple cycles elimination test passed")

    def test_performance_large_dataset(self):
        """Test hiệu suất với dataset lớn"""
        print("\n" + "="*60)
        print("TEST: Performance with Large Dataset")
        print("="*60)
        
        # Tạo dataset lớn với 50 giao dịch
        transactions = LinkedList[AdvancedTransaction]()
        people = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"]
        
        random.seed(42)  # Để có kết quả nhất quán
        
        for i in range(50):
            debtor = random.choice(people)
            creditor = random.choice(people)
            while creditor == debtor:
                creditor = random.choice(people)
            
            amount = random.uniform(10.0, 500.0)
            interest_rate = random.uniform(0.01, 0.15)
            penalty_rate = random.uniform(0.0, 30.0) if random.random() > 0.7 else 0.0
            
            # Một số giao dịch quá hạn
            if random.random() > 0.6:
                due_date = self.past_due_date
            else:
                due_date = date(2024, 12, 1)
            
            tx = AdvancedTransaction(
                debtor=debtor, creditor=creditor, amount=amount,
                borrow_date=self.base_date, due_date=due_date,
                interest_rate=interest_rate, penalty_rate=penalty_rate,
                interest_type=random.choice([InterestType.SIMPLE, InterestType.COMPOUND_MONTHLY]),
                penalty_type=PenaltyType.FIXED
            )
            transactions.append(tx)
        
        print(f"📊 Created {transactions.get_length()} random transactions with {len(people)} people")
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        # Đo thời gian thực thi
        start_time = time.time()
        result = simplifier.simplify_advanced()
        execution_time = time.time() - start_time
        
        original_count = transactions.get_length()
        simplified_count = result.get_length()
        reduction_percent = (original_count - simplified_count) / original_count * 100
        
        print(f"⏱️  Execution time: {execution_time:.4f} seconds")
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        print(f"📉 Reduction: {reduction_percent:.1f}%")
        
        # Kiểm tra hiệu suất
        self.assertLess(execution_time, 1.0, "Algorithm should complete within 1 second for 50 transactions")
        self.assertGreater(reduction_percent, 10, "Should achieve at least 10% reduction")
        
        print("✅ Performance test passed")

    def test_financial_summary_accuracy(self):
        """Test tính chính xác của tóm tắt tài chính"""
        print("\n" + "="*60)
        print("TEST: Financial Summary Accuracy")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Giao dịch có lãi suất kép
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=1000.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.10, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Giao dịch có phí phạt
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=500.0,
            borrow_date=self.base_date, due_date=self.past_due_date,
            interest_rate=0.05, penalty_rate=100.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedDebtCycleSimplifier(
            advanced_transactions=transactions,
            calculation_date=self.current_date
        )
        
        # Tính toán thủ công để so sánh
        manual_total = 0.0
        manual_interest = 0.0
        manual_penalty = 0.0
        
        for tx_node in transactions:
            tx = tx_node.data
            breakdown = tx.get_debt_breakdown(self.current_date)
            manual_total += breakdown['total']
            manual_interest += breakdown['interest']
            manual_penalty += breakdown['penalty']
        
        print(f"💰 Manual calculation:")
        print(f"   Total debt: ${manual_total:.2f}")
        print(f"   Interest: ${manual_interest:.2f}")
        print(f"   Penalty: ${manual_penalty:.2f}")
        
        # Thực hiện đơn giản hóa
        result = simplifier.simplify_advanced()
        summary = simplifier.get_financial_summary()
        
        print(f"\n💰 Algorithm summary:")
        print(f"   Original total: ${summary.get('original_debt_total', 0):.2f}")
        print(f"   Interest total: ${summary.get('original_interest_total', 0):.2f}")
        print(f"   Penalty total: ${summary.get('original_penalty_total', 0):.2f}")
        
        # Kiểm tra tính chính xác
        self.assertAlmostEqual(manual_total, summary.get('original_debt_total', 0), places=2)
        self.assertAlmostEqual(manual_interest, summary.get('original_interest_total', 0), places=2)
        self.assertAlmostEqual(manual_penalty, summary.get('original_penalty_total', 0), places=2)
        
        print("✅ Financial summary accuracy test passed")

if __name__ == '__main__':
    unittest.main(verbosity=2)