from typing import TypeVar, Generic, Callable
from .linked_list import LinkedList # ADT tự triển khai
from .hash_table import HashTable   # ADT tự triển khai
from .array import Array

VT = TypeVar('VT') # Kiểu dữ liệu của đỉnh (vertex data)
ET = TypeVar('ET') # Kiểu dữ liệu của thông tin cạnh (edge info, có thể là trọng số)

class GraphEdge(Generic[VT, ET]):
    """
    GRAPH EDGE - CẠNH ĐỒ THỊ
    
    Biểu diễn một cạnh trong đồ thị, chứa thông tin về đỉnh nguồn, đỉnh đích,
    và các thuộc tính bổ sung như trọng số, dung lượng, chi phí cho các thuật toán
    mạng luồng và luồng cực đại chi phí cực tiểu (MCMF).
    
    THUỘC TÍNH:
    - source: Dữ liệu của đỉnh nguồn
    - destination: Dữ liệu của đỉnh đích  
    - data: Thông tin/trọng số của cạnh
    - capacity: Dung lượng cạnh (cho mạng luồng)
    - flow: Luồng hiện tại qua cạnh
    - cost: Chi phí của cạnh (cho MCMF)
    - reverse_edge: Con trỏ đến cạnh ngược (cho đồ thị còn dư)
    """
    
    def __init__(self, source_vertex_data: VT, destination_vertex_data: VT, 
                 edge_data: ET | None = None, 
                 capacity: float | None = None, 
                 cost: float | None = None):
        """
        Khởi tạo một cạnh mới.
        
        Tham số:
            source_vertex_data (VT): Dữ liệu của đỉnh nguồn
            destination_vertex_data (VT): Dữ liệu của đỉnh đích
            edge_data (ET | None): Thông tin/trọng số của cạnh
            capacity (float | None): Dung lượng cạnh (cho mạng luồng)
            cost (float | None): Chi phí của cạnh (cho MCMF)
        """
        self.source: VT = source_vertex_data
        self.destination: VT = destination_vertex_data
        self.data: ET | None = edge_data # Trọng số hoặc thông tin khác của cạnh
        
        # Dành cho mạng luồng / Luồng cực đại chi phí cực tiểu (MCMF)
        self.capacity: float | None = capacity
        self.flow: float = 0.0 # Luồng ban đầu là 0
        self.cost: float | None = cost
        self.reverse_edge: GraphEdge[VT, ET] | None = None # Dành cho đồ thị còn dư (residual graph)

class GraphVertex(Generic[VT, ET]):
    """
    GRAPH VERTEX - ĐỈNH ĐỒ THỊ
    
    Biểu diễn một đỉnh trong đồ thị sử dụng danh sách kề.
    Mỗi đỉnh chứa dữ liệu và danh sách các cạnh đi ra từ đỉnh này.
    
    THUỘC TÍNH:
    - data: Dữ liệu lưu trữ tại đỉnh
    - edges: Danh sách kề các cạnh đi ra từ đỉnh
    
    PHƯƠNG THỨC:
    - add_edge(): Thêm cạnh đi ra từ đỉnh - O(1)
    - get_edge_to(): Tìm cạnh đến một đỉnh cụ thể - O(degree)
    """
    
    def __init__(self, vertex_data: VT):
        """
        Khởi tạo một đỉnh mới.
        
        Tham số:
            vertex_data (VT): Dữ liệu lưu trữ tại đỉnh
        """
        self.data: VT = vertex_data
        # Danh sách kề: mỗi phần tử là một GraphEdge bắt đầu từ đỉnh này
        self.edges: LinkedList[GraphEdge[VT, ET]] = LinkedList()

    def add_edge(self, destination_vertex_data: VT, 
                 edge_data: ET | None = None, 
                 capacity: float | None = None, 
                 cost: float | None = None) -> GraphEdge[VT,ET]:
        """
        Thêm cạnh đi ra từ đỉnh này đến đỉnh đích.
        
        Tham số:
            destination_vertex_data (VT): Dữ liệu của đỉnh đích
            edge_data (ET | None): Thông tin/trọng số của cạnh
            capacity (float | None): Dung lượng cạnh
            cost (float | None): Chi phí của cạnh
            
        Trả về:
            GraphEdge[VT,ET]: Cạnh vừa được tạo
        """
        edge = GraphEdge(self.data, destination_vertex_data, edge_data, capacity, cost)
        self.edges.append(edge)
        return edge

    def get_edge_to(self, destination_vertex_data: VT) -> GraphEdge[VT, ET] | None:
        """
        Tìm cạnh đi từ đỉnh này đến đỉnh đích.
        
        Tham số:
            destination_vertex_data (VT): Dữ liệu của đỉnh đích
            
        Trả về:
            GraphEdge[VT, ET] | None: Cạnh nếu tìm thấy, None nếu không có
            
        Độ phức tạp: O(degree) - degree là số cạnh đi ra từ đỉnh
        """
        for edge in self.edges:
            if edge.destination == destination_vertex_data:
                return edge
        return None

class Graph(Generic[VT, ET]):
    """
    GRAPH - ĐỒ THỊ
    
    Triển khai đồ thị sử dụng danh sách kề với HashTable để lưu trữ các đỉnh.
    Hỗ trợ cả đồ thị có hướng và vô hướng, các thuật toán duyệt, tìm chu trình,
    và các tính năng cho mạng luồng (MCMF).
    
    THUỘC TÍNH:
    - vertices: HashTable lưu trữ các đỉnh
    - is_directed: Xác định đồ thị có hướng hay vô hướng
    
    PHƯƠNG THỨC CƠ BẢN:
    - add_vertex(): Thêm đỉnh - O(1) trung bình
    - get_vertex(): Lấy đỉnh - O(1) trung bình  
    - add_edge(): Thêm cạnh - O(1) trung bình
    - remove_vertex(): Xóa đỉnh - O(V + E) worst case
    - remove_edge(): Xóa cạnh - O(degree) 
    - has_edge(): Kiểm tra cạnh - O(degree)
    - get_neighbors_data(): Lấy danh sách láng giềng - O(degree)
    - dfs(): Duyệt theo chiều sâu - O(V + E)
    - bfs(): Duyệt theo chiều rộng - O(V + E)
    - find_cycles_with_edges(): Tìm chu trình với danh sách cạnh - O(V + E)
    """
    
    def __init__(self, is_directed: bool = True):
        """
        Khởi tạo đồ thị mới.
        
        Tham số:
            is_directed (bool): True nếu đồ thị có hướng, False nếu vô hướng
        """
        # vertices là một HashTable map từ dữ liệu đỉnh (VT) sang đối tượng GraphVertex
        self.vertices: HashTable[VT, GraphVertex[VT, ET]] = HashTable()
        self.is_directed: bool = is_directed

    def add_vertex(self, vertex_data: VT) -> GraphVertex[VT, ET] | None:
        """
        Thêm đỉnh mới vào đồ thị.
        
        Tham số:
            vertex_data (VT): Dữ liệu của đỉnh cần thêm
            
        Trả về:
            GraphVertex[VT, ET] | None: Đối tượng đỉnh nếu thêm thành công, None nếu đã tồn tại
            
        Độ phức tạp: O(1) trung bình
        """ 
        if not self.vertices.contains_key(vertex_data):
            vertex = GraphVertex(vertex_data)
            self.vertices.put(vertex_data, vertex)
            return vertex
        return None # Đỉnh đã tồn tại

    def get_vertex(self, vertex_data: VT) -> GraphVertex[VT, ET] | None:
        """
        Lấy đối tượng đỉnh từ dữ liệu đỉnh.
        
        Tham số:
            vertex_data (VT): Dữ liệu của đỉnh cần tìm
            
        Trả về:
            GraphVertex[VT, ET] | None: Đối tượng đỉnh nếu tìm thấy, None nếu không có
            
        Độ phức tạp: O(1) trung bình
        """ 
        return self.vertices.get(vertex_data)

    def add_edge(self, src_data: VT, dest_data: VT, 
                 edge_data: ET | None = None, 
                 capacity: float | None = None, 
                 cost: float | None = None) -> bool:
        """
        Thêm cạnh vào đồ thị.
        
        Tham số:
            src_data (VT): Dữ liệu đỉnh nguồn
            dest_data (VT): Dữ liệu đỉnh đích
            edge_data (ET | None): Thông tin/trọng số cạnh
            capacity (float | None): Dung lượng cạnh (cho mạng luồng)
            cost (float | None): Chi phí cạnh (cho MCMF)
            
        Trả về:
            bool: True nếu thêm thành công, False nếu cạnh đã tồn tại
            
        Độ phức tạp: O(1) trung bình cho việc thêm, O(degree) để kiểm tra trùng lặp
        """ 
        src_vertex = self.get_vertex(src_data)
        dest_vertex = self.get_vertex(dest_data)

        # Tự động tạo đỉnh nếu chưa tồn tại
        if src_vertex is None:
            src_vertex = self.add_vertex(src_data)
            if src_vertex is None: return False # Không nên xảy ra nếu logic add_vertex đúng

        if dest_vertex is None:
            dest_vertex = self.add_vertex(dest_data)
            if dest_vertex is None: return False
            
        # Kiểm tra xem cạnh đã tồn tại chưa để tránh trùng lặp (cho đồ thị đơn).
        # Đối với MCMF, có thể cần nhiều cạnh với chi phí/khả năng chứa khác nhau,
        # hoặc việc kiểm tra này cần phức tạp hơn nếu các cạnh được xác định duy nhất bởi nhiều yếu tố hơn chỉ là dest_data.
        # get_edge_to hiện tại chỉ tìm thấy một cạnh. Nếu chúng ta sử dụng lớp Graph này một cách nghiêm ngặt cho MCMF,
        # và nhiều giao dịch riêng biệt (dưới dạng edge_data) có thể tồn tại giữa hai người,
        # thì việc kiểm tra này có vấn đề.
        # Tuy nhiên, đối với công thức MCMF điển hình nơi có một cạnh P_i -> P_j với chi phí 1,
        # việc kiểm tra đơn giản này có thể ổn ban đầu.
        if src_vertex.get_edge_to(dest_data) and capacity is None and cost is None:
             # Nếu đây là một phép thêm cạnh "đơn giản" và nó đã tồn tại, trả về False.
             # Nếu đó là một cạnh có khả năng chứa/chi phí, chúng ta có thể cho phép hoặc cần logic khác.
             # Hiện tại, chúng ta giữ nguyên hành vi ban đầu cho các cạnh không có khả năng chứa/chi phí.
            return False 

        # Đối với MCMF, chính đối tượng cạnh sẽ lưu trữ khả năng chứa, chi phí, luồng.
        # 'edge_data' (ET) vẫn có thể hữu ích để mang thông tin giao dịch gốc nếu cần.
        created_edge = src_vertex.add_edge(dest_data, edge_data, capacity, cost)

        # Xử lý đồ thị vô hướng: thêm cạnh ngược
        if not self.is_directed:
            if not dest_vertex.get_edge_to(src_data):
                 # Đối với đồ thị vô hướng, cạnh ngược cũng nên có cùng khả năng chứa/chi phí
                 reverse_created_edge = dest_vertex.add_edge(src_data, edge_data, capacity, cost)
                 # Thiết lập con trỏ reverse_edge cho đồ thị còn dư trong MCMF
                 # Đây là một thiết lập đơn giản hóa; một đồ thị còn dư chuyên dụng thường được xây dựng.
                 if capacity is not None: # Giả sử nếu capacity được đặt, đó là một cạnh mạng luồng
                    created_edge.reverse_edge = reverse_created_edge
                    reverse_created_edge.reverse_edge = created_edge
            
        return True

    def remove_vertex(self, vertex_data: VT) -> bool:
        """
        Xóa đỉnh và tất cả các cạnh liên quan.
        
        Tham số:
            vertex_data (VT): Dữ liệu của đỉnh cần xóa
            
        Trả về:
            bool: True nếu xóa thành công, False nếu đỉnh không tồn tại
            
        Độ phức tạp: O(V + E) - cần duyệt tất cả đỉnh để xóa cạnh đi vào
        """ 
        vertex_to_remove = self.vertices.get(vertex_data)
        if not vertex_to_remove:
            return False # Đỉnh không tồn tại

        # Xóa tất cả các cạnh đi vào đỉnh này
        keys_ll = self.vertices.keys() 
        if keys_ll: # Đảm bảo keys_ll không None
            current_key_node = keys_ll.head
            while current_key_node:
                v_data = current_key_node.data
                if v_data != vertex_data:
                    v = self.vertices.get(v_data)
                    if v:
                        edge_to_remove_vertex = v.get_edge_to(vertex_data)
                        if edge_to_remove_vertex:
                            v.edges.remove_by_value(edge_to_remove_vertex)
                current_key_node = current_key_node.next

        # Xóa đỉnh khỏi HashTable
        self.vertices.remove(vertex_data)
        return True

    def remove_edge(self, src_data: VT, dest_data: VT) -> bool:
        """
        Xóa cạnh khỏi đồ thị.
        
        Tham số:
            src_data (VT): Dữ liệu đỉnh nguồn
            dest_data (VT): Dữ liệu đỉnh đích
            
        Trả về:
            bool: True nếu xóa thành công, False nếu cạnh không tồn tại
            
        Độ phức tạp: O(degree) - degree là số cạnh đi ra từ đỉnh nguồn
        """ 
        src_vertex = self.get_vertex(src_data)
        if not src_vertex:
            return False
        
        edge = src_vertex.get_edge_to(dest_data)
        if edge:
            src_vertex.edges.remove_by_value(edge)
            # Xử lý đồ thị vô hướng: xóa cạnh ngược
            if not self.is_directed:
                dest_vertex = self.get_vertex(dest_data)
                if dest_vertex:
                    reverse_edge = dest_vertex.get_edge_to(src_data)
                    if reverse_edge:
                        dest_vertex.edges.remove_by_value(reverse_edge)
            return True
        return False

    def get_neighbors_data(self, vertex_data: VT) -> LinkedList[VT] | None:
        """
        Lấy danh sách dữ liệu của các đỉnh kề.
        
        Tham số:
            vertex_data (VT): Dữ liệu của đỉnh cần lấy láng giềng
            
        Trả về:
            LinkedList[VT] | None: Danh sách dữ liệu các đỉnh kề, None nếu đỉnh không tồn tại
            
        Độ phức tạp: O(degree) - degree là số cạnh đi ra từ đỉnh
        """ 
        vertex = self.get_vertex(vertex_data)
        if not vertex:
            return None
        
        neighbors = LinkedList[VT]()
        for edge in vertex.edges:
            neighbors.append(edge.destination)
        return neighbors

    def get_edges_from(self, vertex_data: VT) -> LinkedList[GraphEdge[VT,ET]] | None:
        """
        Lấy danh sách các cạnh đi ra từ đỉnh.
        
        Tham số:
            vertex_data (VT): Dữ liệu của đỉnh
            
        Trả về:
            LinkedList[GraphEdge[VT,ET]] | None: Danh sách cạnh đi ra, None nếu đỉnh không tồn tại
            
        Độ phức tạp: O(1) - trả về tham chiếu đến danh sách có sẵn
        """ 
        vertex = self.get_vertex(vertex_data)
        if not vertex:
            return None
        return vertex.edges

    def has_edge(self, src_data: VT, dest_data: VT) -> bool:
        """
        Kiểm tra xem cạnh có tồn tại hay không.
        
        Tham số:
            src_data (VT): Dữ liệu đỉnh nguồn
            dest_data (VT): Dữ liệu đỉnh đích
            
        Trả về:
            bool: True nếu cạnh tồn tại, False nếu không
            
        Độ phức tạp: O(degree) - degree là số cạnh đi ra từ đỉnh nguồn
        """ 
        src_vertex = self.get_vertex(src_data)
        return src_vertex is not None and src_vertex.get_edge_to(dest_data) is not None

    def get_edge_data(self, src_data: VT, dest_data: VT) -> ET | None:
        """
        Lấy dữ liệu (trọng số) của cạnh.
        
        Tham số:
            src_data (VT): Dữ liệu đỉnh nguồn
            dest_data (VT): Dữ liệu đỉnh đích
            
        Trả về:
            ET | None: Dữ liệu của cạnh nếu tồn tại, None nếu không
            
        Độ phức tạp: O(degree) - degree là số cạnh đi ra từ đỉnh nguồn
        """ 
        src_vertex = self.get_vertex(src_data)
        if src_vertex:
            edge = src_vertex.get_edge_to(dest_data)
            if edge:
                return edge.data
        return None

    def get_num_vertices(self) -> int:
        """
        Lấy số lượng đỉnh trong đồ thị.
        
        Trả về:
            int: Số lượng đỉnh
            
        Độ phức tạp: O(1)
        """
        return self.vertices.get_num_elements()
    
    def get_num_edges(self) -> int:
        """
        Lấy số lượng cạnh trong đồ thị.
        
        Trả về:
            int: Số lượng cạnh
            
        Độ phức tạp: O(V) - cần duyệt qua tất cả đỉnh để đếm cạnh
        """
        # Tính lại số cạnh chính xác hơn cho đồ thị có hướng bằng cách tính tổng độ dài của các danh sách kề.
        # Đối với đồ thị vô hướng, điều này sẽ đếm mỗi cạnh hai lần, vì vậy cần chia cho 2.
        count = 0
        # HashTable.keys() trả về LinkedList các keys, cần duyệt qua nó.
        keys_list = self.vertices.keys()
        node = keys_list.head
        while node:
            vertex_data = node.data
            vertex = self.vertices.get(vertex_data)
            if vertex:
                count += vertex.edges.get_length()
            node = node.next
        
        if not self.is_directed:
            # Đối với đồ thị vô hướng, mỗi cạnh (u,v) sẽ được lưu trữ dưới dạng u->v và v->u trong danh sách kề.
            # Vì vậy, tổng độ dài của tất cả các danh sách kề là 2*E.
            return count // 2
        return count # Đối với đồ thị có hướng, tổng các bậc ra là E.
    def get_all_vertices(self) -> LinkedList[VT]:
        """
        Lấy danh sách tất cả các đỉnh trong đồ thị.
        
        Trả về:
            LinkedList[VT]: Danh sách dữ liệu của tất cả các đỉnh
            
        Độ phức tạp: O(V) - V là số đỉnh
        """
        all_vertices = LinkedList[VT]()
        keys_list = self.vertices.keys()
        
        if keys_list:
            current_node = keys_list.head
            while current_node:
                vertex_data = current_node.data
                all_vertices.append(vertex_data)
                current_node = current_node.next
        
        return all_vertices

    def get_all_vertex_objects(self) -> LinkedList[GraphVertex[VT, ET]]:
        """
        Lấy danh sách tất cả các đối tượng đỉnh trong đồ thị.
        
        Trả về:
            LinkedList[GraphVertex[VT, ET]]: Danh sách tất cả các đối tượng đỉnh
            
        Độ phức tạp: O(V) - V là số đỉnh
        """
        all_vertex_objects = LinkedList[GraphVertex[VT, ET]]()
        keys_list = self.vertices.keys()
        
        if keys_list:
            current_node = keys_list.head
            while current_node:
                vertex_data = current_node.data
                vertex_obj = self.vertices.get(vertex_data)
                if vertex_obj:
                    all_vertex_objects.append(vertex_obj)
                current_node = current_node.next
        
        return all_vertex_objects

    def dfs(self, start_vertex_data: VT, visit_callback: Callable[[VT], None] | None = None) -> LinkedList[VT]:
        """
        Duyệt đồ thị theo chiều sâu (Depth-First Search).
        
        Tham số:
            start_vertex_data (VT): Dữ liệu đỉnh bắt đầu duyệt
            visit_callback (Callable[[VT], None] | None): Hàm callback được gọi khi thăm mỗi đỉnh
            
        Trả về:
            LinkedList[VT]: Danh sách các đỉnh theo thứ tự duyệt DFS
            
        Độ phức tạp: O(V + E) - V là số đỉnh, E là số cạnh
        """ 
        start_vertex = self.get_vertex(start_vertex_data)
        if not start_vertex:
            return LinkedList[VT]()

        visited_order = LinkedList[VT]()
        # visited_set dùng HashTable để check O(1) trung bình
        visited_set = HashTable[VT, bool]() 
        stack = LinkedList[GraphVertex[VT,ET]]() # Dùng LinkedList như stack

        stack.prepend(start_vertex)
        
        while not stack.is_empty():
            current_vertex = stack.remove_at_index(0) # pop từ đầu (prepend/remove_at_index(0))

            if not visited_set.contains_key(current_vertex.data):
                visited_set.put(current_vertex.data, True)
                visited_order.append(current_vertex.data)
                if visit_callback:
                    visit_callback(current_vertex.data)
                
                # Thêm các đỉnh kề chưa thăm vào stack (theo thứ tự ngược để duyệt đúng thứ tự mong muốn)
                # Hoặc không cần quan tâm thứ tự duyệt neighbors nếu bài toán không yêu cầu
                temp_neighbors = LinkedList[GraphVertex[VT,ET]]()
                for edge in current_vertex.edges:
                    neighbor_vertex = self.get_vertex(edge.destination)
                    if neighbor_vertex and not visited_set.contains_key(neighbor_vertex.data):
                        temp_neighbors.prepend(neighbor_vertex) # Thêm vào đầu để xử lý sau
                
                for neighbor_to_visit in temp_neighbors:
                    stack.prepend(neighbor_to_visit)
                    
        return visited_order

    def bfs(self, start_vertex_data: VT, visit_callback: Callable[[VT], None] | None = None) -> LinkedList[VT]:
        """
        Duyệt đồ thị theo chiều rộng (Breadth-First Search).
        
        Tham số:
            start_vertex_data (VT): Dữ liệu đỉnh bắt đầu duyệt
            visit_callback (Callable[[VT], None] | None): Hàm callback được gọi khi thăm mỗi đỉnh
            
        Trả về:
            LinkedList[VT]: Danh sách các đỉnh theo thứ tự duyệt BFS
            
        Độ phức tạp: O(V + E) - V là số đỉnh, E là số cạnh
        """ 
        start_vertex = self.get_vertex(start_vertex_data)
        if not start_vertex:
            return LinkedList[VT]()

        visited_order = LinkedList[VT]()
        visited_set = HashTable[VT, bool]()
        queue = LinkedList[GraphVertex[VT,ET]]() # Dùng LinkedList như queue

        queue.append(start_vertex) # enqueue
        visited_set.put(start_vertex.data, True)
        
        while not queue.is_empty():
            current_vertex = queue.remove_at_index(0) # dequeue
            visited_order.append(current_vertex.data)
            if visit_callback:
                visit_callback(current_vertex.data)

            for edge in current_vertex.edges:
                neighbor_vertex = self.get_vertex(edge.destination)
                if neighbor_vertex and not visited_set.contains_key(neighbor_vertex.data):
                    visited_set.put(neighbor_vertex.data, True)
                    queue.append(neighbor_vertex)
        return visited_order

    def find_cycles_with_edges(self) -> LinkedList[LinkedList[GraphEdge[VT, ET]]]:
        """
        Tìm tất cả các chu trình trong đồ thị có hướng và trả về danh sách các cạnh tạo thành từng chu trình.
        
        Sử dụng thuật toán Depth-First Search (DFS) với recursion stack để phát hiện back edges.
        Khi phát hiện back edge, trích xuất chu trình từ path hiện tại và lưu trữ các cạnh của chu trình.
        
        Lưu ý:
            - Chỉ hoạt động hiệu quả với đồ thị có hướng
            - ET (kiểu dữ liệu trên cạnh) được mong đợi là Transaction
            
        Trả về:
            LinkedList[LinkedList[GraphEdge[VT, ET]]]: Danh sách các chu trình, mỗi chu trình là một 
            danh sách các cạnh tạo thành chu trình đó. Trả về danh sách rỗng nếu đồ thị không có hướng.
            
        Độ phức tạp: O(V + E) - V là số đỉnh, E là số cạnh
        """
        # ET (kiểu dữ liệu trên cạnh) được mong đợi là Transaction.
        all_cycles_edges = LinkedList[LinkedList[GraphEdge[VT, ET]]]()
        if not self.is_directed:
            print("Cảnh báo: Việc phát hiện chu trình với các cạnh chủ yếu dành cho đồ thị có hướng.")
            return all_cycles_edges

        globally_visited = HashTable[VT, bool]()
        
        # HashTable.keys() trả về một LinkedList các khóa
        keys_ll = self.vertices.keys()
        current_key_node = keys_ll.head
        while current_key_node:
            v_key = current_key_node.data # Lấy khóa thực tế
            if not globally_visited.contains_key(v_key):
                recursion_stack_nodes = HashTable[VT, bool]()
                path_edges = LinkedList[GraphEdge[VT, ET]]()
                self.__find_cycles_dfs_util_with_edges__(
                    v_key,
                    path_edges,
                    recursion_stack_nodes,
                    globally_visited,
                    all_cycles_edges
                )
            current_key_node = current_key_node.next
        return all_cycles_edges

    def __find_cycles_dfs_util_with_edges__(
        self,
        u_data: VT,
        path_edges: LinkedList[GraphEdge[VT, ET]], 
        recursion_stack_nodes: HashTable[VT, bool], 
        globally_visited: HashTable[VT, bool], 
        all_cycles_edges: LinkedList[LinkedList[GraphEdge[VT, ET]]]
    ):
        """
        Hàm trợ giúp thực hiện DFS để tìm chu trình với các cạnh trong đồ thị có hướng.
        
        Thực hiện tìm kiếm theo chiều sâu và phát hiện back edges để xác định chu trình.
        Khi phát hiện back edge (cạnh quay lại đỉnh đã có trong recursion stack), 
        trích xuất chu trình từ đường đi hiện tại và lưu trữ các cạnh của chu trình.
        
        Tham số:
            u_data (VT): Dữ liệu của đỉnh hiện tại đang xét
            path_edges (LinkedList[GraphEdge[VT, ET]]): Danh sách các cạnh trong đường đi hiện tại
            recursion_stack_nodes (HashTable[VT, bool]): Các đỉnh hiện tại trong recursion stack
            globally_visited (HashTable[VT, bool]): Các đỉnh đã được thăm toàn cục  
            all_cycles_edges (LinkedList[LinkedList[GraphEdge[VT, ET]]]): Danh sách kết quả chứa tất cả chu trình
            
        Lưu ý:
            - Hàm này chỉ nên được gọi từ find_cycles_with_edges()
            - Đảm bảo dọn dẹp recursion stack để tránh ảnh hưởng đến các lần gọi khác
            
        Độ phức tạp: O(V + E) - V là số đỉnh, E là số cạnh
        """
        # Hàm trợ giúp cho find_cycles_with_edges.
        globally_visited.put(u_data, True)
        recursion_stack_nodes.put(u_data, True)

        u_vertex = self.get_vertex(u_data)
        if not u_vertex:
            if recursion_stack_nodes.contains_key(u_data):
                recursion_stack_nodes.remove(u_data)
            return

        for edge_to_v in u_vertex.edges:
            v_data = edge_to_v.destination
            path_edges.append(edge_to_v) # Thêm cạnh vào đường đi hiện tại

            if not globally_visited.contains_key(v_data):
                self.__find_cycles_dfs_util_with_edges__(
                    v_data, path_edges, recursion_stack_nodes, globally_visited, all_cycles_edges
                )
            elif recursion_stack_nodes.contains_key(v_data):
                # Phát hiện back edge - có chu trình
                start_cycle_edge_index = -1
                temp_node_path_scanner = path_edges.head
                current_idx_scanner = 0
                while temp_node_path_scanner:
                    # Tìm cạnh đầu tiên trong path_edges có nguồn là v_data (nơi back-edge trỏ tới)
                    if temp_node_path_scanner.data.source == v_data:
                        start_cycle_edge_index = current_idx_scanner
                        break
                    temp_node_path_scanner = temp_node_path_scanner.next
                    current_idx_scanner += 1

                if start_cycle_edge_index != -1:
                    # Trích xuất chu trình từ start_cycle_edge_index đến cuối path_edges
                    # (cạnh cuối cùng trong path_edges là back-edge)
                    cycle_edges_for_this_path = LinkedList[GraphEdge[VT, ET]]()
                    # Bắt đầu từ node trong path_edges tại start_cycle_edge_index
                    current_edge_node_in_path = path_edges.get_node_at_index(start_cycle_edge_index)
                    while current_edge_node_in_path:
                        cycle_edges_for_this_path.append(current_edge_node_in_path.data)
                        current_edge_node_in_path = current_edge_node_in_path.next
                    
                    if not cycle_edges_for_this_path.is_empty():
                        all_cycles_edges.append(cycle_edges_for_this_path)
                # KHÔNG CÓ `break` ở đây nữa, để tiếp tục tìm các chu trình khác từ u_data

            # Backtrack: loại bỏ cạnh vừa xử lý khỏi path_edges
            # Đảm bảo chỉ remove nếu nó thực sự là cạnh cuối cùng (quan trọng khi không có break)
            if not path_edges.is_empty() and path_edges.get_last() == edge_to_v:
                path_edges.remove_last()

        if recursion_stack_nodes.contains_key(u_data):
            recursion_stack_nodes.remove(u_data)