# Thuật toán Đơn giản hóa Nợ Nâng cao với Tính toán Tài chính
# Advanced Debt Cycle Simplification Algorithm with Financial Calculations
from __future__ import annotations

from datetime import date
from src.core_types import AdvancedTransaction, BasicTransaction
from src.data_structures import LinkedList, Graph, HashTable, Array, Tuple
from src.utils.sorting import merge_sort_array
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money
from src.utils.financial_calculator import FinancialCalculator, InterestType, PenaltyType

class AdvancedDebtCycleSimplifier:
    """
    Thuật toán đơn giản hóa nợ nâng cao với khả năng xử lý:
    - Giao dịch có lãi suất (đơn, kép theo các chu kỳ)
    - Phí phạt cho giao dịch quá hạn
    - Ưu tiên xử lý dựa trên điểm priority score
    - Tối ưu hóa theo thời gian thực và chi phí tài chính
    
    Thuật toán hoạt động theo 3 giai đoạn:
    1. Phase 1: Chuẩn bị và tính toán tài chính
       - Tính tổng nợ thực tế cho mỗi giao dịch (gốc + lãi + phí phạt)
       - Tính điểm ưu tiên cho việc sắp xếp xử lý
       - Chuyển đổi sang BasicTransaction để áp dụng thuật toán cycle
    
    2. Phase 2: Loại bỏ chu trình có trọng số
       - Xây dựng đồ thị với trọng số là tổng nợ thực tế
       - Tìm và loại bỏ chu trình theo thứ tự ưu tiên tài chính
       - Áp dụng cycle elimination với consideration cho chi phí thời gian
    
    3. Phase 3: Net Settlement thông minh
       - Net settlement với trọng số ưu tiên
       - Tối thiểu hóa chi phí tài chính tổng thể
       - Ưu tiên thanh toán các khoản nợ có chi phí cao
    
    Độ phức tạp: O((V+E) * C + T*log(T)) với T = số giao dịch, C = số chu trình
    """
    
    def __init__(self, 
                 advanced_transactions: LinkedList[AdvancedTransaction],
                 calculation_date: date = None):
        """
        Khởi tạo bộ đơn giản hóa nợ nâng cao.
        
        Args:
            advanced_transactions: Danh sách giao dịch nâng cao
            calculation_date: Ngày tính toán (mặc định là ngày hiện tại)
        """
        self.advanced_transactions = advanced_transactions
        self.calculation_date = calculation_date or date.today()
        self.simplified_transactions: LinkedList[AdvancedTransaction] = LinkedList()
        self.financial_summary: HashTable[str, float] = HashTable()
        
    def _calculate_financial_metrics(self) -> HashTable[str, Tuple]:
        """
        Tính toán các chỉ số tài chính cho tất cả giao dịch.
        
        Returns:
            HashTable mapping transaction_id -> (total_debt, priority_score, breakdown)
        """
        metrics = HashTable[str, Tuple]()
        
        for tx_node in self.advanced_transactions:
            tx = tx_node.data
            tx_id = f"{tx.debtor}->{tx.creditor}-{tx.amount}"
            
            # Tính tổng nợ thực tế
            total_debt = tx.calculate_total_debt(self.calculation_date)
            
            # Tính điểm ưu tiên
            priority_score = tx.get_priority_score(self.calculation_date)
            
            # Lấy breakdown chi tiết
            breakdown = tx.get_debt_breakdown(self.calculation_date)
            
            metrics.put(tx_id, Tuple([total_debt, priority_score, breakdown]))
            
        return metrics

    def _convert_to_basic_transactions_with_priority(self) -> Tuple:
        """
        Chuyển đổi AdvancedTransaction thành BasicTransaction với thông tin ưu tiên.
        
        Returns:
            Tuple: (basic_transactions_list, priority_mapping, original_mapping)
        """
        basic_transactions = LinkedList[BasicTransaction]()
        priority_mapping = HashTable[str, float]()
        original_mapping = HashTable[str, AdvancedTransaction]()
        
        # Tính toán metrics tài chính
        financial_metrics = self._calculate_financial_metrics()
        
        # Chuyển đổi từng giao dịch
        for tx_node in self.advanced_transactions:
            tx = tx_node.data
            tx_id = f"{tx.debtor}->{tx.creditor}-{tx.amount}"
            
            # Lấy tổng nợ thực tế làm số tiền cho BasicTransaction
            metrics = financial_metrics.get(tx_id)
            total_debt, priority_score, breakdown = metrics[0], metrics[1], metrics[2]
            
            if total_debt > EPSILON:
                # Tạo BasicTransaction với số tiền là tổng nợ thực tế
                basic_tx = BasicTransaction(
                    debtor=tx.debtor,
                    creditor=tx.creditor,
                    amount=total_debt
                )
                
                basic_transactions.append(basic_tx)
                
                # Lưu thông tin ưu tiên và mapping
                basic_tx_id = f"{basic_tx.debtor}->{basic_tx.creditor}-{basic_tx.amount}"
                priority_mapping.put(basic_tx_id, priority_score)
                original_mapping.put(basic_tx_id, tx)
        
        return Tuple([basic_transactions, priority_mapping, original_mapping])

    def _build_weighted_graph(self, 
                            tx_array: Array[BasicTransaction], 
                            priority_mapping: HashTable[str, float]) -> Graph[str, BasicTransaction]:
        """
        Xây dựng đồ thị có trọng số với consideration cho priority score.
        
        Đồ thị được xây dựng với:
        - Trọng số cạnh = total_debt * priority_weight
        - Ưu tiên các cạnh có điểm priority cao hơn
        """
        weighted_graph = Graph[str, BasicTransaction](is_directed=True)
        
        for tx in tx_array:
            if tx.amount > EPSILON:
                tx_id = f"{tx.debtor}->{tx.creditor}-{tx.amount}"
                priority_score = priority_mapping.get(tx_id, 1.0)
                
                # Tạo weighted transaction
                weighted_tx = BasicTransaction(
                    debtor=tx.debtor,
                    creditor=tx.creditor,
                    amount=tx.amount
                )
                
                # Thêm thông tin priority vào transaction (custom attribute)
                weighted_tx.priority_score = priority_score
                
                weighted_graph.add_vertex(tx.debtor)
                weighted_graph.add_vertex(tx.creditor)
                weighted_graph.add_edge(tx.debtor, tx.creditor, weighted_tx)
        
        return weighted_graph

    def _calculate_financial_cycle_score(self, cycle_edges: LinkedList) -> Tuple:
        """
        Tính điểm chu trình dựa trên lợi ích tài chính và số lượng giao dịch loại bỏ.
        
        Tiêu chí đánh giá:
        1. Số giao dịch được loại bỏ hoàn toàn
        2. Tổng tiết kiệm chi phí tài chính
        3. Điểm ưu tiên trung bình của chu trình
        """
        if cycle_edges.get_length() < 2:
            return Tuple([-1, 0.0, 0.0])
        
        min_amount = float('inf')
        total_priority = 0.0
        transaction_count = 0
        total_financial_saving = 0.0
        
        # Phân tích chu trình
        for edge_node in cycle_edges:
            tx = edge_node.data
            if tx is None or tx.amount <= EPSILON:
                return Tuple([-1, 0.0, 0.0])
            
            min_amount = min(min_amount, tx.amount)
            
            # Tính điểm ưu tiên nếu có
            priority = getattr(tx, 'priority_score', 1.0)
            total_priority += priority
            transaction_count += 1
            
            # Ước tính tiết kiệm chi phí tài chính
            financial_saving = min_amount * priority * 0.1  # 10% của giá trị có trọng số
            total_financial_saving += financial_saving
        
        if min_amount == float('inf') or min_amount <= EPSILON:
            return Tuple([-1, 0.0, 0.0])
        
        # Đếm số giao dịch sẽ bị loại bỏ
        transactions_eliminated = 0
        for edge_node in cycle_edges:
            tx = edge_node.data
            if abs(tx.amount - min_amount) < EPSILON:
                transactions_eliminated += 1
        
        # Tính điểm ưu tiên trung bình
        avg_priority = total_priority / max(transaction_count, 1)
        
        return Tuple([transactions_eliminated, total_financial_saving, avg_priority])

    def _find_financially_optimal_cycles(self, weighted_graph: Graph) -> LinkedList[Tuple]:
        """
        Tìm các chu trình tối ưu về mặt tài chính và sắp xếp theo độ ưu tiên.
        """
        found_cycles_edges = weighted_graph.find_cycles_with_edges()
        optimal_cycles = LinkedList[Tuple]()
        
        if found_cycles_edges.is_empty():
            return optimal_cycles
        
        # Đánh giá từng chu trình
        for cycle_edges_ll_node in found_cycles_edges:
            score_tuple = self._calculate_financial_cycle_score(cycle_edges_ll_node)
            transactions_eliminated, financial_saving, avg_priority = score_tuple[0], score_tuple[1], score_tuple[2]
            
            if transactions_eliminated > 0:
                # Tính min_amount cho chu trình
                min_amount = float('inf')
                for edge_node in cycle_edges_ll_node:
                    tx = edge_node.data
                    min_amount = min(min_amount, tx.amount)
                
                cycle_info = Tuple([score_tuple, cycle_edges_ll_node, min_amount])
                optimal_cycles.append(cycle_info)
        
        # Sắp xếp theo độ ưu tiên tài chính
        if not optimal_cycles.is_empty():
            optimal_cycles = self._sort_cycles_by_financial_priority(optimal_cycles)
        
        return optimal_cycles

    def _sort_cycles_by_financial_priority(self, cycles: LinkedList[Tuple]) -> LinkedList[Tuple]:
        """
        Sắp xếp chu trình theo độ ưu tiên tài chính.
        
        Tiêu chí sắp xếp:
        1. Số giao dịch loại bỏ (cao hơn = tốt hơn)
        2. Tiết kiệm chi phí tài chính (cao hơn = tốt hơn)
        3. Điểm ưu tiên trung bình (cao hơn = tốt hơn)
        """
        cycles_array = Array()
        for cycle_node in cycles:
            cycles_array.append(cycle_node)
        
        def financial_comparator(cycle1, cycle2):
            score1 = cycle1[0]
            score2 = cycle2[0]
            
            elim1, saving1, priority1 = score1[0], score1[1], score1[2]
            elim2, saving2, priority2 = score2[0], score2[1], score2[2]
            
            # Ưu tiên số giao dịch loại bỏ
            if elim1 != elim2:
                return elim1 > elim2
            
            # Ưu tiên tiết kiệm chi phí
            if abs(saving1 - saving2) > EPSILON:
                return saving1 > saving2
            
            # Ưu tiên điểm priority cao
            return priority1 > priority2
        
        sorted_array = merge_sort_array(cycles_array, comparator=financial_comparator)
        
        sorted_cycles = LinkedList[Tuple]()
        for cycle in sorted_array:
            sorted_cycles.append(cycle)
        
        return sorted_cycles

    def _priority_based_net_settlement(self, 
                                     tx_array: Array[BasicTransaction],
                                     priority_mapping: HashTable[str, float],
                                     original_mapping: HashTable[str, AdvancedTransaction]) -> LinkedList[AdvancedTransaction]:
        """
        Thực hiện net settlement với ưu tiên dựa trên điểm priority và chi phí tài chính.
        """
        # Tính net balances với trọng số ưu tiên
        net_balances = HashTable[str, float]()
        person_priorities = HashTable[str, float]()  # Điểm ưu tiên trung bình của mỗi người
        person_transaction_counts = HashTable[str, int]()
        
        for tx in tx_array:
            tx_id = f"{tx.debtor}->{tx.creditor}-{tx.amount}"
            priority = priority_mapping.get(tx_id, 1.0)
            
            # Cập nhật net balances
            current_debtor_balance = net_balances.get(tx.debtor, 0.0)
            current_creditor_balance = net_balances.get(tx.creditor, 0.0)
            
            net_balances.put(tx.debtor, current_debtor_balance - tx.amount)
            net_balances.put(tx.creditor, current_creditor_balance + tx.amount)
            
            # Cập nhật điểm ưu tiên trung bình
            for person in [tx.debtor, tx.creditor]:
                current_priority = person_priorities.get(person, 0.0)
                current_count = person_transaction_counts.get(person, 0)
                
                new_priority = (current_priority * current_count + priority) / (current_count + 1)
                person_priorities.put(person, new_priority)
                person_transaction_counts.put(person, current_count + 1)
        
        # Phân loại debtors và creditors với thông tin ưu tiên
        debtors_with_priority = Array[Tuple]()  # (person, abs_balance, priority)
        creditors_with_priority = Array[Tuple]()
        
        keys_ll = net_balances.keys()
        if keys_ll:
            current_key_node = keys_ll.head
            while current_key_node:
                person = current_key_node.data
                balance = net_balances.get(person)
                priority = person_priorities.get(person, 1.0)
                
                if balance < -EPSILON:  # Debtor
                    debtors_with_priority.append(Tuple([person, abs(balance), priority]))
                elif balance > EPSILON:  # Creditor
                    creditors_with_priority.append(Tuple([person, balance, priority]))
                    
                current_key_node = current_key_node.next
        
        # Sắp xếp theo độ ưu tiên tài chính
        def priority_comparator(item1, item2):
            _, balance1, priority1 = item1[0], item1[1], item1[2]
            _, balance2, priority2 = item2[0], item2[1], item2[2]
            
            # Ưu tiên điểm priority cao và số dư lớn
            score1 = balance1 * priority1
            score2 = balance2 * priority2
            return score1 > score2
        
        debtors_sorted = merge_sort_array(debtors_with_priority, priority_comparator)
        creditors_sorted = merge_sort_array(creditors_with_priority, priority_comparator)
        
        # Thực hiện matching với ưu tiên
        result = LinkedList[AdvancedTransaction]()
        
        for i in range(len(debtors_sorted)):
            debtor_info = debtors_sorted.get(i)
            debtor, debtor_amount, debtor_priority = debtor_info[0], debtor_info[1], debtor_info[2]
            
            for j in range(len(creditors_sorted)):
                if debtor_amount <= EPSILON:
                    break
                
                creditor_info = creditors_sorted.get(j)
                creditor, creditor_amount, creditor_priority = creditor_info[0], creditor_info[1], creditor_info[2]
                
                if creditor_amount <= EPSILON:
                    continue
                
                transfer_amount = min(debtor_amount, creditor_amount)
                if transfer_amount > EPSILON:
                    # Tạo AdvancedTransaction mới với thông tin tối ưu
                    # Sử dụng thông tin từ giao dịch gốc có priority cao nhất
                    avg_priority = (debtor_priority + creditor_priority) / 2
                    
                    # Tìm giao dịch gốc để lấy thông tin tài chính
                    original_tx = self._find_representative_transaction(
                        debtor, creditor, original_mapping, avg_priority
                    )
                    
                    if original_tx:
                        new_advanced_tx = AdvancedTransaction(
                            debtor=debtor,
                            creditor=creditor,
                            amount=round_money(transfer_amount),
                            borrow_date=original_tx.borrow_date,
                            due_date=original_tx.due_date,
                            interest_rate=original_tx.interest_rate,
                            penalty_rate=original_tx.penalty_rate,
                            interest_type=original_tx.interest_type,
                            penalty_type=original_tx.penalty_type
                        )
                    else:
                        # Fallback: tạo giao dịch đơn giản
                        new_advanced_tx = AdvancedTransaction(
                            debtor=debtor,
                            creditor=creditor,
                            amount=round_money(transfer_amount),
                            borrow_date=self.calculation_date,
                            due_date=self.calculation_date,
                            interest_rate=0.0,
                            penalty_rate=0.0
                        )
                    
                    result.append(new_advanced_tx)
                    
                    # Cập nhật số dư
                    debtor_amount -= transfer_amount
                    creditors_sorted.get(j)[1] -= transfer_amount  # Cập nhật creditor_amount
        
        return result

    def _find_representative_transaction(self, 
                                       debtor: str, 
                                       creditor: str,
                                       original_mapping: HashTable[str, AdvancedTransaction],
                                       target_priority: float) -> AdvancedTransaction:
        """
        Tìm giao dịch đại diện để lấy thông tin tài chính cho giao dịch mới.
        """
        best_match = None
        best_score = float('inf')
        
        # Duyệt qua tất cả giao dịch gốc
        keys_ll = original_mapping.keys()
        if keys_ll:
            current_key_node = keys_ll.head
            while current_key_node:
                key = current_key_node.data
                original_tx = original_mapping.get(key)
                
                if original_tx:
                    # Tính điểm phù hợp
                    tx_priority = original_tx.get_priority_score(self.calculation_date)
                    priority_diff = abs(tx_priority - target_priority)
                    
                    # Ưu tiên giao dịch liên quan đến debtor hoặc creditor
                    relevance_bonus = 0.0
                    if original_tx.debtor == debtor or original_tx.creditor == creditor:
                        relevance_bonus = -1000.0  # Bonus lớn cho sự liên quan
                    
                    score = priority_diff + relevance_bonus
                    
                    if score < best_score:
                        best_score = score
                        best_match = original_tx
                
                current_key_node = current_key_node.next
        
        return best_match

    def simplify_advanced(self) -> LinkedList[AdvancedTransaction]:
        """
        Thực hiện đơn giản hóa nợ nâng cao với tính toán tài chính đầy đủ.
        
        Returns:
            LinkedList[AdvancedTransaction]: Danh sách giao dịch đã được tối ưu hóa
        """
        if self.advanced_transactions.is_empty():
            return LinkedList[AdvancedTransaction]()

        # Phase 1: Chuẩn bị và chuyển đổi
        conversion_result = self._convert_to_basic_transactions_with_priority()
        basic_transactions, priority_mapping, original_mapping = conversion_result[0], conversion_result[1], conversion_result[2]
        
        if basic_transactions.is_empty():
            return LinkedList[AdvancedTransaction]()

        # Chuyển sang array để xử lý
        current_tx_array = Array[BasicTransaction]()
        for tx_node in basic_transactions:
            current_tx_array.append(tx_node)

        # Phase 2: Loại bỏ chu trình có trọng số tài chính
        iteration_count = 0
        max_iterations = min(len(current_tx_array) * 2, 50)

        while iteration_count < max_iterations and len(current_tx_array) > 1:
            iteration_count += 1
            
            # Xây dựng đồ thị có trọng số
            weighted_graph = self._build_weighted_graph(current_tx_array, priority_mapping)
            
            # Tìm chu trình tối ưu tài chính
            optimal_cycles = self._find_financially_optimal_cycles(weighted_graph)
            
            if optimal_cycles.is_empty():
                break
            
            # Áp dụng chu trình tốt nhất
            best_cycle_info = optimal_cycles.head.data
            _, cycle_edges, min_amount = best_cycle_info[0], best_cycle_info[1], best_cycle_info[2]
            
            # Loại bỏ chu trình
            for edge_node in cycle_edges:
                tx = edge_node.data
                tx.amount -= min_amount
            
            # Cập nhật danh sách
            updated_tx_array = Array[BasicTransaction]()
            for tx in current_tx_array:
                if tx.amount > EPSILON:
                    updated_tx_array.append(tx)
            
            current_tx_array = updated_tx_array

        # Phase 3: Net settlement thông minh
        self.simplified_transactions = self._priority_based_net_settlement(
            current_tx_array, priority_mapping, original_mapping
        )
        
        # Tính toán tóm tắt tài chính
        self._calculate_financial_summary()
        
        return self.simplified_transactions

    def _calculate_financial_summary(self):
        """Tính toán tóm tắt tài chính của quá trình đơn giản hóa."""
        # Tính tổng chi phí trước và sau
        total_original_debt = 0.0
        total_original_interest = 0.0
        total_original_penalty = 0.0
        
        for tx_node in self.advanced_transactions:
            tx = tx_node.data
            breakdown = tx.get_debt_breakdown(self.calculation_date)
            total_original_debt += breakdown['total']
            total_original_interest += breakdown['interest']
            total_original_penalty += breakdown['penalty']
        
        total_simplified_debt = 0.0
        for tx_node in self.simplified_transactions:
            tx = tx_node.data
            total_simplified_debt += tx.calculate_total_debt(self.calculation_date)
        
        # Lưu summary
        self.financial_summary.put('original_debt_total', round_money(total_original_debt))
        self.financial_summary.put('original_interest_total', round_money(total_original_interest))
        self.financial_summary.put('original_penalty_total', round_money(total_original_penalty))
        self.financial_summary.put('simplified_debt_total', round_money(total_simplified_debt))
        self.financial_summary.put('debt_reduction', round_money(total_original_debt - total_simplified_debt))
        self.financial_summary.put('transaction_count_before', self.advanced_transactions.get_length())
        self.financial_summary.put('transaction_count_after', self.simplified_transactions.get_length())
        self.financial_summary.put('transaction_reduction', 
                                 self.advanced_transactions.get_length() - self.simplified_transactions.get_length())

    def get_financial_summary(self) -> HashTable[str, float]:
        """Lấy tóm tắt tài chính của quá trình đơn giản hóa."""
        return self.financial_summary

    def get_detailed_report(self) -> str:
        """
        Tạo báo cáo chi tiết về quá trình đơn giản hóa.
        """
        if self.financial_summary.is_empty():
            return "Chưa thực hiện đơn giản hóa."
        
        report = "=== BÁO CÁO ĐƠN GIẢN HÓA NỢ NÂNG CAO ===\n\n"
        report += f"Ngày tính toán: {self.calculation_date}\n\n"
        
        report += "TRƯỚC KHI ĐƠN GIẢN HÓA:\n"
        report += f"- Tổng số giao dịch: {int(self.financial_summary.get('transaction_count_before', 0))}\n"
        report += f"- Tổng nợ gốc + lãi + phí: {self.financial_summary.get('original_debt_total', 0.0):,.2f}\n"
        report += f"- Tổng tiền lãi: {self.financial_summary.get('original_interest_total', 0.0):,.2f}\n"
        report += f"- Tổng phí phạt: {self.financial_summary.get('original_penalty_total', 0.0):,.2f}\n\n"
        
        report += "SAU KHI ĐƠN GIẢN HÓA:\n"
        report += f"- Tổng số giao dịch: {int(self.financial_summary.get('transaction_count_after', 0))}\n"
        report += f"- Tổng nợ còn lại: {self.financial_summary.get('simplified_debt_total', 0.0):,.2f}\n\n"
        
        report += "KẾT QUẢ:\n"
        report += f"- Giảm {int(self.financial_summary.get('transaction_reduction', 0))} giao dịch\n"
        report += f"- Tiết kiệm chi phí: {self.financial_summary.get('debt_reduction', 0.0):,.2f}\n"
        
        reduction_percent = 0.0
        original_total = self.financial_summary.get('original_debt_total', 0.0)
        if original_total > 0:
            reduction_percent = (self.financial_summary.get('debt_reduction', 0.0) / original_total) * 100
        
        report += f"- Tỷ lệ tiết kiệm: {reduction_percent:.2f}%\n"
        
        return report