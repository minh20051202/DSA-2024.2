from typing import TypeVar, Generic, Callable
from .linked_list import LinkedList # ADT tự triển khai
from .hash_table import HashTable   # ADT tự triển khai

VT = TypeVar('VT') # Kiểu dữ liệu của đỉnh (vertex data)
ET = TypeVar('ET') # Kiểu dữ liệu của thông tin cạnh (edge info, có thể là trọng số)

class GraphEdge(Generic[VT, ET]):
    """Lớp biểu diễn một cạnh trong đồ thị."""
    def __init__(self, source_vertex_data: VT, destination_vertex_data: VT, 
                 edge_data: ET | None = None, 
                 capacity: float | None = None, 
                 cost: float | None = None):
        self.source: VT = source_vertex_data
        self.destination: VT = destination_vertex_data
        self.data: ET | None = edge_data # Trọng số hoặc thông tin khác của cạnh
        
        # Dành cho mạng luồng / Luồng cực đại chi phí cực tiểu (MCMF)
        self.capacity: float | None = capacity
        self.flow: float = 0.0 # Luồng ban đầu là 0
        self.cost: float | None = cost
        self.reverse_edge: GraphEdge[VT, ET] | None = None # Dành cho đồ thị còn dư (residual graph)

    def __str__(self):
        details = f"Edge({self.source} -> {self.destination}, Data: {self.data}"
        if self.capacity is not None:
            details += f", Cap: {self.capacity}, Flow: {self.flow}"
        if self.cost is not None:
            details += f", Cost: {self.cost}"
        details += ")"
        return details

class GraphVertex(Generic[VT, ET]):
    """Lớp biểu diễn một đỉnh trong đồ thị."""
    def __init__(self, vertex_data: VT):
        self.data: VT = vertex_data
        # Danh sách kề: mỗi phần tử là một GraphEdge bắt đầu từ đỉnh này
        self.edges: LinkedList[GraphEdge[VT, ET]] = LinkedList()

    def add_edge(self, destination_vertex_data: VT, 
                 edge_data: ET | None = None, 
                 capacity: float | None = None, 
                 cost: float | None = None) -> GraphEdge[VT,ET]:
        edge = GraphEdge(self.data, destination_vertex_data, edge_data, capacity, cost)
        self.edges.append(edge)
        return edge

    def get_edge_to(self, destination_vertex_data: VT) -> GraphEdge[VT, ET] | None:
        for edge in self.edges:
            if edge.destination == destination_vertex_data:
                return edge
        return None

    def __str__(self):
        return f"Vertex({self.data})"

class Graph(Generic[VT, ET]):
    """Triển khai Đồ thị tự tạo."""
    def __init__(self, is_directed: bool = True):
        # vertices là một HashTable map từ dữ liệu đỉnh (VT) sang đối tượng GraphVertex
        self.vertices: HashTable[VT, GraphVertex[VT, ET]] = HashTable()
        self.is_directed: bool = is_directed

    def add_vertex(self, vertex_data: VT) -> GraphVertex[VT, ET] | None:
        "Thêm đỉnh. Trả về đối tượng đỉnh nếu thêm mới, None nếu đã tồn tại." 
        if not self.vertices.contains_key(vertex_data):
            vertex = GraphVertex(vertex_data)
            self.vertices.put(vertex_data, vertex)
            return vertex
        return None # Đỉnh đã tồn tại

    def get_vertex(self, vertex_data: VT) -> GraphVertex[VT, ET] | None:
        "Lấy đối tượng đỉnh từ dữ liệu đỉnh." 
        return self.vertices.get(vertex_data)

    def add_edge(self, src_data: VT, dest_data: VT, 
                 edge_data: ET | None = None, 
                 capacity: float | None = None, 
                 cost: float | None = None) -> bool:
        "Thêm cạnh. Trả về True nếu thành công." 
        src_vertex = self.get_vertex(src_data)
        dest_vertex = self.get_vertex(dest_data)

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
        "Xóa đỉnh và tất cả các cạnh liên quan." 
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

        self.vertices.remove(vertex_data)
        return True

    def remove_edge(self, src_data: VT, dest_data: VT) -> bool:
        "Xóa cạnh." 
        src_vertex = self.get_vertex(src_data)
        if not src_vertex:
            return False
        
        edge = src_vertex.get_edge_to(dest_data)
        if edge:
            src_vertex.edges.remove_by_value(edge)
            if not self.is_directed:
                dest_vertex = self.get_vertex(dest_data)
                if dest_vertex:
                    reverse_edge = dest_vertex.get_edge_to(src_data)
                    if reverse_edge:
                        dest_vertex.edges.remove_by_value(reverse_edge)
            return True
        return False

    def get_neighbors_data(self, vertex_data: VT) -> LinkedList[VT] | None:
        "Trả về LinkedList dữ liệu của các đỉnh kề." 
        vertex = self.get_vertex(vertex_data)
        if not vertex:
            return None
        
        neighbors = LinkedList[VT]()
        for edge in vertex.edges:
            neighbors.append(edge.destination)
        return neighbors

    def get_edges_from(self, vertex_data: VT) -> LinkedList[GraphEdge[VT,ET]] | None:
        "Trả về LinkedList các cạnh đi ra từ đỉnh." 
        vertex = self.get_vertex(vertex_data)
        if not vertex:
            return None
        return vertex.edges

    def has_edge(self, src_data: VT, dest_data: VT) -> bool:
        "Kiểm tra cạnh tồn tại." 
        src_vertex = self.get_vertex(src_data)
        return src_vertex is not None and src_vertex.get_edge_to(dest_data) is not None

    def get_edge_data(self, src_data: VT, dest_data: VT) -> ET | None:
        "Lấy dữ liệu (trọng số) của cạnh." 
        src_vertex = self.get_vertex(src_data)
        if src_vertex:
            edge = src_vertex.get_edge_to(dest_data)
            if edge:
                return edge.data
        return None

    def get_num_vertices(self) -> int:
        return self.vertices.get_num_elements()
    
    def get_num_edges(self) -> int:
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

    def dfs(self, start_vertex_data: VT, visit_callback: Callable[[VT], None] | None = None) -> LinkedList[VT]:
        "Duyệt theo chiều sâu. Trả về LinkedList các đỉnh đã duyệt theo thứ tự DFS." 
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
        "Duyệt theo chiều rộng. Trả về LinkedList các đỉnh đã duyệt theo thứ tự BFS." 
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
                self._find_cycles_dfs_util_with_edges(
                    v_key,
                    path_edges,
                    recursion_stack_nodes,
                    globally_visited,
                    all_cycles_edges
                )
            current_key_node = current_key_node.next
        return all_cycles_edges

    def _find_cycles_dfs_util_with_edges(
        self,
        u_data: VT,
        path_edges: LinkedList[GraphEdge[VT, ET]], 
        recursion_stack_nodes: HashTable[VT, bool], 
        globally_visited: HashTable[VT, bool], 
        all_cycles_edges: LinkedList[LinkedList[GraphEdge[VT, ET]]]
    ):
        # Hàm trợ giúp cho find_cycles_with_edges.
        globally_visited.put(u_data, True)
        recursion_stack_nodes.put(u_data, True)

        u_vertex = self.get_vertex(u_data)
        if not u_vertex:
            if recursion_stack_nodes.contains_key(u_data): recursion_stack_nodes.remove(u_data) # Đảm bảo stack được dọn dẹp
            return

        for edge_to_v in u_vertex.edges: 
            v_data = edge_to_v.destination
            path_edges.append(edge_to_v)

            if not globally_visited.contains_key(v_data):
                self._find_cycles_dfs_util_with_edges(
                    v_data, path_edges, recursion_stack_nodes, globally_visited, all_cycles_edges
                )
            elif recursion_stack_nodes.contains_key(v_data):
                start_cycle_edge_index = -1
                temp_node = path_edges.head
                current_idx = 0
                while temp_node:
                    if temp_node.data.source == v_data:
                        start_cycle_edge_index = current_idx
                        break
                    temp_node = temp_node.next
                    current_idx +=1
                
                if start_cycle_edge_index != -1:
                    path_node_at_cycle_start = path_edges.get_node_at_index(start_cycle_edge_index)
                    if path_node_at_cycle_start and path_node_at_cycle_start.data.source == v_data:
                        temp_cycle_edges_list_py = []
                        current_edge_node_in_path = path_node_at_cycle_start
                        
                        while current_edge_node_in_path: 
                            temp_cycle_edges_list_py.append(current_edge_node_in_path.data)
                            if current_edge_node_in_path.data == edge_to_v: 
                                break
                            current_edge_node_in_path = current_edge_node_in_path.next
                        
                        if (temp_cycle_edges_list_py and 
                           len(temp_cycle_edges_list_py) > 0 and 
                           temp_cycle_edges_list_py[-1].destination == temp_cycle_edges_list_py[0].source):
                            
                            final_cycle_edges_ll = LinkedList[GraphEdge[VT,ET]]()
                            for cedg in temp_cycle_edges_list_py:
                                final_cycle_edges_ll.append(cedg)

                            if final_cycle_edges_ll.get_length() > 0:
                                all_cycles_edges.append(final_cycle_edges_ll)
            
            if not path_edges.is_empty() and path_edges.get_last() == edge_to_v:
                 path_edges.remove_last() 

        if recursion_stack_nodes.contains_key(u_data):
            recursion_stack_nodes.remove(u_data)