# Thuật toán Min-Cost Max-Flow cho Đơn giản hóa Nợ Nâng cao
# Advanced Min-Cost Max-Flow Algorithm for Debt Simplification with Financial Calculations
from __future__ import annotations
from datetime import date
from typing import Any
from src.data_structures import Array, LinkedList, HashTable, Graph, GraphEdge, Tuple
from src.core_type import BasicTransaction, AdvancedTransaction
from src.utils.sorting import merge_sort_linked_list, merge_sort_array
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money
from src.utils.financial_calculator import FinancialCalculator, InterestType, PenaltyType

class AdvancedMinCostMaxFlowSimplifier:
    """
    Thực hiện đơn giản hóa nợ nâng cao bằng thuật toán Min-Cost Max-Flow với tính toán tài chính:
    - Xử lý AdvancedTransaction với lãi suất, phí phạt, ngày tháng
    - Tính toán số dư thực tế dựa trên ngày hiện tại
    - Sử dụng điểm ưu tiên để tối ưu hóa thứ tự thanh toán
    - Áp dụng SPFA để tìm đường tăng luồng với chi phí tối ưu
    
    Thuật toán hoạt động theo nguyên tắc:
    1. Tính toán tổng nợ thực tế của mỗi người (bao gồm lãi và phí phạt)
    2. Xây dựng mạng luồng với trọng số dựa trên điểm ưu tiên
    3. Tìm đường đi có chi phí nhỏ nhất và tăng luồng
    4. Trích xuất giao dịch tối ưu từ luồng cuối cùng
    
    Độ phức tạp thời gian: O(V²E²) với V = số đỉnh, E = số cạnh
    Độ phức tạp không gian: O(V + E)
    """
    
    # Hằng số định danh cho các đỉnh đặc biệt trong mạng luồng
    _S_NODE = "_SOURCE_"    
    _T_NODE = "_SINK_"      
    _INFINITY = float('inf')
    
    def __init__(self, 
                 transactions: LinkedList[AdvancedTransaction],
                 current_date: date,
                 interest_type: InterestType = InterestType.COMPOUND_DAILY,
                 penalty_type: PenaltyType = PenaltyType.FIXED):
        """
        Khởi tạo bộ đơn giản hóa Min-Cost Max-Flow nâng cao.
        
        Tham số:
            transactions: Danh sách giao dịch nâng cao cần đơn giản hóa
            current_date: Ngày hiện tại để tính toán lãi và phí phạt
            interest_type: Loại lãi suất (đơn, kép theo ngày/tháng/năm)
            penalty_type: Loại phí phạt (cố định, theo ngày, theo phần trăm)
        """
        self.initial_transactions = transactions
        self.current_date = current_date
        self.interest_type = interest_type
        self.penalty_type = penalty_type
        
        # Cấu trúc dữ liệu chính
        self.people_balances: HashTable[str, float] = HashTable()
        self.people_priorities: HashTable[str, float] = HashTable()  # Điểm ưu tiên của từng người
        self.transaction_details: HashTable[str, HashTable[str, float]] = HashTable()  # Chi tiết nợ giữa các cặp
        self.all_people: LinkedList[str] = LinkedList()
        self.flow_graph: Graph[str, None] | None = None
        
        self._calculate_advanced_balances()
    
    def _calculate_advanced_balances(self) -> None:
        """
        Tính toán số dư nâng cao với lãi suất, phí phạt và điểm ưu tiên.
        
        Quy trình:
        1. Duyệt qua tất cả giao dịch nâng cao
        2. Tính tổng nợ thực tế cho mỗi giao dịch (gốc + lãi + phí phạt)
        3. Tính điểm ưu tiên cho mỗi giao dịch
        4. Cập nhật số dư ròng cho mỗi người
        5. Lưu chi tiết nợ giữa các cặp người
        """
        people_set: HashTable[str, bool] = HashTable()
        
        # Khởi tạo bảng chi tiết giao dịch giữa các cặp
        current = self.initial_transactions.head
        while current:
            tx = current.data
            
            # Tính tổng nợ thực tế bao gồm lãi và phí phạt
            debt_breakdown = FinancialCalculator.calculate_total_debt(
                amount=tx.amount,
                interest_rate=tx.interest_rate,
                penalty_rate=tx.penalty_rate,
                borrow_date=tx.borrow_date,
                due_date=tx.due_date,
                current_date=self.current_date,
                interest_type=tx.interest_type,
                penalty_type=tx.penalty_type
            )
            
            total_debt = debt_breakdown['total']
            
            # Tính điểm ưu tiên cho giao dịch này
            priority_score = FinancialCalculator.calculate_priority_score(
                principal=tx.amount,
                interest_rate=tx.interest_rate,
                penalty_rate=tx.penalty_rate,
                borrow_date=tx.borrow_date,
                due_date=tx.due_date,
                current_date=self.current_date,
                interest_type=tx.interest_type,
                penalty_type=tx.penalty_type
            )
            
            # Cập nhật số dư cho từng người
            debtor_balance = self.people_balances.get(tx.debtor, 0.0)
            creditor_balance = self.people_balances.get(tx.creditor, 0.0)
            
            self.people_balances.put(tx.debtor, debtor_balance - total_debt)
            self.people_balances.put(tx.creditor, creditor_balance + total_debt)
            
            # Cập nhật điểm ưu tiên tích lũy cho từng người
            debtor_priority = self.people_priorities.get(tx.debtor, 0.0)
            creditor_priority = self.people_priorities.get(tx.creditor, 0.0)
            
            self.people_priorities.put(tx.debtor, debtor_priority + priority_score)
            self.people_priorities.put(tx.creditor, creditor_priority + priority_score)
            
            # Lưu chi tiết nợ giữa cặp người này
            self._update_transaction_details(tx.debtor, tx.creditor, total_debt, priority_score)
            
            # Thêm vào tập hợp người tham gia
            people_set.put(tx.debtor, True)
            people_set.put(tx.creditor, True)
            
            current = current.next
        
        # Chuyển đổi tập hợp thành danh sách và sắp xếp
        people_keys = people_set.keys()
        if people_keys:
            self.all_people = merge_sort_linked_list(
                people_keys, 
                comparator=lambda a, b: a < b
            )

    def _update_transaction_details(self, debtor: str, creditor: str, 
                                  total_debt: float, priority_score: float) -> None:
        """
        Cập nhật chi tiết giao dịch giữa hai người.
        
        Tham số:
            debtor: Người nợ
            creditor: Người cho vay
            total_debt: Tổng số nợ thực tế
            priority_score: Điểm ưu tiên của giao dịch
        """
        # Tạo key duy nhất cho cặp người
        pair_key = f"{debtor}->{creditor}"
        
        # Lấy chi tiết hiện tại hoặc tạo mới
        current_details = self.transaction_details.get(pair_key, HashTable())
        
        # Cập nhật tổng nợ và điểm ưu tiên
        existing_debt = current_details.get('total_debt', 0.0)
        existing_priority = current_details.get('priority_score', 0.0)
        
        current_details.put('total_debt', existing_debt + total_debt)
        current_details.put('priority_score', existing_priority + priority_score)
        current_details.put('avg_priority', 
                           (existing_priority + priority_score) / 2 if existing_priority > 0 else priority_score)
        
        self.transaction_details.put(pair_key, current_details)
    
    def _build_flow_network(self) -> None:
        """
        Xây dựng mạng luồng nâng cao với trọng số dựa trên điểm ưu tiên.
        
        Cấu trúc mạng luồng:
        1. Source -> Người nợ (capacity = tổng nợ, cost = 0)
        2. Người cho vay -> Sink (capacity = tổng cho vay, cost = 0)  
        3. Người nợ -> Người cho vay (capacity = min flow, cost = 1/priority_score)
        
        Cost ngược với điểm ưu tiên để ưu tiên xử lý giao dịch quan trọng trước.
        """
        self.flow_graph = Graph[str, None](is_directed=True)
        g = self.flow_graph
        
        # Thêm các đỉnh đặc biệt
        g.add_vertex(self._S_NODE)
        g.add_vertex(self._T_NODE)
        
        # Thêm tất cả người tham gia
        current = self.all_people.head
        while current:
            g.add_vertex(current.data)
            current = current.next
        
        # Tính tổng nợ và tổng cho vay
        total_debt = 0.0
        total_credit = 0.0
        
        current = self.all_people.head
        while current:
            person = current.data
            balance = self.people_balances.get(person, 0.0)
            
            if balance < -EPSILON:  # Người nợ
                debt_amount = abs(balance)
                total_debt += debt_amount
                self._add_edge_with_reverse(self._S_NODE, person, debt_amount, 0)
                
            elif balance > EPSILON:  # Người cho vay
                total_credit += balance
                self._add_edge_with_reverse(person, self._T_NODE, balance, 0)
            
            current = current.next
        
        # Thêm cạnh giữa các người với cost dựa trên priority
        max_flow_per_edge = min(total_debt, total_credit)
        
        p1_node = self.all_people.head
        while p1_node:
            p1 = p1_node.data
            p1_balance = self.people_balances.get(p1, 0.0)
            
            if p1_balance < -EPSILON:  # p1 là người nợ
                p2_node = self.all_people.head
                while p2_node:
                    p2 = p2_node.data
                    p2_balance = self.people_balances.get(p2, 0.0)
                    
                    if p1 != p2 and p2_balance > EPSILON:  # p2 là người cho vay
                        # Tính capacity và cost cho cạnh này
                        capacity = min(abs(p1_balance), p2_balance, max_flow_per_edge)
                        
                        # Tính cost dựa trên điểm ưu tiên
                        cost = self._calculate_edge_cost(p1, p2)
                        
                        self._add_edge_with_reverse(p1, p2, capacity, cost)
                    
                    p2_node = p2_node.next
            p1_node = p1_node.next
    
    def _calculate_edge_cost(self, debtor: str, creditor: str) -> float:
        """
        Tính cost cho cạnh dựa trên chi tiết giao dịch và điểm ưu tiên.
        
        Tham số:
            debtor: Người nợ
            creditor: Người cho vay
            
        Trả về:
            float: Cost cho cạnh (càng thấp càng được ưu tiên)
        """
        pair_key = f"{debtor}->{creditor}"
        transaction_detail = self.transaction_details.get(pair_key)
        
        if transaction_detail:
            # Nếu có giao dịch trực tiếp, ưu tiên cao (cost thấp)
            priority_score = transaction_detail.get('avg_priority', 1.0)
            # Cost ngược với priority: priority cao -> cost thấp
            base_cost = max(0.1, 1.0 / max(priority_score, 1.0))
        else:
            # Nếu không có giao dịch trực tiếp, cost cao hơn
            debtor_priority = self.people_priorities.get(debtor, 1.0)
            creditor_priority = self.people_priorities.get(creditor, 1.0)
            avg_priority = (debtor_priority + creditor_priority) / 2
            base_cost = max(1.0, 10.0 / max(avg_priority, 1.0))
        
        return round_money(base_cost)
    
    def _add_edge_with_reverse(self, from_node: str, to_node: str, 
                              capacity: float, cost: float) -> None:
        """
        Thêm cạnh thuận và cạnh ngược cho mạng luồng.
        
        Tham số:
            from_node: Đỉnh nguồn
            to_node: Đỉnh đích
            capacity: Khả năng thông qua
            cost: Chi phí cho mỗi đơn vị luồng
        """
        if not self.flow_graph:
            return
            
        from_vertex = self.flow_graph.get_vertex(from_node)
        to_vertex = self.flow_graph.get_vertex(to_node)
        
        if from_vertex and to_vertex:
            # Cạnh thuận
            forward_edge = from_vertex.add_edge(to_node, None, capacity=capacity, cost=cost)
            # Cạnh ngược
            reverse_edge = to_vertex.add_edge(from_node, None, capacity=0, cost=-cost)
            
            # Liên kết hai cạnh
            if forward_edge and reverse_edge:
                forward_edge.reverse_edge = reverse_edge
                reverse_edge.reverse_edge = forward_edge
    
    def _find_shortest_path_spfa(self) -> Tuple[LinkedList[GraphEdge[str, None]], float] | None:
        """
        Tìm đường đi ngắn nhất từ Source đến Sink bằng thuật toán SPFA.
        
        Trả về:
            Tuple chứa đường đi và khả năng luồng tối thiểu, hoặc None nếu không tìm thấy
        """
        if not self.flow_graph:
            return None
        
        # Khởi tạo cấu trúc dữ liệu cho SPFA
        distances: HashTable[str, float] = HashTable()
        parent_edge: HashTable[str, GraphEdge[str, None]] = HashTable()
        in_queue: HashTable[str, bool] = HashTable()
        queue: LinkedList[str] = LinkedList()
        
        # Khởi tạo khoảng cách
        current = self.all_people.head
        while current:
            distances.put(current.data, self._INFINITY)
            current = current.next
        distances.put(self._S_NODE, self._INFINITY)
        distances.put(self._T_NODE, self._INFINITY)
        
        # Bắt đầu từ source
        distances.put(self._S_NODE, 0.0)
        queue.append(self._S_NODE)
        in_queue.put(self._S_NODE, True)
        
        # Thuật toán SPFA
        while not queue.is_empty():
            u = queue.remove_first()
            in_queue.put(u, False)
            
            u_vertex = self.flow_graph.get_vertex(u)
            if not u_vertex or not u_vertex.edges:
                continue
            
            edge_node = u_vertex.edges.head
            while edge_node:
                edge = edge_node.data
                v = edge.destination
                
                residual_cap = (edge.capacity or 0) - edge.flow
                if residual_cap > EPSILON:
                    u_dist = distances.get(u, self._INFINITY)
                    v_dist = distances.get(v, self._INFINITY)
                    edge_cost = edge.cost or 0
                    
                    if u_dist + edge_cost < v_dist:
                        distances.put(v, u_dist + edge_cost)
                        parent_edge.put(v, edge)
                        
                        if not in_queue.get(v, False):
                            queue.append(v)
                            in_queue.put(v, True)
                
                edge_node = edge_node.next
        
        # Kiểm tra đường đi đến sink
        if distances.get(self._T_NODE, self._INFINITY) >= self._INFINITY:
            return None
        
        # Truy vết đường đi
        path_edges: LinkedList[GraphEdge[str, None]] = LinkedList()
        min_capacity = self._INFINITY
        current_node = self._T_NODE
        
        while current_node != self._S_NODE:
            edge = parent_edge.get(current_node)
            if not edge:
                return None
            
            path_edges.prepend(edge)
            residual_cap = (edge.capacity or 0) - edge.flow
            min_capacity = min(min_capacity, residual_cap)
            current_node = edge.source
        
        return Tuple([path_edges, min_capacity])
    
    def simplify(self) -> LinkedList[BasicTransaction]:
        """
        Thực hiện đơn giản hóa nợ nâng cao.
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch đã được đơn giản hóa
        """
        if self.initial_transactions.is_empty():
            return LinkedList()
        
        # Xây dựng mạng luồng
        self._build_flow_network()
        if not self.flow_graph:
            return LinkedList()
        
        # Vòng lặp chính - tìm và tăng luồng
        while True:
            path_result = self._find_shortest_path_spfa()
            if not path_result:
                break
            
            path_edges, flow_amount = path_result[0], path_result[1]
            
            # Tính chi phí đường đi
            path_cost = 0.0
            edge_node = path_edges.head
            while edge_node:
                edge = edge_node.data
                path_cost += (edge.cost or 0) * flow_amount
                edge_node = edge_node.next
            
            # Cập nhật luồng
            edge_node = path_edges.head
            while edge_node:
                edge = edge_node.data
                edge.flow += flow_amount
                if edge.reverse_edge:
                    edge.reverse_edge.flow -= flow_amount
                edge_node = edge_node.next

        return self._extract_transactions()
    
    def _extract_transactions(self) -> LinkedList[BasicTransaction]:
        """
        Trích xuất các giao dịch từ đồ thị luồng với tổng tiền khớp tuyệt đối.
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch được trích xuất
        """
        raw_transactions: HashTable[Tuple[str, str], float] = HashTable()
        person_node = self.all_people.head
        total_flow = 0.0

        # Bước 1: Tính tổng luồng thực tế giữa các cặp người
        # (Giữ nguyên logic này)
        while person_node:
            debtor = person_node.data
            person_vertex = self.flow_graph.get_vertex(debtor)
            if person_vertex and person_vertex.edges:
                edge_node = person_vertex.edges.head
                while edge_node:
                    edge = edge_node.data
                    creditor = edge.destination
                    if edge.flow > EPSILON and creditor != self._S_NODE and creditor != self._T_NODE:
                        key = Tuple([debtor, creditor])
                        existing = raw_transactions.get(key, 0.0)
                        raw_transactions.put(key, existing + edge.flow)
                        total_flow += edge.flow
                    edge_node = edge_node.next
            person_node = person_node.next

        # Bước 2: Làm tròn từng giao dịch, theo dõi sai số
        rounded_transactions = LinkedList[BasicTransaction]()
        rounded_total = 0.0
        
        # Khởi tạo temp_list là Array của bạn
        # temp_list sẽ chứa các tuple: (name_from, name_to, original_amount, rounded_amount)
        temp_list: Array[Tuple[str, str, float, float]] = Array() # Type hint rõ ràng hơn

        for key in raw_transactions: # Giả sử raw_transactions.keys() hoạt động hoặc bạn có cách lặp khác
            # Nếu raw_transactions là HashTable tự định nghĩa, bạn có thể cần:
            # for key_node in raw_transactions.keys():
            #    key = key_node.data # Hoặc cách bạn lấy key
            #    amount = raw_transactions.get(key)
            # Hoặc nếu HashTable của bạn hỗ trợ __iter__ trả về key:
            amount = raw_transactions.get(key)
            if amount is None: continue # Bỏ qua nếu không lấy được amount

            rounded = round_money(amount)
            rounded_total += rounded
            # temp_list.append(value=(key[0], key[1], amount, rounded)) # Giả sử key là Tuple[str,str]
            # Để an toàn hơn với key từ HashTable, nếu key là đối tượng Tuple của bạn:
            name_from = key[0]  # Truy cập phần tử đầu tiên của Tuple key
            name_to = key[1]
            temp_list.append(value=(name_from, name_to, amount, rounded))


        # Bước 3: Tính sai số cần phân bổ
        delta = round_money(total_flow) - rounded_total

        # SỬA ĐỔI Ở ĐÂY: Sử dụng merge_sort_array của bạn
        # Mã gốc gây lỗi:
        # temp_list.sort(key=lambda x: x[2] - x[3], reverse=(delta > 0))

        # Mã sửa đổi:
        # Tạo hàm so sánh dựa trên logic của key và reverse
        def sort_key_for_delta_distribution(item_tuple: Tuple[str, str, float, float]) -> float:
            # item_tuple là (name_from, name_to, original_amount, rounded_amount)
            return item_tuple[2] - item_tuple[3] # original_amount - rounded_amount

        # Hàm so sánh cho merge_sort_array
        # comparator(a, b) trả về True nếu a nên đứng trước b (ví dụ: a < b cho tăng dần)
        if delta > 0: # reverse=True => Sắp xếp giảm dần theo key
            # Nếu delta > 0, muốn ưu tiên những cái có (original - rounded) LỚN NHẤT
            # => sắp xếp giảm dần theo (original - rounded)
            # => comparator(a,b) là True nếu (key(a) > key(b))
            delta_comparator = lambda item_a, item_b: sort_key_for_delta_distribution(item_a) > sort_key_for_delta_distribution(item_b)
        else: # reverse=False (hoặc delta <= 0) => Sắp xếp tăng dần theo key
            # Nếu delta <= 0, muốn ưu tiên những cái có (original - rounded) NHỎ NHẤT (có thể âm)
            # => sắp xếp tăng dần theo (original - rounded)
            # => comparator(a,b) là True nếu (key(a) < key(b))
            delta_comparator = lambda item_a, item_b: sort_key_for_delta_distribution(item_a) < sort_key_for_delta_distribution(item_b)
        
        if len(temp_list) > 0 : # Chỉ sắp xếp nếu có phần tử
            temp_list = merge_sort_array(temp_list, comparator=delta_comparator)
        # Lưu ý: merge_sort_array của bạn trả về một Array MỚI đã sắp xếp.
        # Bạn cần gán lại nó cho temp_list.

        # Phân phối sai số (mỗi bước = 0.01)
        i = 0
        # Kiểm tra len(temp_list) > 0 trước khi truy cập để tránh lỗi nếu rỗng
        while abs(delta) >= 0.009 and len(temp_list) > 0:
            # Giả sử Array có phương thức get(index) và set_at_index(index, value)
            current_item_tuple = temp_list.get(i)
            name_from, name_to, amt, rounded_amt = current_item_tuple[0], current_item_tuple[1], current_item_tuple[2], current_item_tuple[3]
            
            corrected_amt = rounded_amt + (0.01 if delta > 0 else -0.01)
            
            # Cập nhật lại phần tử trong temp_list
            temp_list.set(i, (name_from, name_to, amt, corrected_amt))

            delta -= (0.01 if delta > 0 else -0.01)
            i = (i + 1) % len(temp_list)

        # Bước 4: Tạo LinkedList kết quả cuối cùng
        # Lặp qua Array bằng chỉ số nếu nó không hỗ trợ __iter__ trực tiếp
        for idx in range(len(temp_list)):
            item_data = temp_list.get(idx) # Giả sử có phương thức get(index)
            name_from, name_to, _, final_amt = item_data[0], item_data[1], item_data[2], item_data[3]
            
            if final_amt > EPSILON:
                rounded_transactions.append(BasicTransaction(
                    debtor=name_from,
                    creditor=name_to,
                    amount=round_money(final_amt)
                ))

        return rounded_transactions