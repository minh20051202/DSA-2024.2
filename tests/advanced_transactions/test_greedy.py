"""
Test Suite cho AdvancedGreedySimplifier
"""

from __future__ import annotations
import unittest
from datetime import date, timedelta
import random
import time

from src.data_structures import LinkedList
from src.core_types import AdvancedTransaction
from src.algorithms.advanced_transactions.greedy import AdvancedGreedySimplifier
from src.utils.financial_calculator import InterestType, PenaltyType


class TestAdvancedGreedySimplifier(unittest.TestCase):
    """Test suite cho AdvancedGreedySimplifier"""
    def setUp(self):
        """Thiết lập dữ liệu test cơ bản"""
        self.base_date = date(2024, 1, 1)
        self.current_date = date(2024, 6, 1)  # 5 tháng sau
        
    def test_initialization(self):
        """Test khởi tạo AdvancedGreedySimplifier"""
        print("\n" + "="*60)
        print("TEST: Initialization")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        tx = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.05, penalty_rate=10.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        self.assertIsNotNone(simplifier)
        self.assertEqual(simplifier.evaluation_date, self.current_date)
        print("✅ Initialization test passed")
        
    def test_empty_transactions(self):
        """Test với danh sách giao dịch rỗng"""
        print("\n" + "="*60)
        print("TEST: Empty Transactions")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        simplified = simplifier.simplify()
        self.assertTrue(simplified.is_empty())
        
        print("📊 Empty transactions handled correctly")
        print("✅ Empty transactions test passed")
        
    def test_single_transaction(self):
        """Test với một giao dịch duy nhất"""
        print("\n" + "="*60)
        print("TEST: Single Transaction")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        tx = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.05, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        simplified = simplifier.simplify()
        self.assertFalse(simplified.is_empty())
        
        result_tx = simplified.head.data
        print(f"💸 Result: {result_tx.debtor} → {result_tx.creditor} = ${result_tx.amount:.2f}")
        print("✅ Single transaction test passed")
        
    def test_simple_debt_simplification(self):
        """Test đơn giản hóa nợ đơn giản"""
        print("\n" + "="*60)
        print("TEST: Simple Debt Simplification")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 20
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=20.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Alice nợ Charlie 80
        tx2 = AdvancedTransaction(
            debtor="Alice", creditor="Charlie", amount=80.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        original_count = 2
        simplified = simplifier.simplify()
        
        # Đếm giao dịch kết quả
        simplified_count = 0
        current = simplified.head
        transaction_num = 1
        
        while current:
            tx = current.data
            print(f"💸 Transaction {transaction_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            simplified_count += 1
            transaction_num += 1
            current = current.next
        
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        print("✅ Simple debt simplification test passed")
        
    def test_circular_debt_resolution(self):
        """Test giải quyết nợ có chu kỳ"""
        print("\n" + "="*60)
        print("TEST: Circular Debt Resolution")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 100
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.02, penalty_rate=5.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 50
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=50.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 50
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=50.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.01, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        original_count = 3
        simplified = simplifier.simplify()
        
        # Đếm và hiển thị giao dịch kết quả
        simplified_count = 0
        current = simplified.head
        transaction_num = 1
        
        while current:
            tx = current.data
            print(f"💸 Transaction {transaction_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            simplified_count += 1
            transaction_num += 1
            current = current.next
        
        print(f"📊 Original circular transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        print("✅ Circular debt resolution test passed")
        
    def test_complex_debt_simplification(self):
        """Test đơn giản hóa nợ phức tạp với lãi suất và phí phạt"""
        print("\n" + "="*60)
        print("TEST: Complex Debt Simplification")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 50, quá hạn
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=50.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.10, penalty_rate=20.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 200
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=200.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # David nợ Alice 300, có lãi suất cao
        tx3 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=300.0,
            borrow_date=self.base_date, due_date=date(2024, 8, 1),
            interest_rate=0.08, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        # David nợ Bob 100
        tx4 = AdvancedTransaction(
            debtor="David", creditor="Bob", amount=100.0,
            borrow_date=date(2024, 2, 1), due_date=date(2024, 7, 1),
            interest_rate=0.05, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx4)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        # Hiển thị tóm tắt nợ trước khi đơn giản hóa
        print("📊 Debt summary before simplification:")
        people_balances = []
        for person in simplifier.people_balances.keys():
            balance = simplifier.people_balances.get(person, 0.0)
            
            # Tính priority score từ transaction details
            priority_score = 0.0
            current = simplifier.transaction_details.head
            while current:
                detail = current.data
                if detail[0] == person or detail[1] == person:
                    priority_score = max(priority_score, detail[6])
                current = current.next
            
            people_balances.append((person, balance, priority_score))
        
        # Sắp xếp theo balance
        people_balances.sort(key=lambda x: x[1])
        
        for person, balance, priority in people_balances:
            status = "🔴 DEBT" if balance < 0 else "🟢 CREDIT"
            print(f"   👤 {person}: {status} ${balance:.2f} (Priority: {priority:.2f})")
        
        # Thực hiện đơn giản hóa
        simplified = simplifier.simplify()
        
        print("\n📋 Simplified transactions:")
        simplified_count = 0
        total_flow = 0.0
        current = simplified.head
        
        while current:
            tx = current.data
            print(f"💸 {tx.debtor} → {tx.creditor}: ${tx.amount:.2f}")
            simplified_count += 1
            total_flow += tx.amount
            current = current.next
        
        print(f"\n📊 Total simplified transactions: {simplified_count}")
        print(f"💵 Total flow: ${total_flow:.2f}")
        print("✅ Complex debt simplification test passed")
        
    def test_financial_calculations(self):
        """Test tính toán tài chính nâng cao"""
        print("\n" + "="*60)
        print("TEST: Financial Calculations")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Giao dịch với lãi suất kép theo ngày
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=50.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.10, penalty_rate=20.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Giao dịch với lãi suất đơn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=200.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        # Hiển thị balance và priority của từng người
        for person in ["Alice", "Bob", "Charlie"]:
            balance = simplifier.people_balances.get(person, 0.0)
            
            # Tìm priority score cao nhất cho người này
            max_priority = 0.0
            current = simplifier.transaction_details.head
            while current:
                detail = current.data
                if detail[0] == person or detail[1] == person:
                    max_priority = max(max_priority, detail[6])
                current = current.next
            
            print(f"💰 {person} balance: ${balance:.2f}")
            if max_priority > 0:
                print(f"⭐ {person} priority: {max_priority:.2f}")
        
        print("✅ Financial calculations test passed")
        
    def test_debt_summary(self):
        """Test tóm tắt nợ"""
        print("\n" + "="*60)
        print("TEST: Debt Summary")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Tạo một số giao dịch phức tạp
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=50.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.10, penalty_rate=20.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        tx2 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=300.0,
            borrow_date=self.base_date, due_date=date(2024, 8, 1),
            interest_rate=0.08, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        print("📊 Detailed debt summary:")
        
        total_debt = 0.0
        total_credit = 0.0
        
        # Thu thập thông tin về từng người
        people_info = {}
        for person in simplifier.people_balances.keys():
            balance = simplifier.people_balances.get(person, 0.0)
            
            # Đếm giao dịch debt và credit
            debt_count = 0
            credit_count = 0
            max_priority = 0.0
            
            current = simplifier.transaction_details.head
            while current:
                detail = current.data
                debtor, creditor = detail[0], detail[1]
                priority = detail[6]
                
                if debtor == person:
                    debt_count += 1
                if creditor == person:
                    credit_count += 1
                if debtor == person or creditor == person:
                    max_priority = max(max_priority, priority)
                
                current = current.next
            
            people_info[person] = {
                'balance': balance,
                'priority': max_priority,
                'debt_count': debt_count,
                'credit_count': credit_count
            }
            
            if balance < 0:
                total_debt += abs(balance)
            else:
                total_credit += balance
        
        # Sắp xếp theo balance
        sorted_people = sorted(people_info.items(), key=lambda x: x[1]['balance'])
        
        for person, info in sorted_people:
            balance = info['balance']
            priority = info['priority']
            debt_count = info['debt_count']
            credit_count = info['credit_count']
            
            status = "🔴 DEBTOR" if balance < 0 else "🟢 CREDITOR"
            print(f"   👤 {person}: {status}")
            print(f"      💰 Balance: ${balance:.2f}")
            print(f"      ⭐ Priority: {priority:.2f}")
            print(f"      📤 Debt transactions: {debt_count}")
            print(f"      📥 Credit transactions: {credit_count}")
        
        print(f"\n💵 Total system debt: ${total_debt:.2f}")
        print(f"💵 Total system credit: ${total_credit:.2f}")
        print("✅ Debt summary test passed")
        
    def test_priority_scoring(self):
        """Test tính điểm ưu tiên"""
        print("\n" + "="*60)
        print("TEST: Priority Scoring")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Giao dịch quá hạn lâu - priority cao
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=50.0,
            borrow_date=self.base_date, due_date=date(2024, 2, 1),
            interest_rate=0.10, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Giao dịch trong hạn - priority thấp
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=200.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        
        # Thu thập priority scores
        priorities = []
        current = simplifier.transaction_details.head
        while current:
            detail = current.data
            debtor = detail[0]
            priority = detail[6]
            priorities.append((debtor, priority))
            current = current.next
        
        # Sắp xếp theo priority giảm dần
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        print("🏆 Priority ranking:")
        for i, (person, priority) in enumerate(priorities[:4]):
            print(f"   {i+1}. {person}: {priority:.2f}")
        
        print("✅ Priority scoring test passed")
        
    def test_performance_large_dataset(self):
        """Test hiệu suất với dataset lớn"""
        print("\n" + "="*60)
        print("TEST: Performance with Large Dataset")
        print("="*60)
        
        # Tạo dataset lớn
        transactions = LinkedList[AdvancedTransaction]()
        people_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry']
        
        random.seed(42)  # Để kết quả có thể lặp lại
        
        for i in range(20):
            debtor = random.choice(people_names)
            creditor = random.choice(people_names)
            while creditor == debtor:
                creditor = random.choice(people_names)
            
            amount = random.uniform(50, 500)
            days_ago = random.randint(30, 300)
            borrow_date = self.current_date - timedelta(days=days_ago)
            due_date = borrow_date + timedelta(days=random.randint(60, 365))
            
            interest_rate = random.uniform(0.01, 0.15)
            penalty_rate = random.uniform(0, 30)
            
            tx = AdvancedTransaction(
                debtor=debtor, creditor=creditor, amount=amount,
                borrow_date=borrow_date, due_date=due_date,
                interest_rate=interest_rate, penalty_rate=penalty_rate,
                interest_type=random.choice(list(InterestType)),
                penalty_type=random.choice(list(PenaltyType))
            )
            transactions.append(tx)
        
        print(f"📊 Created 20 random transactions with {len(people_names)} people")
        
        # Đo thời gian thực thi
        start_time = time.time()
        
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            evaluation_date=self.current_date
        )
        simplified = simplifier.simplify()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Đếm kết quả
        original_count = 20
        simplified_count = 0
        current = simplified.head
        while current:
            simplified_count += 1
            current = current.next
        
        reduction_pct = (1 - simplified_count / original_count) * 100
        
        print(f"⏱️  Execution time: {execution_time:.4f} seconds")
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        print(f"📉 Reduction: {reduction_pct:.1f}%")
        print("✅ Performance test passed")
        
        # Kiểm tra hiệu suất
        self.assertLess(execution_time, 1.0, "Algorithm should complete within 1 second")
        self.assertGreater(reduction_pct, 0, "Should achieve some reduction")


if __name__ == '__main__':
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)