from __future__ import annotations
from datetime import date
from typing import Any
from src.data_structures import LinkedList, HashTable, Array
from src.core_type import AdvancedTransaction, BasicTransaction
from src.algorithms.basic_transactions.cycle_detector import DebtCycleSimplifier
from src.utils.financial_calculator import FinancialCalculator, InterestType,PenaltyType
from src.utils.money_utils import round_money
from src.utils.constants import EPSILON

class AdvancedDebtCycleSimplifier:
    """
    Đơn giản hóa chu trình nợ nâng cao với tính toán tài chính:
    - Xử lý AdvancedTransaction với lãi suất, phí phạt và ngày tháng
    - Tính toán số dư thực tế của từng giao dịch
    - Chuyển đổi sang BasicTransaction để áp dụng thuật toán DebtCycleSimplifier
    - Chuyển đổi ngược về AdvancedTransaction và tạo báo cáo chi tiết
    """

    def __init__(self,
                 advanced_transactions: LinkedList[AdvancedTransaction],
                 current_date: date):
        self.advanced_transactions = advanced_transactions
        self.current_date = current_date
        self.financial_metrics: HashTable[str, float] = HashTable()
        self.detailed_report: str = ""
        self._calculator = FinancialCalculator()

    def simplify_advanced(self) -> LinkedList[AdvancedTransaction]:
        if len(self.advanced_transactions) == 0:
            return LinkedList[AdvancedTransaction]()

        self.financial_metrics = self._calculate_financial_metrics()

        conversion_data = self._convert_to_basic_transactions_with_priority()
        basic_transactions = conversion_data["transactions"]

        if len(basic_transactions) == 0:
            return LinkedList[AdvancedTransaction]()

        simplified_basic = DebtCycleSimplifier(basic_transactions).simplify()

        simplified_advanced = self._convert_back_to_advanced_transactions(
            simplified_basic,
            conversion_data["person_to_advanced_map"]
        )

        return simplified_advanced

    def _calculate_financial_metrics(self) -> HashTable[str, float]:
        metrics: HashTable[str, float] = HashTable()
        total_original, total_current, total_interest, total_penalty = 0.0, 0.0, 0.0, 0.0
        overdue_count = high_priority_count = 0

        node = self.advanced_transactions.head
        while node:
            tx: AdvancedTransaction = node.data
            breakdown = self._calculator.calculate_total_debt(
                amount=tx.amount,
                interest_rate=tx.interest_rate,
                penalty_rate=tx.penalty_rate,
                borrow_date=tx.borrow_date,
                due_date=tx.due_date,
                current_date=self.current_date,
                interest_type=tx.interest_type,
                penalty_type=tx.penalty_type
            )
            priority = self._calculator.calculate_priority_score(
                principal=tx.amount,
                interest_rate=tx.interest_rate,
                penalty_rate=tx.penalty_rate,
                borrow_date=tx.borrow_date,
                due_date=tx.due_date,
                current_date=self.current_date,
                interest_type=tx.interest_type,
                penalty_type=tx.penalty_type
            )

            total_original += tx.amount
            total_current += breakdown["total"]
            total_interest += breakdown["interest"]
            total_penalty += breakdown["penalty"]

            if self.current_date > tx.due_date:
                overdue_count += 1
            if priority > 50.0:
                high_priority_count += 1

            node = node.next

        count = len(self.advanced_transactions)
        metrics["original_debt_total"] = total_original
        metrics["current_debt_total"] = total_current
        metrics["interest_total"] = total_interest
        metrics["penalty_total"] = total_penalty
        metrics["overdue_count"] = float(overdue_count)
        metrics["high_priority_count"] = float(high_priority_count)
        metrics["average_debt"] = total_current / max(1, count)

        return metrics

    def _convert_to_basic_transactions_with_priority(self) -> HashTable[str, any]:
        basic_transactions: LinkedList[BasicTransaction] = LinkedList()
        person_to_advanced_map: HashTable[str, Array[AdvancedTransaction]] = HashTable()
        priority_scores: HashTable[str, float] = HashTable()

        node = self.advanced_transactions.head
        while node:
            tx: AdvancedTransaction = node.data

            breakdown = self._calculator.calculate_total_debt(
                amount=tx.amount,
                interest_rate=tx.interest_rate,
                penalty_rate=tx.penalty_rate,
                borrow_date=tx.borrow_date,
                due_date=tx.due_date,
                current_date=self.current_date,
                interest_type=tx.interest_type,
                penalty_type=tx.penalty_type
            )
            priority = self._calculator.calculate_priority_score(
                principal=tx.amount,
                interest_rate=tx.interest_rate,
                penalty_rate=tx.penalty_rate,
                borrow_date=tx.borrow_date,
                due_date=tx.due_date,
                current_date=self.current_date,
                interest_type=tx.interest_type,
                penalty_type=tx.penalty_type
            )

            basic_tx = BasicTransaction(
                debtor=tx.debtor,
                creditor=tx.creditor,
                amount=breakdown["total"]
            )
            basic_transactions.append(basic_tx)

            key = f"{tx.debtor}->{tx.creditor}"
            if not person_to_advanced_map.contains_key(key):
                person_to_advanced_map.put(key, Array[AdvancedTransaction]())
            array_of_tx = person_to_advanced_map.get(key)
            if array_of_tx is not None: # Kiểm tra an toàn
                array_of_tx.append(value=tx)
            priority_scores[key] = priority

            node = node.next

        return {
            "transactions": basic_transactions,
            "person_to_advanced_map": person_to_advanced_map,
            "priority_scores": priority_scores,
            "financial_metrics": self.financial_metrics
        }

    def _convert_back_to_advanced_transactions(
        self,
        basic_transactions: LinkedList[BasicTransaction],
        person_map: HashTable[str, Array[AdvancedTransaction]] # person_map chứa các AdvancedTransaction GỐC
    ) -> LinkedList[AdvancedTransaction]:
        result: LinkedList[AdvancedTransaction] = LinkedList()

        node = basic_transactions.head
        while node:
            basic_tx: BasicTransaction = node.data
            key = f"{basic_tx.debtor}->{basic_tx.creditor}"
            
            original_advanced_tx_list_for_pair = person_map.get(key)

            final_borrow_date = self.current_date
            final_due_date = self.current_date
            final_interest_type = InterestType.SIMPLE # Ví dụ
            final_penalty_type = PenaltyType.FIXED   # Ví dụ

            if original_advanced_tx_list_for_pair is not None and len(original_advanced_tx_list_for_pair):
                template: AdvancedTransaction = original_advanced_tx_list_for_pair.get(0)
                final_interest_type = template.interest_type
                final_penalty_type = template.penalty_type

            final_amount_for_advanced = round_money(basic_tx.amount)

            if final_amount_for_advanced > EPSILON: # Chỉ tạo nếu số tiền có ý nghĩa
                new_advanced = AdvancedTransaction(
                    debtor=basic_tx.debtor,
                    creditor=basic_tx.creditor,
                    amount=final_amount_for_advanced,
                    borrow_date=final_borrow_date, # Luôn là current_date cho giao dịch đã chốt sổ
                    due_date=final_due_date,       # Luôn là current_date
                    interest_rate=0.0,             # Không có lãi/phạt cho giao dịch đã chốt sổ
                    penalty_rate=0.0,
                    interest_type=final_interest_type, # Loại đã xác định (từ template hoặc mặc định)
                    penalty_type=final_penalty_type    # Loại đã xác định
                )
                result.append(new_advanced)
            node = node.next
        return result