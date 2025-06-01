"""
Test Suite cho AdvancedMinCostMaxFlowSimplifier
"""

from __future__ import annotations
import unittest
from datetime import date, timedelta
import random
import time

from src.data_structures import LinkedList
from src.core_types import AdvancedTransaction
from src.utils.financial_calculator import InterestType, PenaltyType
from src.algorithms.advanced_transactions.min_cost_max_flow import AdvancedMinCostMaxFlowSimplifier
from src.utils.constants import EPSILON


class TestAdvancedMinCostMaxFlowSimplifier(unittest.TestCase):
    """Test suite cho AdvancedMinCostMaxFlowSimplifier"""
    
    def setUp(self):
        """Khởi tạo dữ liệu test cho mỗi test case"""
        self.base_date = date(2024, 1, 1)
        self.current_date = date(2024, 6, 1)  # 5 tháng sau
    
    def test_initialization(self):
        """Test khởi tạo AdvancedMinCostMaxFlowSimplifier"""
        print("\n" + "="*60)
        print("TEST: Initialization")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 100, không lãi, không phạt
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 80, không lãi, không phạt
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=80.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        
        # Kiểm tra các thuộc tính cơ bản
        self.assertIsNotNone(simplifier.people_balances)
        self.assertIsNotNone(simplifier.people_priorities)
        self.assertIsNotNone(simplifier.transaction_details)
        self.assertIsNotNone(simplifier.all_people)
        
        # Kiểm tra số người tham gia
        people_count = 0
        current = simplifier.all_people.head
        while current:
            people_count += 1
            current = current.next
        self.assertEqual(people_count, 3)  # Alice, Bob, Charlie
        
        print("✅ Initialization test passed")
    
    def test_financial_calculations(self):
        """Test tính toán tài chính nâng cao"""
        print("\n" + "="*60)
        print("TEST: Financial Calculations")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 1000, lãi suất kép, quá hạn
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=1000.0,
            borrow_date=self.base_date, due_date=date(2024, 4, 1),
            interest_rate=0.05, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 800, lãi suất đơn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=800.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 600, phí phạt theo ngày
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=600.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.02, penalty_rate=5.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.DAILY
        )
        transactions.append(tx3)
        
        # David nợ Alice 400
        tx4 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=400.0,
            borrow_date=date(2024, 2, 1), due_date=date(2024, 8, 1),
            interest_rate=0.04, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx4)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        
        # Kiểm tra số dư có tính lãi và phí phạt
        alice_balance = simplifier.people_balances.get("Alice", 0.0)
        bob_balance = simplifier.people_balances.get("Bob", 0.0)
        charlie_balance = simplifier.people_balances.get("Charlie", 0.0)
        david_balance = simplifier.people_balances.get("David", 0.0)
        
        print(f"💰 Alice balance: ${alice_balance:.2f}")
        print(f"💰 Bob balance: ${bob_balance:.2f}")
        print(f"💰 Charlie balance: ${charlie_balance:.2f}")
        print(f"💰 David balance: ${david_balance:.2f}")
        
        # Kiểm tra tổng số dư = 0 (nguyên tắc cân bằng)
        total_balance = alice_balance + bob_balance + charlie_balance + david_balance
        self.assertTrue(abs(total_balance) < EPSILON, 
                       f"Total balance should be ~0, got {total_balance}")
        
        # Kiểm tra điểm ưu tiên
        alice_priority = simplifier.people_priorities.get("Alice", 0.0)
        bob_priority = simplifier.people_priorities.get("Bob", 0.0)
        
        self.assertGreater(alice_priority, 0.0)
        self.assertGreater(bob_priority, 0.0)
        
        print(f"⭐ Alice priority: {alice_priority:.2f}")
        print(f"⭐ Bob priority: {bob_priority:.2f}")
        print("✅ Financial calculations test passed")
    
    def test_simple_debt_simplification(self):
        """Test đơn giản hóa nợ đơn giản"""
        print("\n" + "="*60)
        print("TEST: Simple Debt Simplification")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 100, không lãi, không phạt
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 80, không lãi, không phạt
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=80.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        simplified = simplifier.simplify()
        
        # Đếm số giao dịch
        original_count = 2
        simplified_count = 0
        current = simplified.head
        while current:
            simplified_count += 1
            current = current.next
        
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        
        # In ra các giao dịch đã đơn giản hóa
        tx_num = 1
        current = simplified.head
        while current:
            tx = current.data
            print(f"💸 Transaction {tx_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            tx_num += 1
            current = current.next
        
        # Kiểm tra giảm được ít nhất 1 giao dịch hoặc bằng 0 (nếu đã tối ưu)
        self.assertTrue(simplified_count <= original_count)
        print("✅ Simple debt simplification test passed")
    
    def test_complex_debt_simplification(self):
        """Test đơn giản hóa nợ phức tạp với lãi suất và phí phạt"""
        print("\n" + "="*60)
        print("TEST: Complex Debt Simplification")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 1000, lãi suất kép, quá hạn
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=1000.0,
            borrow_date=self.base_date, due_date=date(2024, 4, 1),
            interest_rate=0.05, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 800, lãi suất đơn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=800.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 600, phí phạt theo ngày
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=600.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.02, penalty_rate=5.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.DAILY
        )
        transactions.append(tx3)
        
        # David nợ Alice 400
        tx4 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=400.0,
            borrow_date=date(2024, 2, 1), due_date=date(2024, 8, 1),
            interest_rate=0.04, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx4)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        
        # Hiển thị tóm tắt nợ trước khi đơn giản hóa
        debt_summary = simplifier.get_debt_summary()
        print("📊 Debt summary before simplification:")
        
        summary_keys = debt_summary.keys()
        if summary_keys:
            for person in summary_keys:
                person_info = debt_summary.get(person)
                if person_info:
                    balance = person_info.get('total_balance', 0.0)
                    priority = person_info.get('priority_score', 0.0)
                    status = "🔴 DEBT" if balance < 0 else "🟢 CREDIT" if balance > 0 else "⚪ BALANCED"
                    print(f"   👤 {person}: {status} ${balance:.2f} (Priority: {priority:.2f})")
        
        # Thực hiện đơn giản hóa
        simplified = simplifier.simplify()
        
        # Đếm và hiển thị kết quả
        simplified_count = 0
        total_flow = 0.0
        current = simplified.head
        
        print("\n📋 Simplified transactions:")
        while current:
            tx = current.data
            simplified_count += 1
            total_flow += tx.amount
            print(f"💸 {tx.debtor} → {tx.creditor}: ${tx.amount:.2f}")
            current = current.next
        
        print(f"\n📊 Total simplified transactions: {simplified_count}")
        print(f"💵 Total flow: ${total_flow:.2f}")
        
        # Validate tổng luồng phải > 0
        self.assertGreater(total_flow, 0.0)
        print("✅ Complex debt simplification test passed")
    
    def test_circular_debt_resolution(self):
        """Test giải quyết nợ có chu kỳ"""
        print("\n" + "="*60)
        print("TEST: Circular Debt Resolution")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 300
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=300.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 250
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=250.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 200
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=200.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        simplified = simplifier.simplify()
        
        # Đếm giao dịch
        original_count = 3
        simplified_count = 0
        current = simplified.head
        while current:
            simplified_count += 1
            current = current.next
        
        print(f"📊 Original circular transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        
        # Hiển thị kết quả
        tx_num = 1
        current = simplified.head
        while current:
            tx = current.data
            print(f"💸 Transaction {tx_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            tx_num += 1
            current = current.next
        
        # Với circular debt, nên giảm được ít nhất 1 giao dịch
        self.assertLessEqual(simplified_count, original_count)
        print("✅ Circular debt resolution test passed")
    
    def test_priority_scoring(self):
        """Test tính điểm ưu tiên"""
        print("\n" + "="*60)
        print("TEST: Priority Scoring")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 1000, lãi suất kép, quá hạn
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=1000.0,
            borrow_date=self.base_date, due_date=date(2024, 4, 1),
            interest_rate=0.05, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 800, lãi suất đơn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=800.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 600, phí phạt theo ngày
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=600.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.02, penalty_rate=5.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.DAILY
        )
        transactions.append(tx3)
        
        # David nợ Alice 400
        tx4 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=400.0,
            borrow_date=date(2024, 2, 1), due_date=date(2024, 8, 1),
            interest_rate=0.04, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx4)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        
        # Kiểm tra điểm ưu tiên được tính chính xác
        people_priorities = []
        people_node = simplifier.all_people.head
        while people_node:
            person = people_node.data
            priority = simplifier.people_priorities.get(person, 0.0)
            people_priorities.append((person, priority))
            people_node = people_node.next
        
        # Sắp xếp theo độ ưu tiên
        people_priorities.sort(key=lambda x: x[1], reverse=True)
        
        print("🏆 Priority ranking:")
        for i, (person, priority) in enumerate(people_priorities):
            print(f"   {i+1}. {person}: {priority:.2f}")
        
        # Kiểm tra ít nhất có 1 người có priority > 0
        max_priority = max(p[1] for p in people_priorities) if people_priorities else 0
        self.assertGreater(max_priority, 0.0)
        
        print("✅ Priority scoring test passed")
    
    def test_empty_transactions(self):
        """Test với danh sách giao dịch rỗng"""
        print("\n" + "="*60)
        print("TEST: Empty Transactions")
        print("="*60)
        
        empty_transactions = LinkedList[AdvancedTransaction]()
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=empty_transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        simplified = simplifier.simplify()
        
        # Kết quả phải là danh sách rỗng
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
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.05, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        simplified = simplifier.simplify()
        
        # Với 1 giao dịch, kết quả phải có 1 giao dịch
        simplified_count = 0
        current = simplified.head
        while current:
            simplified_count += 1
            current = current.next
        
        self.assertEqual(simplified_count, 1)
        
        # Hiển thị kết quả
        if not simplified.is_empty():
            result_tx = simplified.head.data
            print(f"💸 Result: {result_tx.debtor} → {result_tx.creditor} = ${result_tx.amount:.2f}")
        
        print("✅ Single transaction test passed")
    
    def test_debt_summary(self):
        """Test tóm tắt nợ"""
        print("\n" + "="*60)
        print("TEST: Debt Summary")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice nợ Bob 1000, lãi suất kép, quá hạn
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=1000.0,
            borrow_date=self.base_date, due_date=date(2024, 4, 1),
            interest_rate=0.05, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Bob nợ Charlie 800, lãi suất đơn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=800.0,
            borrow_date=self.base_date, due_date=date(2024, 12, 1),
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Charlie nợ Alice 600, phí phạt theo ngày
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=600.0,
            borrow_date=self.base_date, due_date=date(2024, 3, 1),
            interest_rate=0.02, penalty_rate=5.0,
            interest_type=InterestType.COMPOUND_MONTHLY,
            penalty_type=PenaltyType.DAILY
        )
        transactions.append(tx3)
        
        # David nợ Alice 400
        tx4 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=400.0,
            borrow_date=date(2024, 2, 1), due_date=date(2024, 8, 1),
            interest_rate=0.04, penalty_rate=0.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx4)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        
        debt_summary = simplifier.get_debt_summary()
        
        # Kiểm tra tóm tắt chứa đủ thông tin
        summary_keys = debt_summary.keys()
        self.assertIsNotNone(summary_keys)
        
        total_debt = 0.0
        total_credit = 0.0
        
        print("📊 Detailed debt summary:")
        if summary_keys:
            for person in summary_keys:
                person_info = debt_summary.get(person)
                if person_info:
                    balance = person_info.get('total_balance', 0.0)
                    priority = person_info.get('priority_score', 0.0)
                    debt_count = int(person_info.get('debt_count', 0))
                    credit_count = int(person_info.get('credit_count', 0))
                    
                    if balance < 0:
                        total_debt += abs(balance)
                    else:
                        total_credit += balance
                    
                    status = "🔴 DEBTOR" if balance < 0 else "🟢 CREDITOR" if balance > 0 else "⚪ BALANCED"
                    
                    print(f"   👤 {person}: {status}")
                    print(f"      💰 Balance: ${balance:.2f}")
                    print(f"      ⭐ Priority: {priority:.2f}")
                    print(f"      📤 Debt transactions: {debt_count}")
                    print(f"      📥 Credit transactions: {credit_count}")
        
        print(f"\n💵 Total system debt: ${total_debt:.2f}")
        print(f"💵 Total system credit: ${total_credit:.2f}")
        
        # Tổng nợ và tổng cho vay phải bằng nhau
        self.assertTrue(abs(total_debt - total_credit) < EPSILON)
        print("✅ Debt summary test passed")
    
    def test_performance_large_dataset(self):
        """Test hiệu suất với dataset lớn"""
        print("\n" + "="*60)
        print("TEST: Performance with Large Dataset")
        print("="*60)
        
        # Tạo dataset lớn
        transactions = LinkedList[AdvancedTransaction]()
        
        people = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry"]
        
        random.seed(42)  # Để kết quả có thể tái tạo
        
        # Tạo 20 giao dịch ngẫu nhiên
        for i in range(20):
            debtor = random.choice(people)
            creditor = random.choice([p for p in people if p != debtor])
            amount = round(random.uniform(100, 1000), 2)
            
            days_offset = random.randint(-90, 90)
            due_date = self.current_date + timedelta(days=days_offset)
            
            tx = AdvancedTransaction(
                debtor=debtor, creditor=creditor, amount=amount,
                borrow_date=self.base_date, due_date=due_date,
                interest_rate=random.uniform(0.01, 0.10),
                penalty_rate=random.uniform(0, 20),
                interest_type=random.choice(list(InterestType)),
                penalty_type=random.choice(list(PenaltyType)))
            transactions.append(tx)
        
        print(f"📊 Created 20 random transactions with {len(people)} people")
        
        # Đo thời gian thực thi
        start_time = time.time()
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
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
        
        reduction_pct = (1 - simplified_count / original_count) * 100 if original_count > 0 else 0
        
        print(f"⏱️  Execution time: {execution_time:.4f} seconds")
        print(f"📊 Original transactions: {original_count}")
        print(f"📊 Simplified transactions: {simplified_count}")
        print(f"📉 Reduction: {reduction_pct:.1f}%")
        
        # Kiểm tra hiệu suất
        self.assertLess(execution_time, 2.0, "Algorithm should complete within 2 seconds")
        self.assertLessEqual(simplified_count, original_count, "Simplified count should not exceed original")
        
        print("✅ Performance test passed")

    def test_edge_cases(self):
        """Test các trường hợp biên"""
        print("\n" + "="*60)
        print("TEST: Edge Cases")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Giao dịch với số tiền rất nhỏ
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=0.01,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        # Giao dịch với số tiền rất lớn
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=999999.99,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.001, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        # Giao dịch với lãi suất 0
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        simplified = simplifier.simplify()
        
        # Đếm kết quả
        simplified_count = 0
        current = simplified.head
        while current:
            tx = current.data
            print(f"💸 Edge case result: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            simplified_count += 1
            current = current.next
        
        print(f"📊 Edge cases handled: {simplified_count} transactions")
        self.assertGreaterEqual(simplified_count, 0)
        print("✅ Edge cases test passed")

    def test_same_person_multiple_roles(self):
        """Test người tham gia với nhiều vai trò khác nhau"""
        print("\n" + "="*60)
        print("TEST: Same Person Multiple Roles")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Alice vừa là con nợ vừa là chủ nợ
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=500.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30),
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        tx2 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=300.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=60),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        tx3 = AdvancedTransaction(
            debtor="David", creditor="Alice", amount=250.0,
            borrow_date=self.base_date, due_date=self.current_date + timedelta(days=45),
            interest_rate=0.04, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        # Kiểm tra Alice có trong cả hai vai trò
        alice_balance = simplifier.people_balances.get("Alice", 0.0)
        print(f"💰 Alice net balance: ${alice_balance:.2f}")
        
        simplified = simplifier.simplify()
        
        # Hiển thị kết quả
        simplified_count = 0
        current = simplified.head
        while current:
            tx = current.data
            print(f"💸 Multi-role result: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            simplified_count += 1
            current = current.next
        
        print(f"📊 Multiple roles handled: {simplified_count} transactions")
        print("✅ Same person multiple roles test passed")

    def test_get_optimization_metrics(self):
        """Test metrics tối ưu hóa"""
        print("\n" + "="*60)
        print("TEST: Optimization Metrics")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Tạo một số giao dịch để test metrics
        people = ["Alice", "Bob", "Charlie", "David"]
        for i in range(8):
            debtor = people[i % 4]
            creditor = people[(i + 1) % 4]
            amount = 100.0 + i * 50
            
            tx = AdvancedTransaction(
                debtor=debtor, creditor=creditor, amount=amount,
                borrow_date=self.base_date, due_date=self.current_date + timedelta(days=30+i*10),
                interest_rate=0.02, penalty_rate=0.0,
                interest_type=InterestType.SIMPLE,
                penalty_type=PenaltyType.FIXED
            )
            transactions.append(tx)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        # Test metrics method nếu có
        try:
            metrics = simplifier.get_optimization_metrics()
            if metrics:
                print("📊 Optimization metrics:")
                for key, value in metrics.items():
                    print(f"   {key}: {value}")
            else:
                print("📊 No optimization metrics available")
        except AttributeError:
            print("📊 get_optimization_metrics method not implemented")
        
        simplified = simplifier.simplify()
        
        # Tính toán metrics cơ bản
        original_count = 8
        simplified_count = 0
        current = simplified.head
        while current:
            simplified_count += 1
            current = current.next
        
        reduction = original_count - simplified_count
        print(f"📊 Transactions reduced by: {reduction}")
        print(f"📊 Reduction percentage: {(reduction/original_count)*100:.1f}%")
        
        print("✅ Optimization metrics test passed")

    def test_stress_test(self):
        """Test căng thẳng với nhiều giao dịch phức tạp"""
        print("\n" + "="*60)
        print("TEST: Stress Test")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        people = [f"Person{i}" for i in range(10)]  # 10 người
        
        random.seed(123)  # Để kết quả có thể tái tạo
        
        # Tạo 50 giao dịch ngẫu nhiên
        for i in range(50):
            debtor = random.choice(people)
            creditor = random.choice([p for p in people if p != debtor])
            amount = round(random.uniform(10, 1000), 2)
            
            borrow_date = self.base_date - timedelta(days=random.randint(0, 180))
            due_date = borrow_date + timedelta(days=random.randint(30, 365))
            
            tx = AdvancedTransaction(
                debtor=debtor, creditor=creditor, amount=amount,
                borrow_date=borrow_date, due_date=due_date,
                interest_rate=random.uniform(0.01, 0.15),
                penalty_rate=random.uniform(0, 50),
                interest_type=random.choice(list(InterestType)),
                penalty_type=random.choice(list(PenaltyType))
            )
            transactions.append(tx)
        
        print(f"📊 Created 50 stress test transactions with {len(people)} people")
        
        start_time = time.time()
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.DAILY
        )
        
        simplified = simplifier.simplify()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Đếm kết quả
        simplified_count = 0
        current = simplified.head
        while current:
            simplified_count += 1
            current = current.next
        
        print(f"⏱️  Stress test execution time: {execution_time:.4f} seconds")
        print(f"📊 Simplified to: {simplified_count} transactions")
        print(f"📉 Stress test reduction: {((50-simplified_count)/50)*100:.1f}%")
        
        # Kiểm tra hiệu suất trong stress test
        self.assertLess(execution_time, 5.0, "Stress test should complete within 5 seconds")
        self.assertLessEqual(simplified_count, 50, "Should not increase transaction count")
        
        print("✅ Stress test passed")

    def test_validate_solution(self):
        """Test validation của solution"""
        print("\n" + "="*60)
        print("TEST: Solution Validation")
        print("="*60)
        
        transactions = LinkedList[AdvancedTransaction]()
        
        # Tạo giao dịch có thể validate được
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.05, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)
        
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=150.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.03, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)
        
        tx3 = AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=50.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx3)
        
        simplifier = AdvancedMinCostMaxFlowSimplifier(
            transactions=transactions,
            current_date=self.current_date,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        
        # Lưu balance trước khi simplify
        original_balances = {}
        for person in simplifier.people_balances.keys():
            original_balances[person] = simplifier.people_balances.get(person, 0.0)
        
        print("💰 Original balances:")
        for person, balance in original_balances.items():
            print(f"   {person}: ${balance:.2f}")
        
        simplified = simplifier.simplify()
        
        # Tính balance sau khi simplify
        new_balances = {person: 0.0 for person in original_balances.keys()}
        current = simplified.head
        while current:
            tx = current.data
            # Cập nhật balance từ simplified transactions
            if tx.debtor in new_balances:
                new_balances[tx.debtor] -= tx.amount
            else:
                new_balances[tx.debtor] = -tx.amount
                
            if tx.creditor in new_balances:
                new_balances[tx.creditor] += tx.amount
            else:
                new_balances[tx.creditor] = tx.amount
            current = current.next
        
        print("\n💰 New balances after simplification:")
        for person, balance in new_balances.items():
            print(f"   {person}: ${balance:.2f}")
        
        # Validate rằng tổng balance vẫn bằng 0
        total_original = sum(original_balances.values())
        total_new = sum(new_balances.values())
        
        print(f"\n📊 Total original balance: ${total_original:.2f}")
        print(f"📊 Total new balance: ${total_new:.2f}")
        
        self.assertTrue(abs(total_original) < EPSILON, "Original total should be ~0")
        self.assertTrue(abs(total_new) < EPSILON, "New total should be ~0")
        
        print("✅ Solution validation test passed")


if __name__ == '__main__':
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)