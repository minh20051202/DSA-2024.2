# Thuật toán Tham lam Nâng cao cho Đơn giản hóa Nợ với Yếu tố Thời gian, Lãi suất, Phí phạt
# Advanced Greedy Algorithm for Debt Simplification with Time Factors
from __future__ import annotations
from datetime import date
from typing import Optional

from src.core_types import BasicTransaction, AdvancedTransaction
from src.data_structures import LinkedList, HashTable, Tuple
from src.utils.sorting import merge_sort_linked_list
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money
from src.utils.financial_calculator import InterestType, PenaltyType

class AdvancedGreedySimplifier:
    """
    Thực hiện đơn giản hóa nợ nâng cao với thuật toán tham lam tối ưu.
    Xử lý các yếu tố phức tạp như thời gian, lãi suất, phí phạt.
    
    Thuật toán hoạt động:
    1. Tính toán tổng nợ thực tế cho từng giao dịch (sử dụng FinancialCalculator)
    2. Tính số dư ròng cho mỗi người dựa trên tổng nợ thực tế
    3. Áp dụng thuật toán Greedy truyền thống trên số dư đã tính toán
    4. Tạo giao dịch thanh toán tối thiểu
    
    Độ phức tạp: O(n log k) với n = số giao dịch, k = số người
    """
    
    def __init__(self, 
                 transactions: LinkedList[AdvancedTransaction],
                 evaluation_date: Optional[date] = None):
        """
        Khởi tạo bộ đơn giản hóa nợ nâng cao.
        
        Args:
            transactions: Danh sách giao dịch nâng cao
            evaluation_date: Ngày đánh giá (mặc định là ngày hiện tại)
        """
        self.initial_transactions = transactions
        self.evaluation_date = evaluation_date or date.today()
        self.people_balances = HashTable[str, float]()
        self.transaction_details = LinkedList[Tuple]()
        self._calculate_advanced_balances()

    def _calculate_advanced_balances(self) -> None:
        """
        Tính toán số dư ròng cho mỗi người dựa trên tổng nợ thực tế.
        Sử dụng FinancialCalculator để xử lý các tính toán phức tạp.
        """
        current = self.initial_transactions.head
        
        while current:
            tx = current.data
            
            # Lấy breakdown chi tiết của nợ
            debt_breakdown = tx.get_debt_breakdown(self.evaluation_date)
            actual_debt = debt_breakdown['total']
            
            # Lưu chi tiết để phân tích sau này
            detail = Tuple([
                tx.debtor, 
                tx.creditor, 
                debt_breakdown['principal'],    # Số tiền gốc
                debt_breakdown['interest'],     # Tiền lãi
                debt_breakdown['penalty'],      # Phí phạt
                actual_debt,                    # Tổng nợ thực tế
                tx.get_priority_score(self.evaluation_date),  # Điểm ưu tiên
                tx.is_overdue(self.evaluation_date)  # Trạng thái quá hạn
            ])
            self.transaction_details.append(detail)
            
            # Cập nhật số dư dựa trên tổng nợ thực tế
            debtor_balance = self.people_balances.get(tx.debtor, 0.0)
            self.people_balances.put(tx.debtor, round_money(debtor_balance - actual_debt))
            
            creditor_balance = self.people_balances.get(tx.creditor, 0.0)
            self.people_balances.put(tx.creditor, round_money(creditor_balance + actual_debt))
            
            current = current.next

    def get_debt_analysis(self) -> HashTable[str, any]:
        """
        Phân tích chi tiết về tình hình nợ nần.
        
        Returns:
            HashTable chứa thông tin phân tích chi tiết
        """
        total_principal = 0.0
        total_interest = 0.0
        total_penalty = 0.0
        total_actual_debt = 0.0
        overdue_count = 0
        
        current = self.transaction_details.head
        while current:
            detail = current.data
            principal = detail[2]
            interest = detail[3]
            penalty = detail[4]
            actual_debt = detail[5]
            is_overdue = detail[7]
            
            total_principal += principal
            total_interest += interest
            total_penalty += penalty
            total_actual_debt += actual_debt
            
            if is_overdue:
                overdue_count += 1
                
            current = current.next
        
        # Tính số người có số dư âm và dương
        debtors_count = 0
        creditors_count = 0
        max_debtor_balance = 0.0
        max_creditor_balance = 0.0
        
        for person in self.people_balances.keys():
            balance = self.people_balances.get(person)
            if balance < -EPSILON:
                debtors_count += 1
                max_debtor_balance = min(max_debtor_balance, balance)
            elif balance > EPSILON:
                creditors_count += 1
                max_creditor_balance = max(max_creditor_balance, balance)
        
        return {
            'total_principal': round_money(total_principal),
            'total_interest': round_money(total_interest),
            'total_penalty': round_money(total_penalty),
            'total_actual_debt': round_money(total_actual_debt),
            'additional_costs': round_money(total_interest + total_penalty),
            'additional_costs_percentage': round(((total_interest + total_penalty) / total_principal * 100), 2) if total_principal > 0 else 0,
            'number_of_debtors': debtors_count,
            'number_of_creditors': creditors_count,
            'overdue_transactions': overdue_count,
            'max_individual_debt': abs(max_debtor_balance),
            'max_individual_credit': max_creditor_balance,
            'evaluation_date': self.evaluation_date.isoformat()
        }

    def simplify(self) -> LinkedList[BasicTransaction]:
        """
        Thực hiện đơn giản hóa nợ bằng thuật toán Greedy truyền thống.
        Áp dụng trên số dư đã được tính toán với các yếu tố tài chính.
        
        Returns:
            LinkedList[BasicTransaction]: Danh sách giao dịch đã được đơn giản hóa
        """
        # Điều kiện dừng
        if self.initial_transactions.is_empty():
            return LinkedList()

        # Phân loại người tham gia thành 2 nhóm dựa trên số dư thực tế
        debtors = LinkedList[Tuple]()    # (tên, số_dư_âm)
        creditors = LinkedList[Tuple]()  # (tên, số_dư_dương)
        
        for person in self.people_balances.keys():
            balance = self.people_balances.get(person)
            
            if balance < -EPSILON:
                debtors.append(Tuple([person, balance]))
            elif balance > EPSILON:
                creditors.append(Tuple([person, balance]))

        # Sắp xếp theo chiến lược Greedy
        debtors = merge_sort_linked_list(
            debtors, 
            comparator=lambda t1, t2: t1[1] < t2[1]  # Nợ nhiều nhất trước
        )
        
        creditors = merge_sort_linked_list(
            creditors, 
            comparator=lambda t1, t2: t1[1] > t2[1]  # Cho vay nhiều nhất trước
        )

        # Thực hiện thuật toán Greedy ghép đôi
        simplified_txs = LinkedList[BasicTransaction]()
        debtor_node = debtors.head
        creditor_node = creditors.head
        
        while debtor_node and creditor_node:
            debtor_name, debtor_balance = debtor_node.data
            creditor_name, creditor_balance = creditor_node.data
            
            # Tính số tiền thanh toán tối ưu
            settle_amount = min(-debtor_balance, creditor_balance)
            
            if settle_amount > EPSILON:
                # Tạo giao dịch thanh toán mới
                new_transaction = BasicTransaction(
                    debtor=debtor_name, 
                    creditor=creditor_name, 
                    amount=settle_amount
                )
                simplified_txs.append(new_transaction)
                
                # Cập nhật số dư
                debtor_balance += settle_amount
                creditor_balance -= settle_amount
                
                debtor_node.data = Tuple([debtor_name, debtor_balance])
                creditor_node.data = Tuple([creditor_name, creditor_balance])
            
            # Chuyển đến người tiếp theo nếu đã thanh toán xong
            if abs(debtor_balance) < EPSILON:
                debtor_node = debtor_node.next
                
            if creditor_balance < EPSILON:
                creditor_node = creditor_node.next
        
        return simplified_txs

    def get_detailed_settlement_plan(self) -> HashTable[str, any]:
        """
        Tạo kế hoạch thanh toán chi tiết bao gồm phân tích tài chính.
        
        Returns:
            HashTable chứa kế hoạch thanh toán và phân tích chi tiết
        """
        simplified_transactions = self.simplify()
        debt_analysis = self.get_debt_analysis()
        
        # Chuyển đổi LinkedList thành list để dễ xử lý
        settlement_list = []
        current = simplified_transactions.head
        while current:
            tx = current.data
            settlement_list.append({
                'debtor': tx.debtor,
                'creditor': tx.creditor,
                'amount': tx.amount
            })
            current = current.next
        
        return {
            'settlement_transactions': settlement_list,
            'financial_analysis': debt_analysis,
            'optimization_results': {
                'original_transaction_count': self._count_transactions(self.initial_transactions),
                'simplified_transaction_count': len(settlement_list),
                'reduction_percentage': round(
                    (1 - len(settlement_list) / max(1, self._count_transactions(self.initial_transactions))) * 100, 2
                )
            }
        }

    def _count_transactions(self, transaction_list: LinkedList) -> int:
        """Đếm số lượng giao dịch trong LinkedList."""
        count = 0
        current = transaction_list.head
        while current:
            count += 1
            current = current.next
        return count