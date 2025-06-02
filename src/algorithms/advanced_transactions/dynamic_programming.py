from __future__ import annotations
from datetime import date
from typing import Any 

from src.core_type import BasicTransaction, AdvancedTransaction
from src.data_structures import LinkedList, HashTable, PriorityQueue, Tuple, Array
from src.utils.sorting import merge_sort_linked_list
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money
from src.utils.financial_calculator import FinancialCalculator 

# Định nghĩa kiểu dữ liệu cho giá trị bảng DP với thông tin tài chính nâng cao
# AdvancedDPValueTuple: (tổng_chi_phí_tài_chính, tổng_số_giao_dịch, danh_sách_giao_dịch, điểm_ưu_tiên_tổng_đã_xử_lý)
AdvancedDPValueTuple = Tuple

# Khóa bảng DP: Tuple chứa số dư thực tế của mọi người theo thứ tự cố định
# Giá trị bảng DP: AdvancedDPValueTuple như định nghĩa ở trên
AdvancedDPTable = HashTable[Tuple, AdvancedDPValueTuple]


class AdvancedDynamicProgrammingSimplifier:
    """
    Thuật toán đơn giản hóa nợ nâng cao sử dụng Quy hoạch động với kỹ thuật ghi nhớ.

    Thuật toán này nhằm mục đích tìm ra giải pháp tối ưu để giải quyết một tập hợp các nghĩa vụ nợ
    phức tạp, có tính đến các yếu tố như lãi suất, phí phạt và ngày đáo hạn.
    Mục tiêu là tối thiểu hóa tổng số tiền thực tế được chuyển giao trong các giao dịch
    đơn giản hóa, và sau đó là tối thiểu hóa số lượng giao dịch.

    Phương pháp tiếp cận:
    1.  Tính toán số dư thực tế cho mỗi người từ các giao dịch nâng cao ban đầu,
        bao gồm cả lãi và phí phạt tính đến ngày đánh giá hiện tại.
    2.  Sử dụng một hàm đệ quy Quy hoạch động (DP) với kỹ thuật ghi nhớ (memoization) để
        khám phá các trạng thái thanh toán có thể.
    3.  Mỗi trạng thái DP được đại diện bởi một Tuple các số dư hiện tại của tất cả những người tham gia.
    4.  Tại mỗi trạng thái, thuật toán thử tất cả các cặp (người nợ, người cho vay) có thể để thực hiện
        một giao dịch thanh toán. Số tiền thanh toán là giá trị nhỏ hơn giữa nợ của người nợ
        và tín dụng của người cho vay.
    5.  Chi phí của một bước được định nghĩa là số tiền thực tế được chuyển.
    6.  Kết quả (chi phí, số lượng giao dịch, danh sách giao dịch, số liệu ưu tiên) cho mỗi trạng thái
        đã giải quyết được lưu trữ để tránh tính toán lại.
    7.  Trường hợp cơ sở của đệ quy là khi tất cả các số dư đều bằng không.
    8.  Thuật toán trả về một Tuple chứa danh sách các giao dịch BasicTransaction đã được tối ưu hóa
        và một HashTable chứa các số liệu thống kê về quá trình tối ưu.

    Độ phức tạp (ước tính):
    -   Thời gian: O(N_people^2 * 3^{N_people}) trong trường hợp xấu nhất nếu không có sự trùng lặp trạng thái nhiều,
        hoặc gần hơn với O( (max_balance_range)^{N_people} * N_people^2 ) nếu số dư được coi là trạng thái.
        Tuy nhiên, với số lượng người vừa phải và cấu trúc nợ cụ thể, hiệu suất thực tế có thể tốt hơn.
    -   Không gian: Chủ yếu phụ thuộc vào kích thước của bảng DP, có thể lớn.

    Ưu điểm:
    -   Tìm kiếm giải pháp tối ưu toàn cục dựa trên tiêu chí chi phí đã định nghĩa (tổng tiền chuyển).
    -   Xử lý chính xác các yếu tố tài chính phức tạp của giao dịch nâng cao.

    Hạn chế:
    -   Độ phức tạp tính toán có thể cao với số lượng lớn người tham gia.
    -   Hiệu suất phụ thuộc vào việc triển khai hiệu quả các cấu trúc dữ liệu (HashTable, LinkedList).
    """

    def __init__(
        self,
        transactions: LinkedList[AdvancedTransaction],
        current_date: date
    ):
        """
        Khởi tạo bộ đơn giản hóa nợ nâng cao.

        Args:
            transactions (LinkedList[AdvancedTransaction]): Danh sách các giao dịch nâng cao ban đầu.
            current_date (date): Ngày hiện tại được sử dụng để tính toán lãi suất, phí phạt,
                                 và các yếu tố tài chính khác.
        """
        self.initial_transactions: LinkedList[AdvancedTransaction] = transactions
        self.current_date: date = current_date
        self.people_real_balances: HashTable[str, float] = HashTable()
        self.people_debt_details: HashTable[str, LinkedList[HashTable[str, Any]]] = HashTable()
        self.all_people_nodes: LinkedList[str] = LinkedList()
        self.advanced_dp_table: AdvancedDPTable = HashTable()
        self.total_priority_score: float = 0.0
        
        self._initialize_advanced_balances()

    def _initialize_advanced_balances(self) -> None:
        """
        Khởi tạo số dư thực tế ban đầu cho mỗi người và các thông tin liên quan.
        Hàm này tính toán tổng số tiền mỗi người nợ hoặc được nợ sau khi đã tính
        toán lãi suất và phí phạt cho tất cả các giao dịch gốc đến `self.current_date`.
        Đồng thời, nó cũng tạo danh sách những người tham gia và tổng điểm ưu tiên.
        """
        unique_names_table: HashTable[str, bool] = HashTable()
        
        if self.initial_transactions.is_empty():
            self.all_people_nodes = LinkedList()
            return

        current_tx_node = self.initial_transactions.head
        while current_tx_node:
            advanced_tx = current_tx_node.data
            if advanced_tx is None:
                current_tx_node = current_tx_node.next
                continue

            # Theo dõi tên người tham gia duy nhất
            unique_names_table.put(advanced_tx.debtor, True)
            unique_names_table.put(advanced_tx.creditor, True)

            # Tính toán nợ thực tế (bao gồm gốc, lãi, phạt) cho giao dịch hiện tại
            debt_breakdown = FinancialCalculator.calculate_total_debt(
                amount=advanced_tx.amount,
                interest_rate=advanced_tx.interest_rate,
                penalty_rate=advanced_tx.penalty_rate,
                borrow_date=advanced_tx.borrow_date,
                due_date=advanced_tx.due_date,
                current_date=self.current_date,
                interest_type=advanced_tx.interest_type,
                penalty_type=advanced_tx.penalty_type,
            )
            real_debt_amount = debt_breakdown["total"]

            # Tính điểm ưu tiên cho giao dịch
            priority_score = FinancialCalculator.calculate_priority_score(
                principal=advanced_tx.amount,
                interest_rate=advanced_tx.interest_rate,
                penalty_rate=advanced_tx.penalty_rate,
                borrow_date=advanced_tx.borrow_date,
                due_date=advanced_tx.due_date,
                current_date=self.current_date,
                interest_type=advanced_tx.interest_type,
                penalty_type=advanced_tx.penalty_type,
            )
            self.total_priority_score += priority_score

            # Cập nhật số dư thực tế cho người nợ và người cho vay
            current_debtor_balance = self.people_real_balances.get(advanced_tx.debtor, 0.0)
            self.people_real_balances.put(
                advanced_tx.debtor, round_money(current_debtor_balance - real_debt_amount)
            )

            current_creditor_balance = self.people_real_balances.get(advanced_tx.creditor, 0.0)
            self.people_real_balances.put(
                advanced_tx.creditor, round_money(current_creditor_balance + real_debt_amount)
            )

            # Lưu trữ chi tiết nợ cho mục đích phân tích (nếu cần thiết)
            self._store_debt_details(
                person_name=advanced_tx.debtor,
                debt_breakdown=debt_breakdown,
                priority_score=priority_score,
                transaction=advanced_tx,
                is_creditor=False,
            )
            self._store_debt_details(
                person_name=advanced_tx.creditor,
                debt_breakdown=debt_breakdown,
                priority_score=priority_score,
                transaction=advanced_tx,
                is_creditor=True,
            )
            current_tx_node = current_tx_node.next

        # Tạo danh sách tên người tham gia duy nhất và sắp xếp theo thứ tự bảng chữ cái
        names_ll_from_ht = unique_names_table.keys()
        if names_ll_from_ht and not names_ll_from_ht.is_empty():
            self.all_people_nodes = merge_sort_linked_list(
                names_ll_from_ht,
                comparator=lambda a, b: a < b
            )
        else:
             self.all_people_nodes = LinkedList()


    def _store_debt_details(
        self,
        person_name: str,
        debt_breakdown: HashTable[str, float],
        priority_score: float,
        transaction: AdvancedTransaction,
        is_creditor: bool = False
    ) -> None:
        """Lưu trữ thông tin chi tiết về một khoản nợ/cho vay cụ thể liên quan đến một người."""
        detail_entry: HashTable[str, Any] = HashTable()
        detail_entry.put("principal", debt_breakdown["principal"])
        detail_entry.put("interest", debt_breakdown["interest"])
        detail_entry.put("penalty", debt_breakdown["penalty"])
        detail_entry.put("total", debt_breakdown["total"])
        detail_entry.put("priority_score", priority_score)
        detail_entry.put("is_creditor", 1.0 if is_creditor else 0.0) # Sử dụng float cho nhất quán
        
        # Lưu trữ thông tin từ giao dịch gốc để tham khảo
        detail_entry.put("original_debtor", transaction.debtor)
        detail_entry.put("original_creditor", transaction.creditor)
        detail_entry.put("original_borrow_date", transaction.borrow_date)
        detail_entry.put("original_due_date", transaction.due_date)

        days_overdue_val = 0.0
        if hasattr(transaction, 'days_overdue') and callable(getattr(transaction, 'days_overdue')):
             days_overdue_val = float(transaction.days_overdue(self.current_date))
        elif hasattr(transaction, 'due_date') and hasattr(transaction, 'borrow_date'): # Dự phòng
            if transaction.due_date and self.current_date > transaction.due_date:
                days_overdue_val = float((self.current_date - transaction.due_date).days)
        detail_entry.put("days_overdue", days_overdue_val)

        if not self.people_debt_details.contains_key(person_name):
            self.people_debt_details.put(person_name, LinkedList[HashTable[str, Any]]())
        
        person_details_list = self.people_debt_details.get(person_name)
        if person_details_list is not None:
            person_details_list.append(detail_entry)


    def _get_balances_tuple_key(self, current_balances: HashTable[str, float]) -> Tuple:
        """
        Tạo một khóa Tuple duy nhất từ trạng thái số dư hiện tại.
        Thứ tự của các số dư trong Tuple được xác định bởi `self.all_people_nodes` (đã được sắp xếp),
        đảm bảo tính nhất quán của khóa cho bảng DP.
        """
        py_balances_list = Array[Any]()
        if not self.all_people_nodes.is_empty():
            current_name_node = self.all_people_nodes.head
            while current_name_node:
                name = current_name_node.data
                if name is not None:
                    py_balances_list.append(value=round_money(current_balances.get(name, 0.0)))
                current_name_node = current_name_node.next
        return Tuple(py_balances_list)


    def _deep_copy_balances_map(self, source_balances: HashTable[str, float]) -> HashTable[str, float]:
        """
        Tạo một bản sao sâu của HashTable chứa số dư.
        Điều này quan trọng để đảm bảo các nhánh khác nhau của cây đệ quy DP
        hoạt động trên các bản sao độc lập của trạng thái số dư.
        """
        copied_balances = HashTable[str, float]()
        
        if hasattr(source_balances, 'capacity') and hasattr(source_balances, 'load_factor_threshold'):
            copied_balances = HashTable[str, float](capacity=source_balances.capacity,
                                                load_factor_threshold=source_balances.load_factor_threshold)
        
      
        for key in source_balances:
            value = source_balances.get(key)
            if value is not None: # Kiểm tra an toàn
                 copied_balances.put(key, value)
        return copied_balances

    def _find_priority_based_settlements(self, current_balances_map: HashTable[str, float]) -> Tuple: 
        """
        (Hàm này không được sử dụng trong logic DP chính hiện tại, có thể dùng cho các chiến lược khác hoặc phân tích).
        Tìm kiếm các giải pháp thanh toán dựa trên độ ưu tiên của người nợ và người cho vay.
        Sử dụng hàng đợi ưu tiên để ghép cặp.
        """
        simplified_tx_list = LinkedList[BasicTransaction]()
        balances_after_settlement = self._deep_copy_balances_map(current_balances_map)
        financial_cost = 0.0
        num_tx_this_step = 0
        total_priority_handled_this_step = 0.0

        # Bộ so sánh cho hàng đợi ưu tiên
        def debtor_comparator(t1_tuple: Tuple, t2_tuple: Tuple) -> bool:
            return t1_tuple[2] > t2_tuple[2] # Ưu tiên điểm ưu tiên trung bình cao hơn (index 2)

        def creditor_comparator(t1_tuple: Tuple, t2_tuple: Tuple) -> bool:
            norm_p_score = max(1.0, self.total_priority_score if self.total_priority_score > 0 else 1.0)
            eff1 = t1_tuple[1] * (1 + t1_tuple[2] / norm_p_score) # balance (idx 1), priority (idx 2)
            eff2 = t2_tuple[1] * (1 + t2_tuple[2] / norm_p_score)
            return eff1 > eff2

        # Khởi tạo hàng đợi ưu tiên. Item là Tuple: (tên_người, số_dư, điểm_ưu_tiên_tb)
        priority_debtors_pq = PriorityQueue[Tuple](comparator=debtor_comparator)
        priority_creditors_pq = PriorityQueue[Tuple](comparator=creditor_comparator)

        # Đưa người nợ/cho vay vào hàng đợi
        for person_name in balances_after_settlement: # Giả sử HashTable lặp qua các khóa
            balance = balances_after_settlement.get(person_name, 0.0)
            avg_priority = self._calculate_person_avg_priority(person_name)
            
            item_tuple_for_pq = Tuple([person_name, balance, avg_priority])

            if balance < -EPSILON: # Người nợ
                priority_debtors_pq.enqueue(item_tuple_for_pq)
            elif balance > EPSILON: # Người cho vay
                priority_creditors_pq.enqueue(item_tuple_for_pq)
        
        # Xử lý thanh toán
        while not priority_debtors_pq.is_empty() and not priority_creditors_pq.is_empty():
            debtor_item_tuple = priority_debtors_pq.dequeue()
            d_name, d_balance, d_priority = debtor_item_tuple[0], debtor_item_tuple[1], debtor_item_tuple[2]

            creditor_item_tuple = priority_creditors_pq.dequeue()
            c_name, c_balance, c_priority = creditor_item_tuple[0], creditor_item_tuple[1], creditor_item_tuple[2]
            
            amount_to_settle = round_money(min(abs(d_balance), c_balance))
            if amount_to_settle > EPSILON:
                simplified_tx_list.append(BasicTransaction(debtor=d_name, creditor=c_name, amount=amount_to_settle))
                financial_cost += amount_to_settle
                num_tx_this_step += 1
                # Tính toán điểm ưu tiên được xử lý bởi giao dịch này (ước lượng)
                total_priority_handled_this_step += amount_to_settle * (d_priority + c_priority) / 2.0 

                # Cập nhật số dư và đưa lại vào hàng đợi nếu cần
                new_d_balance = round_money(d_balance + amount_to_settle)
                new_c_balance = round_money(c_balance - amount_to_settle)
                balances_after_settlement.put(d_name, new_d_balance)
                balances_after_settlement.put(c_name, new_c_balance)

                if new_d_balance < -EPSILON:
                    priority_debtors_pq.enqueue(Tuple([d_name, new_d_balance, d_priority]))
                if new_c_balance > EPSILON:
                    priority_creditors_pq.enqueue(Tuple([c_name, new_c_balance, c_priority]))
        
        return Tuple([simplified_tx_list, # Các giao dịch thực hiện trong bước này
                      Tuple([financial_cost, num_tx_this_step, total_priority_handled_this_step]), # Thống kê bước này
                      balances_after_settlement]) # Số dư đã cập nhật


    def _calculate_person_avg_priority(self, person_name: str) -> float:
        """Tính điểm ưu tiên trung bình cho một người dựa trên các khoản nợ/cho vay liên quan đến họ."""
        if not self.people_debt_details.contains_key(person_name):
            return 0.0
        
        details_list = self.people_debt_details.get(person_name) # LinkedList các HashTable chi tiết
        if not details_list or details_list.is_empty():
            return 0.0

        total_priority_sum = 0.0
        count = 0
        current_detail_node = details_list.head
        while current_detail_node:
            entry_ht = current_detail_node.data # Đây là một HashTable chứa "priority_score"
            if entry_ht is not None:
                 priority_val = entry_ht.get("priority_score")
                 if priority_val is not None:
                    total_priority_sum += float(priority_val) 
                 count += 1
            current_detail_node = current_detail_node.next
            
        return (total_priority_sum / count) if count > 0 else 0.0


    def _solve_advanced_dp_recursive(self, current_balances_map: HashTable[str, float]) -> AdvancedDPValueTuple:
        """
        Hàm đệ quy chính của thuật toán Quy hoạch động nâng cao.
        Tìm giải pháp tối ưu (chi phí thấp nhất, sau đó là số lượng giao dịch ít nhất)
        cho trạng thái số dư hiện tại.
        """
        key_tuple = self._get_balances_tuple_key(current_balances_map)

        # Kiểm tra bảng ghi nhớ xem trạng thái này đã được giải quyết chưa
        memoized_result = self.advanced_dp_table.get(key_tuple)
        if memoized_result is not None:
            return memoized_result

        # Trường hợp cơ sở: kiểm tra xem tất cả số dư có bằng không không
        all_zero = True
        if not self.all_people_nodes.is_empty():
            current_name_node_check = self.all_people_nodes.head
            while current_name_node_check:
                name = current_name_node_check.data
                if name is not None and abs(current_balances_map.get(name, 0.0)) > EPSILON:
                    all_zero = False
                    break
                current_name_node_check = current_name_node_check.next
        elif not current_balances_map.is_empty(): # Fallback, không nên xảy ra nếu khởi tạo đúng
            all_zero = False 
            for name_key in current_balances_map:
                if abs(current_balances_map.get(name_key, 0.0)) > EPSILON:
                    break
            else: # Vòng lặp hoàn thành không break, nghĩa là tất cả bằng 0 (hoặc map rỗng)
                 all_zero = current_balances_map.is_empty()

        if all_zero:
            # Nếu tất cả số dư bằng không, không cần làm gì thêm
            # Trả về: (tổng_chi_phí, số_GD, danh_sách_GD, tổng_ưu_tiên_xử_lý)
            result = Tuple([0.0, 0, LinkedList[BasicTransaction](), 0.0])
            self.advanced_dp_table.put(key_tuple, result)
            return result

        # Xác định danh sách người nợ và người cho vay từ trạng thái hiện tại
        debtors = Array[Any]()
        creditors = Array[Any]()
        if not self.all_people_nodes.is_empty():
            current_name_node_iter = self.all_people_nodes.head
            while current_name_node_iter:
                name = current_name_node_iter.data
                if name is not None:
                    bal = current_balances_map.get(name, 0.0)
                    if bal < -EPSILON: # Người nợ có số dư âm
                        debtors.append(value=name)
                    elif bal > EPSILON: # Người cho vay có số dư dương
                        creditors.append(value=name)
                current_name_node_iter = current_name_node_iter.next

        # Khởi tạo các biến để theo dõi giải pháp tốt nhất cho trạng thái hiện tại
        best_current_cost = float("inf")
        best_current_count = float("inf")
        best_tx_list = LinkedList[BasicTransaction]()
        best_priority_handled = 0.0 # Số liệu ưu tiên tốt nhất

        # Thử tất cả các cặp (người_nợ, người_cho_vay) có thể có để thực hiện một giao dịch
        for debtor_name in debtors:
            for creditor_name in creditors:
                # Tạo bản sao sâu của số dư để thao tác trong nhánh đệ quy này
                new_balances_for_recursion = self._deep_copy_balances_map(current_balances_map)

                debtor_current_balance = new_balances_for_recursion.get(debtor_name, 0.0)
                creditor_current_balance = new_balances_for_recursion.get(creditor_name, 0.0)

                # Số tiền thực tế có thể chuyển là giá trị nhỏ hơn giữa nợ và tín dụng
                amount_transferred_monetary = round_money(min(abs(debtor_current_balance), creditor_current_balance))
                
                # Bỏ qua nếu số tiền chuyển quá nhỏ
                if amount_transferred_monetary <= EPSILON or amount_transferred_monetary < 0.01:
                    continue

                # Thực hiện giao dịch thử nghiệm trên bản sao số dư
                new_balances_for_recursion.put(debtor_name, round_money(debtor_current_balance + amount_transferred_monetary))
                new_balances_for_recursion.put(creditor_name, round_money(creditor_current_balance - amount_transferred_monetary))

                # Định nghĩa chi phí của bước này là số tiền được chuyển
                # Đây là cách tiếp cận đã được xác minh là hoạt động tốt và đơn giản.
                cost_of_this_step = amount_transferred_monetary

                # Tính một số liệu ưu tiên cho bước này (có thể được cải thiện/tùy chỉnh)
                priority_metric_this_step = (self._calculate_person_avg_priority(debtor_name) +
                                            self._calculate_person_avg_priority(creditor_name)) / 2.0

                current_step_tx = BasicTransaction(debtor=debtor_name, creditor=creditor_name,
                                                amount=amount_transferred_monetary)
                
                # Gọi đệ quy cho trạng thái số dư mới sau giao dịch thử nghiệm
                recursive_result_tuple = self._solve_advanced_dp_recursive(new_balances_for_recursion)

                # Trích xuất kết quả từ lời gọi đệ quy
                rec_cost, rec_count, rec_tx_list, rec_priority_handled = \
                    recursive_result_tuple[0], recursive_result_tuple[1], recursive_result_tuple[2], recursive_result_tuple[3]

                # Tính tổng chi phí, tổng số giao dịch, và tổng ưu tiên cho đường đi hiện tại
                path_total_cost = cost_of_this_step + rec_cost
                path_total_count = 1 + rec_count
                path_total_priority_handled = priority_metric_this_step + rec_priority_handled

                # Xây dựng danh sách giao dịch cho đường đi này
                path_tx_list = LinkedList[BasicTransaction]()
                path_tx_list.append(current_step_tx)
                if rec_tx_list and not rec_tx_list.is_empty():
                    rec_tx_node = rec_tx_list.head
                    while rec_tx_node:
                        if rec_tx_node.data: # Đảm bảo dữ liệu không None
                            path_tx_list.append(rec_tx_node.data)
                        rec_tx_node = rec_tx_node.next
                
                # So sánh và cập nhật giải pháp tốt nhất nếu đường đi này tốt hơn
                # Tiêu chí: tổng chi phí thấp hơn, hoặc chi phí bằng nhau nhưng số giao dịch ít hơn.
                if path_total_cost < best_current_cost or \
                   (abs(path_total_cost - best_current_cost) < EPSILON and path_total_count < best_current_count):
                    best_current_cost = path_total_cost
                    best_current_count = path_total_count
                    best_tx_list = path_tx_list
                    best_priority_handled = path_total_priority_handled

        # Lưu kết quả tốt nhất tìm được cho trạng thái này vào bảng DP
        final_best_result_for_state = Tuple([best_current_cost, best_current_count, best_tx_list, best_priority_handled])
        self.advanced_dp_table.put(key_tuple, final_best_result_for_state)
        return final_best_result_for_state


    def _estimate_borrow_date(self, debtor_simpl_tx: str, creditor_simpl_tx: str) -> date:
        """
        Ước tính ngày vay sớm nhất cho một giao dịch đơn giản hóa tiềm năng giữa hai người.
        Hàm này được sử dụng nếu `cost_of_this_step` trong DP sử dụng một heuristic phức tạp
        cần ngày vay. Với `cost_of_this_step = amount_transferred_monetary`, hàm này ít quan trọng hơn.
        """
        earliest_borrow_date = self.current_date # Giá trị mặc định

        # Tìm kiếm trong chi tiết nợ đã lưu trữ
        # Cố gắng tìm một giao dịch gốc mà debtor_simpl_tx nợ creditor_simpl_tx
        if self.people_debt_details.contains_key(debtor_simpl_tx):
            debt_details_list = self.people_debt_details.get(debtor_simpl_tx)
            if debt_details_list and not debt_details_list.is_empty():
                detail_node = debt_details_list.head
                while detail_node:
                    entry_ht = detail_node.data # HashTable chi tiết
                    if entry_ht:
                        original_debtor = entry_ht.get("original_debtor")
                        original_creditor = entry_ht.get("original_creditor")
                        original_b_date = entry_ht.get("original_borrow_date") # Phải là đối tượng date

                        if (original_debtor == debtor_simpl_tx and
                            original_creditor == creditor_simpl_tx and
                            isinstance(original_b_date, date)): # Đảm bảo original_b_date là kiểu date
                            if original_b_date < earliest_borrow_date:
                                earliest_borrow_date = original_b_date
                    detail_node = detail_node.next
        
        return earliest_borrow_date


    def simplify(self) -> Tuple:
        """
        Điểm vào chính để thực hiện quá trình đơn giản hóa nợ nâng cao.

        Returns:
            Tuple: Một tuple chứa hai phần tử:
                   1. LinkedList[BasicTransaction]: Danh sách các giao dịch cơ bản đã được tối ưu hóa.
                   2. HashTable[str, float]: Một bảng băm chứa các số liệu thống kê về quá trình tối ưu hóa.
        """
        if self.initial_transactions.is_empty():
            # Xử lý trường hợp không có giao dịch đầu vào
            empty_stats = HashTable[str, float]()
            empty_stats.put("total_cost", 0.0)
            empty_stats.put("total_transactions", 0.0)
            empty_stats.put("priority_efficiency", 0.0) # Hiệu quả ưu tiên
            empty_stats.put("cost_reduction_ratio", 0.0) # Tỷ lệ giảm chi phí
            empty_stats.put("average_overdue_days", 0.0) # Số ngày quá hạn trung bình
            empty_stats.put("total_interest_saved", 0.0) # Tổng lãi (và phạt) tiết kiệm được
            return Tuple([LinkedList[BasicTransaction](), empty_stats])

        # Gọi hàm giải DP đệ quy với trạng thái số dư thực tế ban đầu
        final_res_tuple = self._solve_advanced_dp_recursive(self.people_real_balances)
        
        # Giải nén kết quả từ DP
        # final_res_tuple: (tổng_chi_phí_tiền_tệ, tổng_số_GD_đơn_giản, ds_GD_đơn_giản, tổng_ưu_tiên_xử_lý)
        total_monetary_cost_simplified = final_res_tuple[0]
        total_simplified_tx_count = final_res_tuple[1]
        simplified_tx_list = final_res_tuple[2]
        total_priority_metric_handled = final_res_tuple[3]

        # Chuẩn bị HashTable thống kê
        stats = HashTable[str, float]()
        stats.put("total_cost", total_monetary_cost_simplified) # Tổng chi phí (tiền chuyển) sau tối ưu
        stats.put("total_transactions", float(total_simplified_tx_count)) # Tổng số giao dịch sau tối ưu
        
        priority_efficiency = 0.0
        if self.total_priority_score > EPSILON:
             priority_efficiency = total_priority_metric_handled / self.total_priority_score
        stats.put("priority_efficiency", priority_efficiency * 100) # Hiệu quả ưu tiên (dưới dạng %)

        original_sum_of_real_debts = self._calculate_original_total_cost() # Tổng nợ thực tế ban đầu
        
        cost_reduction_ratio = 0.0
        if original_sum_of_real_debts > EPSILON:
            # Tỷ lệ giảm chi phí (dựa trên tổng tiền chuyển thực tế so với tổng nợ gốc)
            cost_reduction_ratio = max(0.0, (original_sum_of_real_debts - total_monetary_cost_simplified) / original_sum_of_real_debts)
        stats.put("cost_reduction_ratio", cost_reduction_ratio * 100) # Chuyển sang phần trăm
        
        stats.put("average_overdue_days", self._calculate_avg_overdue_days()) # Số ngày quá hạn trung bình
        
        # Tổng tiền lãi (và phạt) tiềm năng đã tiết kiệm được
        total_interest_saved = max(0.0, original_sum_of_real_debts - total_monetary_cost_simplified)
        stats.put("total_interest_saved", total_interest_saved)

        return Tuple([simplified_tx_list, stats])

    def _calculate_original_total_cost(self) -> float:
        """Tính tổng giá trị nợ thực tế của tất cả các giao dịch ban đầu."""
        total = 0.0
        if self.initial_transactions.is_empty():
            return 0.0
            
        current_tx_node = self.initial_transactions.head
        while current_tx_node:
            adv_tx = current_tx_node.data
            if adv_tx is None:
                current_tx_node = current_tx_node.next
                continue

            debt_breakdown = FinancialCalculator.calculate_total_debt(
                amount=adv_tx.amount,
                interest_rate=adv_tx.interest_rate,
                penalty_rate=adv_tx.penalty_rate,
                borrow_date=adv_tx.borrow_date,
                due_date=adv_tx.due_date,
                current_date=self.current_date,
                interest_type=adv_tx.interest_type,
                penalty_type=adv_tx.penalty_type,
            )
            total += debt_breakdown["total"]
            current_tx_node = current_tx_node.next
        return round_money(total)

    def _calculate_avg_overdue_days(self) -> float:
        """Tính số ngày quá hạn trung bình của các giao dịch ban đầu."""
        total_overdue_days_sum = 0.0
        num_transactions_counted = 0
        if self.initial_transactions.is_empty():
            return 0.0
            
        current_tx_node = self.initial_transactions.head
        while current_tx_node:
            adv_tx = current_tx_node.data
            if adv_tx is None:
                current_tx_node = current_tx_node.next
                continue

            overdue_days_for_this_tx = 0.0
            # Ưu tiên sử dụng phương thức days_overdue nếu có
            if hasattr(adv_tx, 'days_overdue') and callable(getattr(adv_tx, 'days_overdue')):
                 overdue_days_for_this_tx = float(adv_tx.days_overdue(self.current_date))
            elif hasattr(adv_tx, 'due_date') and hasattr(adv_tx, 'borrow_date'): # Fallback
                if adv_tx.due_date and self.current_date > adv_tx.due_date: # Kiểm tra due_date không None
                    overdue_days_for_this_tx = float((self.current_date - adv_tx.due_date).days)
            
            # Chỉ cộng dồn nếu thực sự quá hạn (ngày > 0)
            if overdue_days_for_this_tx > 0:
                total_overdue_days_sum += overdue_days_for_this_tx
            num_transactions_counted += 1 # Tất cả giao dịch đều được tính vào mẫu số
            current_tx_node = current_tx_node.next
            
        return (total_overdue_days_sum / num_transactions_counted) if num_transactions_counted > 0 else 0.0

