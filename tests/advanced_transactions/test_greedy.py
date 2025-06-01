from __future__ import annotations
from datetime import date, timedelta
import unittest

from src.data_structures import LinkedList
from src.core_type import AdvancedTransaction
from src.algorithms.advanced_transactions.greedy import AdvancedGreedySimplifier
from src.utils.financial_calculator import InterestType, PenaltyType, FinancialCalculator
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

class TestAdvancedGreedySimplifier(unittest.TestCase):
    """Bộ kiểm thử cho AdvancedGreedySimplifier"""
    def setUp(self):
        """Thiết lập dữ liệu test cơ bản"""
        self.base_date = date(2024, 1, 1)
        self.current_date = date(2024, 6, 1)  # 5 tháng sau

    def test_initialization(self):
        """Test khởi tạo AdvancedGreedySimplifier"""
        print("\n" + "="*60)
        print("TEST: Khởi tạo")
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
            current_date=self.current_date
        )

        self.assertIsNotNone(simplifier)
        self.assertEqual(simplifier.current_date, self.current_date)
        print("✅ Test khởi tạo thành công")

    def test_empty_transactions(self):
        """Test với danh sách giao dịch rỗng"""
        print("\n" + "="*60)
        print("TEST: Danh sách giao dịch rỗng")
        print("="*60)

        transactions = LinkedList[AdvancedTransaction]()
        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            current_date=self.current_date
        )

        simplified = simplifier.simplify()
        self.assertTrue(simplified.is_empty())

        print("📊 Xử lý giao dịch rỗng đúng")
        print("✅ Test danh sách giao dịch rỗng thành công")

    def test_single_transaction(self):
        """Test với một giao dịch duy nhất"""
        print("\n" + "="*60)
        print("TEST: Giao dịch đơn lẻ")
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
            current_date=self.current_date
        )

        simplified = simplifier.simplify()
        self.assertFalse(simplified.is_empty())

        result_tx = simplified.head.data
        print(f"💸 Kết quả: {result_tx.debtor} → {result_tx.creditor} = ${result_tx.amount:.2f}")
        print("✅ Test giao dịch đơn lẻ thành công")

    def test_simple_debt_simplification(self):
        """Test đơn giản hóa nợ đơn giản"""
        print("\n" + "="*60)
        print("TEST: Đơn giản hóa nợ đơn giản")
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
            current_date=self.current_date
        )

        original_count = 2
        simplified = simplifier.simplify()

        # Đếm số giao dịch kết quả
        simplified_count = 0
        current = simplified.head
        transaction_num = 1

        while current:
            tx = current.data
            print(f"💸 Giao dịch {transaction_num}: {tx.debtor} → {tx.creditor} = ${tx.amount:.2f}")
            simplified_count += 1
            transaction_num += 1
            current = current.next

        print(f"📊 Giao dịch ban đầu: {original_count}")
        print(f"📊 Giao dịch sau đơn giản hóa: {simplified_count}")
        print("✅ Test đơn giản hóa nợ đơn giản thành công")

    def test_financial_calculations(self):
        """Test tính toán tài chính nâng cao"""
        print("\n" + "="*60)
        print("TEST: Tính toán tài chính")
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

        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            current_date=self.current_date
        )

        # Tính số dư dự kiến và điểm ưu tiên bằng FinancialCalculator
        breakdown = FinancialCalculator.calculate_total_debt(
            50.0, 0.10, 20.0,
            self.base_date, date(2024, 3, 1), self.current_date,
            InterestType.COMPOUND_DAILY, PenaltyType.FIXED
        )
        expected_debt = breakdown['total']
        expected_priority = FinancialCalculator.calculate_priority_score(
            50.0, 0.10, 20.0,
            self.base_date, date(2024, 3, 1), self.current_date,
            InterestType.COMPOUND_DAILY, PenaltyType.FIXED
        )

        # Kiểm tra số dư
        alice_balance = simplifier.people_balances.get("Alice", 0.0)
        bob_balance = simplifier.people_balances.get("Bob", 0.0)
        self.assertAlmostEqual(alice_balance, -round_money(expected_debt), delta=EPSILON)
        self.assertAlmostEqual(bob_balance, round_money(expected_debt), delta=EPSILON)
        print(f"💰 Số dư Alice: ${alice_balance:.2f}, Dự kiến: ${-expected_debt:.2f}")
        print(f"💰 Số dư Bob: ${bob_balance:.2f}, Dự kiến: ${expected_debt:.2f}")

        # Kiểm tra điểm ưu tiên
        current = simplifier.transaction_details.head
        while current:
            detail = current.data
            if detail[0] == "Alice" and detail[1] == "Bob":
                actual_priority = detail[6]
                break
            current = current.next
        else:
            self.fail("Không tìm thấy điểm ưu tiên cho Alice->Bob")

        self.assertAlmostEqual(actual_priority, expected_priority, delta=EPSILON)
        print(f"⭐ Điểm ưu tiên: {actual_priority:.2f}, Dự kiến: {expected_priority:.2f}")
        print("✅ Test tính toán tài chính thành công")

    def test_debt_summary(self):
        """Test tóm tắt nợ"""
        print("\n" + "="*60)
        print("TEST: Tóm tắt nợ")
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
            current_date=self.current_date
        )

        print("📊 Tóm tắt chi tiết nợ:")

        total_debt = 0.0
        total_credit = 0.0

        # Thu thập thông tin từng người
        people_info = {}
        for person in simplifier.people_balances.keys():
            balance = simplifier.people_balances.get(person, 0.0)

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

            status = "🔴 CON NỢ" if balance < 0 else "🟢 NGƯỜI CHO NỢ"
            print(f"   👤 {person}: {status}")
            print(f"      💰 Số dư: ${balance:.2f}")
            print(f"      ⭐ Điểm ưu tiên: {priority:.2f}")
            print(f"      📤 Giao dịch nợ: {debt_count}")
            print(f"      📥 Giao dịch cho nợ: {credit_count}")

        print(f"\n💵 Tổng nợ hệ thống: ${total_debt:.2f}")
        print(f"💵 Tổng cho nợ hệ thống: ${total_credit:.2f}")
        print("✅ Test tóm tắt nợ thành công")

    def test_priority_scoring(self):
        """Test tính điểm ưu tiên"""
        print("\n" + "="*60)
        print("TEST: Tính điểm ưu tiên")
        print("="*60)

        transactions = LinkedList[AdvancedTransaction]()

        # Giao dịch quá hạn lâu - điểm ưu tiên cao
        tx1 = AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=50.0,
            borrow_date=self.base_date, due_date=date(2024, 2, 1),
            interest_rate=0.10, penalty_rate=50.0,
            interest_type=InterestType.COMPOUND_DAILY,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx1)

        # Giao dịch còn hạn - điểm ưu tiên thấp
        tx2 = AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=200.0,
            borrow_date=self.base_date, due_date=date(2024, 7, 1),
            interest_rate=0.02, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        )
        transactions.append(tx2)

        simplifier = AdvancedGreedySimplifier(
            transactions=transactions,
            current_date=self.current_date
        )

        # Kiểm tra điểm ưu tiên
        priorities = {}
        current = simplifier.transaction_details.head
        while current:
            detail = current.data
            key = (detail[0], detail[1])
            priorities[key] = detail[6]
            current = current.next

        self.assertTrue(priorities[("Alice", "Bob")] > priorities[("Bob", "Charlie")])
        print(f"⭐ Điểm ưu tiên Alice→Bob: {priorities[('Alice', 'Bob')]:.2f}")
        print(f"⭐ Điểm ưu tiên Bob→Charlie: {priorities[('Bob', 'Charlie')]:.2f}")
        print("✅ Test tính điểm ưu tiên thành công")

    def test_multi_party_transactions(self):
        """Test với nhiều người tham gia, kiểm tra cân bằng tổng thể"""
        print("\n" + "="*60)
        print("TEST: Giao dịch nhiều chiều")
        print("="*60)

        transactions = LinkedList[AdvancedTransaction]()

        # Alice nợ Bob 100
        transactions.append(AdvancedTransaction(
            debtor="Alice", creditor="Bob", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        ))

        # Bob nợ Charlie 100
        transactions.append(AdvancedTransaction(
            debtor="Bob", creditor="Charlie", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        ))

        # Charlie nợ Alice 100
        transactions.append(AdvancedTransaction(
            debtor="Charlie", creditor="Alice", amount=100.0,
            borrow_date=self.base_date, due_date=self.current_date,
            interest_rate=0.0, penalty_rate=0.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.FIXED
        ))

        simplifier = AdvancedGreedySimplifier(transactions, self.current_date)
        simplified = simplifier.simplify()

        print("📊 Tổng số giao dịch sau đơn giản hóa:", len(simplified))
        self.assertTrue(simplified.is_empty() or len(simplified) <= 1)
        print("✅ Test giao dịch nhiều chiều thành công")

    def test_percentage_penalty_handling(self):
        """Test xử lý mức phạt theo phần trăm"""
        print("\n" + "="*60)
        print("TEST: Phạt theo phần trăm")
        print("="*60)

        transactions = LinkedList[AdvancedTransaction]()
        tx = AdvancedTransaction(
            debtor="Minh", creditor="Tú", amount=200.0,
            borrow_date=self.base_date, due_date=date(2024, 2, 1),
            interest_rate=0.05, penalty_rate=10.0,
            interest_type=InterestType.SIMPLE,
            penalty_type=PenaltyType.PERCENTAGE
        )
        transactions.append(tx)

        simplifier = AdvancedGreedySimplifier(transactions, self.current_date)

        breakdown = FinancialCalculator.calculate_total_debt(
            200.0, 0.05, 10.0,
            self.base_date, date(2024, 2, 1), self.current_date,
            InterestType.SIMPLE, PenaltyType.PERCENTAGE
        )

        expected_total = breakdown['total']
        actual_balance = simplifier.people_balances.get("Minh", 0.0)

        print(f"💰 Tổng nợ thực tế: ${-actual_balance:.2f}")
        print(f"📈 Tổng nợ dự kiến: ${expected_total:.2f}")
        self.assertAlmostEqual(-actual_balance, round_money(expected_total), delta=EPSILON)
        print("✅ Test phạt theo phần trăm thành công")

if __name__ == '__main__':
    # Chạy tất cả test cases với output verbose
    unittest.main(verbosity=2)
