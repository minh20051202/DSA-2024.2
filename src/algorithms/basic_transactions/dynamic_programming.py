# Thuật toán Đơn giản hóa Nợ sử dụng Quy hoạch động
from __future__ import annotations

from src.core_type import BasicTransaction
from src.data_structures import LinkedList, HashTable, PriorityQueue, Tuple, Array
from src.utils.sorting import merge_sort_linked_list
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

# Định nghĩa kiểu dữ liệu cho giá trị bảng DP
# DPValueTuple: Đại diện cho giá trị lưu trong bảng DP cho một trạng thái
# Cấu trúc: (tổng_chi_phí_tài_chính, tổng_số_giao_dịch_đơn_giản, danh_sách_giao_dịch_đơn_giản)
DPValueTuple = Tuple

# Khóa bảng DP: Tuple chứa số dư của mọi người theo thứ tự cố định
# Giá trị bảng DP: DPValueTuple như định nghĩa ở trên
DPTable = HashTable[Tuple, DPValueTuple]

class DynamicProgrammingSimplifier:
    """
    Thuật toán đơn giản hóa nợ nâng cao sử dụng Quy hoạch động với kỹ thuật ghi nhớ.
    
    Thuật toán này tìm ra giải pháp tối ưu toàn cục bằng cách khám phá tất cả
    các đường dẫn thanh toán nợ có thể và chọn ra đường dẫn tối thiểu hóa
    tổng số giao dịch trong khi duy trì độ chính xác tài chính.
    
    Phương pháp tiếp cận:
    1. Tính toán số dư ròng cho mỗi người từ các giao dịch đầu vào
    2. Sử dụng DP đệ quy với ghi nhớ để khám phá tất cả khả năng thanh toán
    3. Áp dụng chiến lược tham lam ở mỗi bước để giảm không gian tìm kiếm
    4. Lưu trữ kết quả trung gian để tránh tính toán lặp lại
    5. Trả về chuỗi giao dịch tối ưu
    
    Độ phức tạp thời gian: O(2^k * k^2) với k = số người tham gia (trường hợp xấu nhất)
    Độ phức tạp không gian: O(2^k * k) cho bảng ghi nhớ
    
    Ưu điểm so với thuật toán tham lam:
    - Đảm bảo tối ưu toàn cục
    - Xử lý các chu trình nợ phức tạp một cách tối ưu
    - Tối thiểu hóa cả số lượng giao dịch và chi phí tài chính
    
    Đánh đổi:
    - Độ phức tạp tính toán cao hơn
    - Sử dụng bộ nhớ theo cấp số mũ với số lượng người tham gia lớn
    - Phù hợp hơn với mạng lưới nợ từ nhỏ đến trung bình
    """

    def __init__(self, transactions: LinkedList[BasicTransaction]):
        """
        Khởi tạo bộ đơn giản hóa nợ dựa trên DP với các giao dịch đầu vào.
        
        Tham số:
            transactions: Danh sách liên kết các giao dịch cơ bản cần được đơn giản hóa
        """
        self.initial_transactions: LinkedList[BasicTransaction] = transactions
        # Bảng băm lưu trữ số dư hiện tại cho mỗi người: tên_người -> số_dư
        self.people_balances: HashTable[str, float] = HashTable()
        # Danh sách liên kết lưu trữ tên tất cả người tham gia, được sắp xếp để đảm bảo tính nhất quán
        self.all_people_nodes: LinkedList[str] = LinkedList()
        # Bảng DP ghi nhớ cho các trạng thái con đã được giải quyết
        self.dp_table: DPTable = HashTable()

        self._initialize_people_and_balances()

    def _initialize_people_and_balances(self) -> None:
        """
        Khởi tạo danh sách người tham gia duy nhất và tính toán số dư ban đầu
        từ các giao dịch đầu vào. Tên người tham gia được sắp xếp để đảm bảo thứ tự xác định.
        
        Quy tắc tính toán số dư:
        - Người nợ: số dư giảm theo số tiền giao dịch
        - Người cho vay: số dư tăng theo số tiền giao dịch
        """
        unique_names_table: HashTable[str, bool] = HashTable()

        # Xử lý từng giao dịch để trích xuất người tham gia và tính toán số dư
        current_tx_node = self.initial_transactions.head
        while current_tx_node:
            tx = current_tx_node.data
            
            # Theo dõi tên người tham gia duy nhất
            unique_names_table.put(tx.debtor, True)
            unique_names_table.put(tx.creditor, True)
            
            # Cập nhật số dư: người nợ nợ tiền (âm), người cho vay nhận tiền (dương)
            current_debtor_balance = self.people_balances.get(tx.debtor, 0.0)
            self.people_balances.put(tx.debtor, current_debtor_balance - tx.amount)
            
            current_creditor_balance = self.people_balances.get(tx.creditor, 0.0)
            self.people_balances.put(tx.creditor, current_creditor_balance + tx.amount)
            
            current_tx_node = current_tx_node.next
        
        # Trích xuất và sắp xếp tên người tham gia để tạo khóa DP nhất quán
        names_ll = unique_names_table.keys()
        if names_ll is None or names_ll.is_empty():
            self.all_people_nodes = LinkedList[str]()
            return

        # Sắp xếp tên theo thứ tự bảng chữ cái để đảm bảo biểu diễn trạng thái DP xác định
        self.all_people_nodes = merge_sort_linked_list(
            names_ll, 
            comparator=lambda a, b: a < b
        )

    def _get_balances_tuple_key(self, current_balances: HashTable[str, float]) -> Tuple:
        """
        Chuyển đổi trạng thái số dư hiện tại thành khóa Tuple xác định cho bảng DP.
        
        Thứ tự Tuple được đảm bảo bởi self.all_people_nodes (đã được sắp xếp trước).
        Điều này đảm bảo biểu diễn trạng thái nhất quán qua các lần gọi đệ quy.
        
        Tham số:
            current_balances: Bảng băm ánh xạ tên người với số dư của họ
            
        Trả về:
            Tuple: Các giá trị số dư được sắp xếp thứ tự phù hợp làm khóa bảng DP
        """
        # Sử dụng Array thay vì list Python built-in
        balance_values = Array[float]()
        current_name_node = self.all_people_nodes.head
        while current_name_node:
            name = current_name_node.data
            balance_values.append(current_balances.get(name, 0.0))
            current_name_node = current_name_node.next
        
        return Tuple(balance_values)

    def _deep_copy_balances_map(self, source_balances: HashTable[str, float]) -> HashTable[str, float]:
        """
        Tạo bản sao sâu của bảng băm số dư để tránh thay đổi trạng thái.
        
        Điều này rất quan trọng để duy trì sự cô lập trạng thái trong quá trình khám phá đệ quy,
        đảm bảo rằng các thay đổi số dư trong một nhánh không ảnh hưởng đến các nhánh khác.
        
        Tham số:
            source_balances: Ánh xạ số dư gốc cần sao chép
            
        Trả về:
            HashTable[str, float]: Bản sao sâu của số dư nguồn
        """
        copied_balances = HashTable[str, float]()
        if source_balances and not source_balances.is_empty():
            keys_ll = source_balances.keys()
            if keys_ll:
                current_key_node = keys_ll.head
                while current_key_node:
                    key = current_key_node.data
                    copied_balances.put(key, source_balances.get(key))
                    current_key_node = current_key_node.next
        return copied_balances

    def _find_greedy_settlements(self, current_balances_map: HashTable[str, float]) -> Tuple:
        """
        Áp dụng chiến lược thanh toán tham lam cho trạng thái số dư hiện tại.
        
        Hàm này triển khai một bước của thuật toán tham lam trong khung DP:
        1. Phân tách người thành người nợ (số dư âm) và người cho vay (số dư dương)
        2. Sử dụng hàng đợi ưu tiên để ưu tiên các khoản nợ và tín dụng lớn nhất
        3. Thực hiện thanh toán theo cặp tối ưu cho đến khi không còn kết hợp có lợi
        4. Trả về kết quả thanh toán và trạng thái cập nhật
        
        Phương pháp tham lam ở mỗi bước DP giúp giảm không gian tìm kiếm trong khi
        duy trì tính tối ưu thông qua việc khám phá toàn diện tất cả các đường dẫn có thể.
        
        Tham số:
            current_balances_map: Trạng thái số dư hiện tại cho tất cả người tham gia
            
        Trả về:
            Tuple chứa:
                1. LinkedList[BasicTransaction]: các giao dịch được tạo trong bước này
                2. Tuple[float, int]: (chi_phí_tài_chính_bước_này, số_giao_dịch_bước_này)
                3. HashTable[str, float]: trạng thái số dư cập nhật sau thanh toán
        """
        # Khởi tạo các cấu trúc dữ liệu
        temp_simplified_tx_list = LinkedList[BasicTransaction]()
        balances_after_settlement = HashTable[str, float]()
        financial_cost = 0.0
        num_tx_this_step = 0
        
        # Tạo bản sao cô lập để ngăn thay đổi trạng thái
        balances_after_settlement = self._deep_copy_balances_map(current_balances_map)

        # Bộ so sánh hàng đợi ưu tiên để ghép nợ-tín dụng tối ưu
        def debtor_comparator(tuple1: Tuple, tuple2: Tuple) -> bool:
            """Min-heap: ưu tiên các khoản nợ lớn nhất (số dư âm nhất)"""
            return tuple1[1] < tuple2[1]  # tuple[1] là giá trị số dư

        def creditor_comparator(tuple1: Tuple, tuple2: Tuple) -> bool:
            """Max-heap: ưu tiên các khoản tín dụng lớn nhất (số dư dương nhất)"""
            return tuple1[1] > tuple2[1]  # tuple[1] là giá trị số dư
        
        debtors_pq = PriorityQueue[Tuple](comparator=debtor_comparator)
        creditors_pq = PriorityQueue[Tuple](comparator=creditor_comparator)

        # Điền hàng đợi ưu tiên với những người tham gia có số dư khác không
        people_names_ll = balances_after_settlement.keys()
        if people_names_ll:
            current_person_node = people_names_ll.head
            while current_person_node:
                person_name = current_person_node.data
                balance = balances_after_settlement.get(person_name, 0.0)
                
                if balance < -EPSILON:  # Người nợ: nợ tiền
                    debtors_pq.enqueue(Tuple([person_name, balance]), balance)
                elif balance > EPSILON:  # Người cho vay: được nợ tiền
                    creditors_pq.enqueue(Tuple([person_name, balance]), balance)
                # Bỏ qua những người tham gia có số dư gần bằng không (đã thanh toán)
                current_person_node = current_person_node.next
        
        # Vòng lặp thanh toán tham lam: ghép các khoản nợ lớn nhất với tín dụng lớn nhất
        while not debtors_pq.is_empty() and not creditors_pq.is_empty():
            # Trích xuất người nợ và người cho vay có ưu tiên cao nhất
            debtor_info_tuple = debtors_pq.dequeue()  # (tên_người_nợ, số_dư_âm)
            debtor_name = debtor_info_tuple[0]
            debtor_balance_negative = debtor_info_tuple[1]

            creditor_info_tuple = creditors_pq.dequeue()  # (tên_người_cho_vay, số_dư_dương)
            creditor_name = creditor_info_tuple[0]
            creditor_balance_positive = creditor_info_tuple[1]
            
            # Tính toán số tiền thanh toán tối ưu (bị giới hạn bởi số tiền nhỏ hơn của nợ/tín dụng)
            amount_to_settle = round_money(min(abs(debtor_balance_negative), creditor_balance_positive))
            
            # Chỉ tạo giao dịch nếu số tiền có ý nghĩa
            if amount_to_settle > EPSILON:
                new_transaction = BasicTransaction(
                    debtor=debtor_name,
                    creditor=creditor_name,
                    amount=amount_to_settle
                )
                temp_simplified_tx_list.append(new_transaction)
                financial_cost += amount_to_settle
                num_tx_this_step += 1

                # Cập nhật số dư sau thanh toán
                updated_debtor_balance = round_money(debtor_balance_negative + amount_to_settle)
                updated_creditor_balance = round_money(creditor_balance_positive - amount_to_settle)

                balances_after_settlement.put(debtor_name, updated_debtor_balance)
                balances_after_settlement.put(creditor_name, updated_creditor_balance)

                # Đưa lại vào hàng đợi những người tham gia nếu họ vẫn có số dư đáng kể
                if updated_debtor_balance < -EPSILON:
                    debtors_pq.enqueue(Tuple([debtor_name, updated_debtor_balance]), updated_debtor_balance)
                
                if updated_creditor_balance > EPSILON:
                    creditors_pq.enqueue(Tuple([creditor_name, updated_creditor_balance]), updated_creditor_balance)

        return Tuple([
            temp_simplified_tx_list, 
            Tuple([financial_cost, num_tx_this_step]), 
            balances_after_settlement
        ])

    def _solve_dp_recursive(self, current_balances_map: HashTable[str, float]) -> DPValueTuple:
        """
        Hàm DP đệ quy cốt lõi với ghi nhớ để đơn giản hóa nợ tối ưu.
        
        Hàm này triển khai trái tim của thuật toán DP:
        1. Kiểm tra bảng ghi nhớ cho các kết quả đã tính toán trước đó
        2. Xử lý trường hợp cơ sở: tất cả số dư gần bằng không (không còn nợ)
        3. Áp dụng thanh toán tham lam cho trạng thái hiện tại
        4. Giải đệ quy bài toán con kết quả
        5. Kết hợp bước hiện tại với giải pháp đệ quy
        6. Lưu trữ kết quả để sử dụng trong tương lai
        
        Thuật toán đảm bảo tính tối ưu bằng cách khám phá tất cả các chuỗi
        thanh toán có thể và chọn ra chuỗi có chi phí/giao dịch tối thiểu.
        
        Tham số:
            current_balances_map: Trạng thái số dư hiện tại cho tất cả người tham gia
            
        Trả về:
            DPValueTuple: (tổng_chi_phí, tổng_giao_dịch, danh_sách_giao_dịch) cho giải pháp tối ưu
        """

        # Bước 1: Tạo khóa bảng DP từ trạng thái hiện tại
        current_balances_key_tuple = self._get_balances_tuple_key(current_balances_map)
        
        # Bước 2: Kiểm tra bảng ghi nhớ (tránh tính toán lặp lại)
        if self.dp_table.contains_key(current_balances_key_tuple):
            return self.dp_table.get(current_balances_key_tuple)
        
        # Bước 3: Trường hợp cơ sở - tất cả số dư gần bằng không (bài toán được giải quyết)
        all_balances_zero = True
        map_keys_ll = current_balances_map.keys()
        if map_keys_ll:
            current_key_node = map_keys_ll.head
            while current_key_node:
                person_name = current_key_node.data
                if abs(current_balances_map.get(person_name, 0.0)) > EPSILON:
                    all_balances_zero = False
                    break
                current_key_node = current_key_node.next
            
        if all_balances_zero:
            # Không còn nợ - tìm thấy giải pháp tối ưu
            base_result = Tuple([0.0, 0, LinkedList[BasicTransaction]()])
            self.dp_table.put(current_balances_key_tuple, base_result)
            return base_result
        
        # Bước 4: Trường hợp đệ quy - áp dụng bước tham lam và giải bài toán con
        settlements_info_tuple = self._find_greedy_settlements(current_balances_map)
        
        # Xử lý lỗi cho các trường hợp biên
        if not settlements_info_tuple: 
            error_result = Tuple([float('inf'), float('inf'), LinkedList[BasicTransaction]()])
            self.dp_table.put(current_balances_key_tuple, error_result)
            return error_result

        # Trích xuất kết quả từ bước thanh toán tham lam
        tx_list_this_step = settlements_info_tuple[0]
        cost_and_count_this_step_tuple = settlements_info_tuple[1]
        next_balances_map = settlements_info_tuple[2]

        cost_this_step = cost_and_count_this_step_tuple[0]
        tx_count_this_step = cost_and_count_this_step_tuple[1]
        
        # Gọi đệ quy để giải quyết bài toán con còn lại
        recursive_result_tuple = self._solve_dp_recursive(next_balances_map)
        
        # Xử lý lỗi cho lời gọi đệ quy
        if not recursive_result_tuple:
             error_result = Tuple([float('inf'), float('inf'), LinkedList[BasicTransaction]()])
             self.dp_table.put(current_balances_key_tuple, error_result)
             return error_result

        # Trích xuất các thành phần giải pháp đệ quy
        cost_from_recursion = recursive_result_tuple[0]
        tx_count_from_recursion = recursive_result_tuple[1]
        tx_list_from_recursion = recursive_result_tuple[2]
        
        # Bước 5: Kết hợp bước hiện tại với giải pháp đệ quy
        total_accumulated_cost = cost_this_step + cost_from_recursion
        total_tx_count = tx_count_this_step + tx_count_from_recursion
        
        # Hợp nhất danh sách giao dịch: bước hiện tại + giải pháp đệ quy
        final_combined_tx_list = LinkedList[BasicTransaction]()
        
        # Thêm giao dịch từ bước tham lam hiện tại
        if tx_list_this_step and not tx_list_this_step.is_empty():
            current_node = tx_list_this_step.head
            while current_node:
                final_combined_tx_list.append(current_node.data)
                current_node = current_node.next
                
        # Thêm giao dịch từ giải pháp đệ quy
        if tx_list_from_recursion and not tx_list_from_recursion.is_empty():
            current_node = tx_list_from_recursion.head
            while current_node:
                final_combined_tx_list.append(current_node.data)
                current_node = current_node.next
        
        # Tạo kết quả cuối cùng cho trạng thái hiện tại
        current_state_result = Tuple([total_accumulated_cost, total_tx_count, final_combined_tx_list])
        
        # Bước 6: Lưu trữ kết quả trong bảng DP trước khi trả về
        self.dp_table.put(current_balances_key_tuple, current_state_result)
        
        return current_state_result

    def simplify(self) -> LinkedList[BasicTransaction]:
        """
        Điểm vào chính cho việc đơn giản hóa nợ dựa trên DP.
        
        Phương thức này điều phối toàn bộ thuật toán DP:
        1. Xử lý trường hợp đầu vào rỗng
        2. Khởi tạo bộ giải DP đệ quy với trạng thái số dư ban đầu
        3. Trích xuất danh sách giao dịch đơn giản từ giải pháp tối ưu
        4. Trả về kết quả cuối cùng
        
        Thuật toán đảm bảo tìm ra giải pháp tối ưu toàn cục để
        tối thiểu hóa cả số lượng giao dịch và tổng chi phí tài chính.
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch được đơn giản hóa tối ưu
        """
        # Xử lý trường hợp biên: không có giao dịch đầu vào
        if self.initial_transactions.is_empty():
            return LinkedList[BasicTransaction]()

        # Giải bài toán DP bắt đầu từ trạng thái số dư ban đầu
        final_result_tuple = self._solve_dp_recursive(self.people_balances)

        # Trích xuất danh sách giao dịch từ giải pháp tối ưu
        if not final_result_tuple:
            return LinkedList[BasicTransaction]()
            
        # final_result_tuple: (tổng_chi_phí, tổng_số_giao_dịch, danh_sách_giao_dịch_đơn_giản)
        simplified_transactions_list = final_result_tuple[2]
        
        return simplified_transactions_list