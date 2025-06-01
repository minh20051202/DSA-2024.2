# Thuật toán Đơn giản hóa Nợ bằng Loại bỏ Chu trình
from __future__ import annotations

from src.core_type import BasicTransaction
from src.data_structures import LinkedList, Graph, HashTable, Array, Tuple
from src.utils.sorting import merge_sort_array
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

class DebtCycleSimplifier:
    """
    Thực hiện đơn giản hóa nợ bằng thuật toán loại bỏ chu trình tối ưu:
    - Phát hiện và loại bỏ các chu trình nợ có lợi trong đồ thị
    - Ưu tiên chu trình loại bỏ được nhiều giao dịch nhất
    - Áp dụng net settlement tối ưu cho giao dịch còn lại
    
    Thuật toán hoạt động theo 2 giai đoạn:
    1. Phase 1: Loại bỏ chu trình
       - Xây dựng đồ thị có hướng từ các giao dịch nợ
       - Tìm tất cả chu trình có lợi (có thể loại bỏ giao dịch)
       - Sắp xếp chu trình theo độ ưu tiên (số giao dịch loại bỏ, số tiền)
       - Áp dụng chu trình tốt nhất và lặp lại cho đến khi hết
    
    2. Phase 2: Net Settlement tối ưu
       - Tính số dư ròng cho từng người
       - Sử dụng thuật toán matching tham lam để tối thiểu hóa giao dịch
    
    Độ phức tạp thời gian: O((V+E) * C) với V = số người, E = số giao dịch, C = số chu trình
    Độ phức tạp không gian: O(V + E)
    """
    
    def __init__(self, transactions: LinkedList[BasicTransaction]):
        """
        Khởi tạo bộ đơn giản hóa nợ với danh sách giao dịch ban đầu.
        
        Tham số:
            transactions: Danh sách liên kết các giao dịch cơ bản cần đơn giản hóa
        """
        self.initial_transactions: LinkedList[BasicTransaction] = transactions
        self.simplified_transactions: LinkedList[BasicTransaction] = LinkedList()

    def _build_graph_from_list(self, tx_array: Array[BasicTransaction]) -> Graph[str, BasicTransaction]:
        """
        Xây dựng đồ thị nợ có hướng từ danh sách các giao dịch cơ bản.
        
        Trong đồ thị:
        - Đỉnh (vertex): đại diện cho mỗi người tham gia
        - Cạnh có hướng (directed edge): từ người nợ đến người cho vay
        - Trọng số của cạnh: số tiền nợ (BasicTransaction object)
        
        Tham số:
            tx_array: Mảng các giao dịch cần xây dựng đồ thị
            
        Trả về:
            Graph[str, BasicTransaction]: Đồ thị nợ có hướng với trọng số
        """
        debt_graph = Graph[str, BasicTransaction](is_directed=True)
        for tx in tx_array:
            # Chỉ thêm giao dịch có số tiền lớn hơn ngưỡng epsilon
            if tx.amount > EPSILON:
                debt_graph.add_vertex(tx.debtor)    # Thêm đỉnh người nợ
                debt_graph.add_vertex(tx.creditor)  # Thêm đỉnh người cho vay
                # Thêm cạnh có hướng từ người nợ đến người cho vay
                debt_graph.add_edge(tx.debtor, tx.creditor, tx)
        return debt_graph

    def _calculate_improved_cycle_score(self, cycle_edges: LinkedList) -> Tuple:
        """
        Tính điểm đánh giá chu trình dựa trên số giao dịch được loại bỏ hoàn toàn.
        
        Nguyên tắc tính điểm:
        - Ưu tiên 1: Số lượng giao dịch sẽ được loại bỏ hoàn toàn sau khi áp dụng chu trình
        - Ưu tiên 2: Số tiền nhỏ nhất trong chu trình (số tiền có thể loại bỏ)
        
        Tham số:
            cycle_edges: Danh sách các cạnh tạo thành chu trình
            
        Trả về:
            Tuple: (số_giao_dịch_được_loại_bỏ, số_tiền_nhỏ_nhất) hoặc (-1, 0.0) nếu không hợp lệ
        """
        # Kiểm tra điều kiện chu trình tối thiểu (ít nhất 2 cạnh)
        if len(cycle_edges) < 2:
            return Tuple([-1, 0.0])
        
        min_amount = float('inf')
        cycle_transactions = []
        
        # Thu thập thông tin chu trình
        for edge_node in cycle_edges:
            tx = edge_node.data
            # Kiểm tra tính hợp lệ của giao dịch
            if tx is None or tx.amount <= EPSILON:
                return Tuple([-1, 0.0])
            min_amount = min(min_amount, tx.amount)
            cycle_transactions.append(tx)
        
        # Kiểm tra tính hợp lệ của số tiền nhỏ nhất
        if min_amount == float('inf') or min_amount <= EPSILON:
            return Tuple([-1, 0.0])
        
        # Đếm số giao dịch sẽ được loại bỏ hoàn toàn
        transactions_eliminated = 0
        for tx in cycle_transactions:
            # Giao dịch được loại bỏ nếu số tiền bằng với số tiền nhỏ nhất
            if abs(tx.amount - min_amount) < EPSILON:
                transactions_eliminated += 1
        
        # Trả về tuple để so sánh: ưu tiên số giao dịch loại bỏ, sau đó đến số tiền
        return Tuple([transactions_eliminated, min_amount])

    def _find_all_profitable_cycles(self, debt_graph: Graph) -> LinkedList[Tuple]:
        """
        Tìm tất cả chu trình có lợi trong đồ thị nợ và sắp xếp theo độ ưu tiên.
        
        Chu trình có lợi: chu trình có thể loại bỏ ít nhất 1 giao dịch hoàn toàn
        
        Quy trình:
        1. Sử dụng thuật toán tìm chu trình trong đồ thị có hướng
        2. Đánh giá từng chu trình bằng hàm tính điểm
        3. Lọc ra các chu trình có lợi (điểm > 0)
        4. Sắp xếp theo độ ưu tiên giảm dần
        
        Tham số:
            debt_graph: Đồ thị nợ có hướng cần tìm chu trình
            
        Trả về:
            LinkedList[Tuple]: Danh sách chu trình có lợi đã sắp xếp
                             Mỗi phần tử: (score_tuple, cycle_edges, min_amount)
        """
        found_cycles_edges = debt_graph.find_cycles_with_edges()
        profitable_cycles = LinkedList[Tuple]()
        
        if found_cycles_edges.is_empty():
            return profitable_cycles
        
        # Đánh giá và lọc các chu trình có lợi
        for cycle_edges_ll_node in found_cycles_edges:
            score_tuple = self._calculate_improved_cycle_score(cycle_edges_ll_node)
            transactions_eliminated, min_amount = score_tuple[0], score_tuple[1]
            
            if transactions_eliminated > 0:  # Chu trình có lợi
                cycle_info = Tuple([score_tuple, cycle_edges_ll_node, min_amount])
                profitable_cycles.append(cycle_info)
        
        # Sắp xếp theo độ ưu tiên: ưu tiên số giao dịch loại bỏ cao nhất
        if not profitable_cycles.is_empty():
            profitable_cycles = self._sort_cycles_by_priority(profitable_cycles)
        
        return profitable_cycles

    def _sort_cycles_by_priority(self, cycles: LinkedList[Tuple]) -> LinkedList[Tuple]:
        """
        Sắp xếp các chu trình theo độ ưu tiên giảm dần.
        
        Tiêu chí sắp xếp (theo thứ tự ưu tiên):
        1. Số giao dịch được loại bỏ (giảm dần) - ưu tiên cao nhất
        2. Số tiền có thể loại bỏ (tăng dần) - ưu tiên thứ hai
        
        Tham số:
            cycles: Danh sách chu trình cần sắp xếp
            
        Trả về:
            LinkedList[Tuple]: Danh sách chu trình đã được sắp xếp theo độ ưu tiên
        """
        cycles_array = Array()
        for cycle_node in cycles:
            cycles_array.append(cycle_node)
        
        def cycle_comparator(cycle1, cycle2):
            """
            Hàm so sánh hai chu trình để xác định thứ tự ưu tiên.
            
            Trả về:
                bool: True nếu cycle1 có độ ưu tiên cao hơn cycle2
            """
            score1 = cycle1[0]
            score2 = cycle2[0]
            
            eliminated1, min_amount1 = score1[0], score1[1]
            eliminated2, min_amount2 = score2[0], score2[1]
            
            # Ưu tiên số giao dịch loại bỏ nhiều hơn
            if eliminated1 != eliminated2:
                return eliminated1 > eliminated2
            # Nếu bằng nhau, ưu tiên số tiền lớn hơn
            return min_amount1 > min_amount2
        
        sorted_array = merge_sort_array(cycles_array, comparator=cycle_comparator)
        
        sorted_cycles = LinkedList[Tuple]()
        for cycle in sorted_array:
            sorted_cycles.append(cycle)
        
        return sorted_cycles

    def _apply_cycle_elimination(self, cycle_edges: LinkedList, min_amount: float) -> Array[BasicTransaction]:
        """
        Áp dụng việc loại bỏ chu trình và trả về danh sách giao dịch được cập nhật.
        
        Quy trình loại bỏ chu trình:
        1. Giảm số tiền của tất cả giao dịch trong chu trình đi min_amount
        2. Loại bỏ các giao dịch có số tiền <= EPSILON (giao dịch đã được thanh toán)
        3. Trả về danh sách giao dịch còn lại
        
        Tham số:
            cycle_edges: Danh sách các cạnh trong chu trình cần loại bỏ
            min_amount: Số tiền nhỏ nhất trong chu trình (số tiền được loại bỏ)
            
        Trả về:
            Array[BasicTransaction]: Danh sách giao dịch sau khi áp dụng loại bỏ chu trình
        """
        # Cập nhật số tiền cho các giao dịch trong chu trình
        for edge_node in cycle_edges:
            tx = edge_node.data
            tx.amount -= min_amount
        
        # Thu thập tất cả giao dịch còn lại có số tiền > 0
        updated_tx_array = Array[BasicTransaction]()
        for tx_node in self.initial_transactions:
            tx = tx_node.data
            if tx.amount > EPSILON:
                updated_tx_array.append(tx)
        
        return updated_tx_array

    def _optimal_net_settlement(self, tx_array: Array[BasicTransaction]) -> LinkedList[BasicTransaction]:
        """
        Thực hiện net settlement tối ưu cho danh sách giao dịch còn lại.
        
        Net Settlement là quá trình:
        1. Tính số dư ròng của từng người (tổng cho vay - tổng nợ)
        2. Phân chia thành 2 nhóm: người nợ (số dư âm) và người cho vay (số dự dương)
        3. Sử dụng thuật toán matching tham lam để ghép đôi tối ưu
        4. Tạo ra số lượng giao dịch tối thiểu để cân bằng tất cả số dư
        
        Tham số:
            tx_array: Mảng các giao dịch cần thực hiện net settlement
            
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch tối ưu sau net settlement
        """
        # Tính số dư ròng
        net_balances: HashTable[str, float] = HashTable()
        
        for tx_item in tx_array:
            current_debtor_balance = net_balances.get(tx_item.debtor, 0.0)
            current_creditor_balance = net_balances.get(tx_item.creditor, 0.0)
            
            net_balances.put(tx_item.debtor, current_debtor_balance - tx_item.amount)
            net_balances.put(tx_item.creditor, current_creditor_balance + tx_item.amount)
        
        # Phân loại người nợ và người cho vay
        debtors_list = Array[str]()
        creditors_list = Array[str]()
        
        keys_ll = net_balances.keys()
        if keys_ll:
            current_key_node = keys_ll.head
            while current_key_node:
                person = current_key_node.data
                balance = net_balances.get(person)
                if balance < -EPSILON:  # Người nợ
                    debtors_list.append(person)
                elif balance > EPSILON:  # Người cho vay
                    creditors_list.append(person)
                current_key_node = current_key_node.next
        
        # Sắp xếp theo số dư tuyệt đối
        debtors_list = merge_sort_array(debtors_list, lambda a, b: abs(net_balances.get(a)) > abs(net_balances.get(b)))
        creditors_list = merge_sort_array(creditors_list, lambda a, b: net_balances.get(a) > net_balances.get(b))
        
        # Thực hiện matching tham lam
        result = LinkedList[BasicTransaction]()
        
        for i in range(len(debtors_list)):
            debtor = debtors_list.get(i)
            debtor_amount = abs(net_balances.get(debtor))
            
            for j in range(len(creditors_list)):
                if debtor_amount <= EPSILON:
                    break
                    
                creditor = creditors_list.get(j)
                creditor_amount = net_balances.get(creditor)
                
                if creditor_amount <= EPSILON:
                    continue
                
                transfer_amount = min(debtor_amount, creditor_amount)
                if transfer_amount > EPSILON:
                    result.append(BasicTransaction(
                        debtor=debtor,
                        creditor=creditor,
                        amount=round_money(transfer_amount)
                    ))
                    
                    debtor_amount -= transfer_amount
                    net_balances.put(creditor, creditor_amount - transfer_amount)
        
        return result

    def simplify(self) -> LinkedList[BasicTransaction]:
        """
        Thực hiện đơn giản hóa nợ hoàn chỉnh bằng thuật toán loại bỏ chu trình cải tiến.
        
        Thuật toán hoạt động theo 2 giai đoạn chính:
        
        Giai đoạn 1 - Loại bỏ chu trình có lợi:
        1. Chuyển đổi danh sách giao dịch thành mảng để xử lý hiệu quả
        2. Lặp cho đến khi không còn chu trình có lợi:
           a. Xây dựng đồ thị nợ từ giao dịch hiện tại
           b. Tìm tất cả chu trình có lợi và sắp xếp theo độ ưu tiên
           c. Áp dụng chu trình tốt nhất (loại bỏ nhiều giao dịch nhất)
           d. Cập nhật danh sách giao dịch và tiếp tục
        
        Giai đoạn 2 - Net settlement tối ưu:
        1. Tính số dư ròng cho tất cả người tham gia
        2. Sử dụng thuật toán matching tham lam để tạo giao dịch tối thiểu
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch đã được đơn giản hóa tối ưu
        """
        if self.initial_transactions.is_empty():
            return LinkedList[BasicTransaction]()

        # Chuyển đổi sang array để xử lý
        current_tx_array: Array[BasicTransaction] = Array()
        for tx_node_data in self.initial_transactions:
            current_tx_array.append(tx_node_data)

        iteration_count = 0
        max_iterations = min(len(current_tx_array) * 2, 50)  # Giới hạn số vòng lặp

        # Phase 1: Loại bỏ chu trình có lợi
        while iteration_count < max_iterations and len(current_tx_array) > 1:
            iteration_count += 1
            
            # Xây dựng đồ thị từ giao dịch hiện tại
            debt_graph = self._build_graph_from_list(current_tx_array)
            
            # Tìm chu trình có lợi nhất
            profitable_cycles = self._find_all_profitable_cycles(debt_graph)
            
            if profitable_cycles.is_empty():
                break  # Không còn chu trình có lợi
            
            # Áp dụng chu trình tốt nhất
            best_cycle_info = profitable_cycles.head.data
            _, cycle_edges, min_amount = best_cycle_info[0], best_cycle_info[1], best_cycle_info[2]
            
            # Áp dụng loại bỏ chu trình
            for edge_node in cycle_edges:
                tx = edge_node.data
                tx.amount -= min_amount
            
            # Cập nhật danh sách giao dịch
            updated_tx_array = Array[BasicTransaction]()
            for tx_in_array in current_tx_array:
                if tx_in_array.amount > EPSILON:
                    updated_tx_array.append(tx_in_array)
            
            current_tx_array = updated_tx_array

        # Phase 2: Net settlement tối ưu cho giao dịch còn lại
        self.simplified_transactions = self._optimal_net_settlement(current_tx_array)
        return self.simplified_transactions