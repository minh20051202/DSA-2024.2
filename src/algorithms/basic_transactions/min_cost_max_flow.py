# Thuật toán Min-Cost Max-Flow cho Đơn giản hóa Nợ
from __future__ import annotations
from src.data_structures import LinkedList, HashTable, Graph, GraphEdge, Tuple
from src.core_type import BasicTransaction
from src.utils.sorting import merge_sort_linked_list
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

class MinCostMaxFlowSimplifier:
    """
    Thực hiện đơn giản hóa nợ bằng thuật toán Min-Cost Max-Flow tối ưu:
    - Xây dựng mạng luồng có hướng với source và sink
    - Sử dụng SPFA (Shortest Path Faster Algorithm) tìm đường tăng luồng
    - Tối thiểu hóa chi phí tổng thể trong khi tối đa hóa luồng
    
    Thuật toán hoạt động theo nguyên tắc:
    1. Tính toán số dư ròng của mỗi người (tổng nợ - tổng cho vay)
    2. Xây dựng mạng luồng: Source -> Người nợ -> Người cho vay -> Sink
    3. Tìm đường đi có chi phí nhỏ nhất và tăng luồng trên đường đó
    4. Lặp lại cho đến khi không tìm được đường tăng luồng nào
    5. Trích xuất giao dịch từ luồng cuối cùng
    
    Độ phức tạp thời gian: O(V²E²) với V = số đỉnh, E = số cạnh
    Độ phức tạp không gian: O(V + E)
    """
    
    # Hằng số định danh cho các đỉnh đặc biệt trong mạng luồng
    _S_NODE = "_SOURCE_"    # Đỉnh nguồn (source) - cung cấp luồng ban đầu
    _T_NODE = "_SINK_"      # Đỉnh đích (sink) - thu thập luồng cuối cùng
    _INFINITY = float('inf') # Giá trị vô cực cho khởi tạo khoảng cách
    
    def __init__(self, transactions: LinkedList[BasicTransaction]):
        """
        Khởi tạo bộ đơn giản hóa Min-Cost Max-Flow với danh sách giao dịch ban đầu.
        
        Tham số:
            transactions: Danh sách liên kết các giao dịch cơ bản cần đơn giản hóa
        """
        self.initial_transactions = transactions              # Lưu trữ giao dịch gốc để tham chiếu
        self.people_balances: HashTable[str, float] = HashTable()  # Bảng băm lưu số dư của từng người
        self.all_people: LinkedList[str] = LinkedList()      # Danh sách tất cả người tham gia
        self.flow_graph: Graph[str, None] | None = None      # Mạng luồng cho thuật toán
        self._calculate_balances()                            # Tính toán số dư ban đầu
    
    def _calculate_balances(self) -> None:
        """
        Tính toán số dư ròng cho mỗi người từ tất cả giao dịch và xây dựng danh sách người tham gia.
        
        Quy tắc tính toán:
        - Người nợ (debtor): số dư giảm theo số tiền nợ (-amount)
        - Người cho vay (creditor): số dư tăng theo số tiền cho vay (+amount)
        
        Sử dụng HashTable để theo dõi người duy nhất và LinkedList để lưu danh sách.
        Cuối cùng sắp xếp danh sách người để đảm bảo tính nhất quán.
        """
        people_set: HashTable[str, bool] = HashTable()  # Set tạm để lưu người duy nhất
        
        # Duyệt qua tất cả giao dịch để tính số dư và thu thập danh sách người
        current = self.initial_transactions.head
        while current:
            tx = current.data
            
            # Cập nhật số dư cho người nợ (trừ đi số tiền nợ)
            debtor_balance = self.people_balances.get(tx.debtor, 0.0)
            creditor_balance = self.people_balances.get(tx.creditor, 0.0)
            
            self.people_balances.put(tx.debtor, debtor_balance - tx.amount)
            self.people_balances.put(tx.creditor, creditor_balance + tx.amount)
            
            # Thêm vào tập hợp người tham gia (tự động loại bỏ trùng lặp)
            people_set.put(tx.debtor, True)
            people_set.put(tx.creditor, True)
            
            current = current.next
        
        # Chuyển đổi tập hợp thành danh sách và sắp xếp để đảm bảo tính xác định
        people_keys = people_set.keys()
        if people_keys:
            self.all_people = merge_sort_linked_list(
                people_keys, 
                comparator=lambda a, b: a < b  # Sắp xếp theo thứ tự từ điển
            )
    
    def _build_flow_network(self) -> None:
        """
        Xây dựng mạng luồng Min-Cost Max-Flow với cấu trúc:
        Source -> Người nợ -> Người cho vay -> Sink
        
        Cấu trúc mạng luồng:
        1. Source kết nối với mỗi người nợ (capacity = số tiền nợ, cost = 0)
        2. Mỗi người cho vay kết nối với Sink (capacity = số tiền cho vay, cost = 0)
        3. Mỗi người nợ kết nối với mỗi người cho vay (capacity = min flow, cost = 1)
        
        Việc thiết lập cost = 1 cho cạnh giữa người giúp tối thiểu hóa số giao dịch.
        """
        self.flow_graph = Graph[str, None](is_directed=True)  # Tạo đồ thị có hướng
        g = self.flow_graph
        
        # Bước 1: Thêm các đỉnh đặc biệt (source và sink)
        g.add_vertex(self._S_NODE)
        g.add_vertex(self._T_NODE)
        
        # Bước 2: Thêm tất cả người tham gia vào đồ thị
        current = self.all_people.head
        while current:
            g.add_vertex(current.data)
            current = current.next
        
        # Bước 3: Tính tổng nợ và tổng cho vay để kiểm tra cân bằng và thiết lập capacity
        total_debt = 0.0      # Tổng số tiền nợ (giá trị dương)
        total_credit = 0.0    # Tổng số tiền cho vay (giá trị dương)
        
        current = self.all_people.head
        while current:
            person = current.data
            balance = self.people_balances.get(person, 0.0)
            
            if balance < -EPSILON:  # Người nợ (số dư âm)
                total_debt += abs(balance)
                # Tạo cạnh từ Source đến người nợ với capacity = số tiền nợ
                self._add_edge_with_reverse(self._S_NODE, person, abs(balance), 0)
                
            elif balance > EPSILON:  # Người cho vay (số dư dương)
                total_credit += balance
                # Tạo cạnh từ người cho vay đến Sink với capacity = số tiền cho vay
                self._add_edge_with_reverse(person, self._T_NODE, balance, 0)
            
            current = current.next
        
        # Bước 4: Thêm cạnh giữa các người với capacity hợp lý
        # Capacity tối đa cho mỗi cạnh = min(total_debt, total_credit)
        max_flow_per_edge = min(total_debt, total_credit)
        
        # Duyệt qua tất cả cặp người để tạo cạnh từ người nợ đến người cho vay
        p1_node = self.all_people.head
        while p1_node:
            p1 = p1_node.data
            p1_balance = self.people_balances.get(p1, 0.0)
            
            p2_node = self.all_people.head
            while p2_node:
                p2 = p2_node.data
                p2_balance = self.people_balances.get(p2, 0.0)
                
                # Chỉ tạo cạnh từ người nợ đến người cho vay (không tự giao dịch)
                if p1 != p2 and p1_balance < -EPSILON and p2_balance > EPSILON:
                    # Capacity = min(khả năng trả nợ, khả năng nhận tiền, max_flow)
                    capacity = min(abs(p1_balance), p2_balance, max_flow_per_edge)
                    self._add_edge_with_reverse(p1, p2, capacity, 1)  # cost = 1 để tối thiểu hóa số giao dịch
                
                p2_node = p2_node.next
            p1_node = p1_node.next
    
    def _add_edge_with_reverse(self, from_node: str, to_node: str, capacity: float, cost: float) -> None:
        """
        Thêm cạnh thuận và cạnh ngược cho mạng luồng (theo yêu cầu của thuật toán flow).
        
        Tham số:
            from_node: Đỉnh nguồn của cạnh
            to_node: Đỉnh đích của cạnh  
            capacity: Khả năng thông qua tối đa của cạnh
            cost: Chi phí cho mỗi đơn vị luồng đi qua cạnh
            
        Cạnh thuận: capacity = capacity, cost = cost
        Cạnh ngược: capacity = 0 (ban đầu), cost = -cost (để hủy luồng nếu cần)
        """
        if not self.flow_graph:
            return
            
        from_vertex = self.flow_graph.get_vertex(from_node)
        to_vertex = self.flow_graph.get_vertex(to_node)
        
        if from_vertex and to_vertex:
            # Tạo cạnh thuận (forward edge)
            forward_edge = from_vertex.add_edge(to_node, None, capacity=capacity, cost=cost)
            # Tạo cạnh ngược (reverse edge) với capacity = 0 và cost âm
            reverse_edge = to_vertex.add_edge(from_node, None, capacity=0, cost=-cost)
            
            # Liên kết hai cạnh với nhau để dễ dàng cập nhật luồng
            if forward_edge and reverse_edge:
                forward_edge.reverse_edge = reverse_edge
                reverse_edge.reverse_edge = forward_edge
    
    def _find_shortest_path_spfa(self) -> Tuple[LinkedList[GraphEdge[str, None]], float] | None:
        """
        Tìm đường đi ngắn nhất từ Source đến Sink bằng thuật toán SPFA.
        SPFA (Shortest Path Faster Algorithm) là cải tiến của Bellman-Ford.
        
        Trả về:
            Tuple chứa:
            - LinkedList[GraphEdge]: Danh sách các cạnh tạo thành đường đi ngắn nhất
            - float: Khả năng luồng tối thiểu trên đường đi (bottleneck capacity)
            Hoặc None nếu không tìm thấy đường đi
            
        Thuật toán SPFA:
        1. Khởi tạo khoảng cách từ source đến tất cả đỉnh = ∞
        2. Đặt khoảng cách đến source = 0 và thêm source vào queue
        3. Lặp cho đến khi queue rỗng:
           - Lấy đỉnh u từ queue
           - Duyệt tất cả cạnh từ u với residual capacity > 0
           - Nếu tìm được đường đi ngắn hơn, cập nhật và thêm vào queue
        4. Truy vết đường đi từ sink về source
        """
        if not self.flow_graph:
            return None
        
        # Bước 1: Khởi tạo cấu trúc dữ liệu cho SPFA
        distances: HashTable[str, float] = HashTable()          # Khoảng cách ngắn nhất từ source
        parent_edge: HashTable[str, GraphEdge[str, None]] = HashTable()  # Cạnh cha để truy vết đường đi
        in_queue: HashTable[str, bool] = HashTable()            # Đánh dấu đỉnh có trong queue không
        
        queue: LinkedList[str] = LinkedList()                   # Queue cho thuật toán SPFA
        
        # Bước 2: Khởi tạo tất cả khoảng cách là vô cực
        current = self.all_people.head
        while current:
            distances.put(current.data, self._INFINITY)
            current = current.next
        distances.put(self._S_NODE, self._INFINITY)
        distances.put(self._T_NODE, self._INFINITY)
        
        # Bước 3: Bắt đầu từ source với khoảng cách = 0
        distances.put(self._S_NODE, 0.0)
        queue.append(self._S_NODE)
        in_queue.put(self._S_NODE, True)
        
        # Bước 4: Thuật toán SPFA chính
        while not queue.is_empty():
            u = queue.remove_first()                            # Lấy đỉnh đầu tiên từ queue
            in_queue.put(u, False)                              # Đánh dấu đỉnh không còn trong queue
            
            u_vertex = self.flow_graph.get_vertex(u)
            if not u_vertex or not u_vertex.edges:
                continue
            
            # Duyệt tất cả cạnh xuất phát từ đỉnh u
            edge_node = u_vertex.edges.head
            while edge_node:
                edge = edge_node.data
                v = edge.destination
                
                # Kiểm tra residual capacity (khả năng còn lại của cạnh)
                residual_cap = (edge.capacity or 0) - edge.flow
                if residual_cap > EPSILON:  # Chỉ xét cạnh còn khả năng thông qua
                    u_dist = distances.get(u, self._INFINITY)
                    v_dist = distances.get(v, self._INFINITY)
                    edge_cost = edge.cost or 0
                    
                    # Relaxation: cập nhật khoảng cách nếu tìm được đường ngắn hơn
                    if u_dist + edge_cost < v_dist:
                        distances.put(v, u_dist + edge_cost)
                        parent_edge.put(v, edge)               # Lưu cạnh cha để truy vết
                        
                        # Thêm đỉnh v vào queue nếu chưa có
                        if not in_queue.get(v, False):
                            queue.append(v)
                            in_queue.put(v, True)
                
                edge_node = edge_node.next
        
        # Bước 5: Kiểm tra xem có đường đi đến sink không
        if distances.get(self._T_NODE, self._INFINITY) >= self._INFINITY:
            return None  # Không tìm thấy đường đi
        
        # Bước 6: Truy vết đường đi từ sink về source
        path_edges: LinkedList[GraphEdge[str, None]] = LinkedList()
        min_capacity = self._INFINITY                           # Khả năng luồng tối thiểu trên đường đi
        current_node = self._T_NODE
        
        while current_node != self._S_NODE:
            edge = parent_edge.get(current_node)
            if not edge:
                return None  # Lỗi trong quá trình truy vết
            
            path_edges.prepend(edge)                            # Thêm vào đầu để có thứ tự đúng
            residual_cap = (edge.capacity or 0) - edge.flow
            min_capacity = min(min_capacity, residual_cap)      # Cập nhật bottleneck capacity
            current_node = edge.source                          # Di chuyển về đỉnh cha
        
        return Tuple([path_edges, min_capacity])
    
    def simplify(self) -> LinkedList[BasicTransaction]:
        """
        Thực hiện đơn giản hóa nợ bằng thuật toán Min-Cost Max-Flow.
        
        Quy trình thực hiện:
        1. Kiểm tra điều kiện dừng (danh sách giao dịch rỗng)
        2. Xây dựng mạng luồng từ danh sách giao dịch ban đầu
        3. Lặp tìm đường tăng luồng có chi phí nhỏ nhất bằng SPFA
        4. Cập nhật luồng trên đường đi tìm được
        5. Lặp lại cho đến khi không còn đường tăng luồng
        6. Trích xuất giao dịch từ luồng cuối cùng
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch đã được đơn giản hóa
        """
        # Điều kiện dừng: nếu không có giao dịch nào thì trả về danh sách rỗng
        if self.initial_transactions.is_empty():
            return LinkedList()
        
        # Bước 1: Xây dựng mạng luồng
        self._build_flow_network()
        if not self.flow_graph:
            return LinkedList()
        
        total_cost = 0.0       # Tổng chi phí tích lũy
        
        # Bước 2: Vòng lặp chính - tìm và tăng luồng
        while True:
            # Tìm đường đi có chi phí nhỏ nhất từ source đến sink
            path_result = self._find_shortest_path_spfa()
            if not path_result:
                break  # Không còn đường tăng luồng
            
            path_edges, flow_amount = path_result[0], path_result[1]
            
            # Tính chi phí của đường đi này
            path_cost = 0.0
            edge_node = path_edges.head
            while edge_node:
                edge = edge_node.data
                path_cost += (edge.cost or 0) * flow_amount
                edge_node = edge_node.next
            
            total_cost += path_cost
            
            
            # Bước 3: Cập nhật luồng trên đường đi
            edge_node = path_edges.head
            while edge_node:
                edge = edge_node.data
                edge.flow += flow_amount                        # Tăng luồng trên cạnh thuận
                if edge.reverse_edge:
                    edge.reverse_edge.flow -= flow_amount       # Giảm luồng trên cạnh ngược
                edge_node = edge_node.next

        return self._extract_transactions()
    
    def _extract_transactions(self) -> LinkedList[BasicTransaction]:
        """
        Trích xuất các giao dịch từ đồ thị luồng.
        
        Quy trình:
        1. Duyệt qua tất cả đỉnh (người tham gia)
        2. Với mỗi đỉnh, xét các cạnh có luồng dương
        3. Tạo giao dịch từ luồng trên cạnh
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch được trích xuất
        """
        transactions = LinkedList[BasicTransaction]()
        person_node = self.all_people.head
        
        while person_node:
            person = person_node.data
            person_vertex = self.flow_graph.get_vertex(person)
            
            if person_vertex and person_vertex.edges:
                # Duyệt qua tất cả cạnh xuất phát từ người này
                edge_node = person_vertex.edges.head
                while edge_node:
                    edge = edge_node.data
                    
                    # Chỉ lấy các cạnh có luồng dương và không kết nối với source/sink
                    if (edge.flow > EPSILON and 
                        edge.destination != self._S_NODE and 
                        edge.destination != self._T_NODE):
                        
                        # Tạo giao dịch từ luồng trên cạnh
                        transactions.append(BasicTransaction(
                            debtor=person,                      # Người gửi luồng = người nợ
                            creditor=edge.destination,          # Người nhận luồng = người cho vay
                            amount=round_money(edge.flow)       # Số tiền = lượng luồng đã làm tròn
                        ))
                    
                    edge_node = edge_node.next
            
            person_node = person_node.next
    
        return transactions