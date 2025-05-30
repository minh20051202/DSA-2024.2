from __future__ import annotations # Hỗ trợ cho PEP 563 (Đánh giá Trì hoãn của Chú thích)
from typing import TypeVar, Generic, Callable
from .linked_list import LinkedList # ADT tự triển khai
from .tuple import Tuple # New import - Renamed CustomTuple

K = TypeVar('K') # Kiểu của key (phải có thể so sánh được)
V = TypeVar('V') # Kiểu của value

class TreeNode(Generic[K, V]):
    """Nút (Node) cho Cây Tìm kiếm Nhị phân (BinarySearchTree)."""
    def __init__(self, key: K, value: V, parent: 'TreeNode[K,V]' | None = None):
        self.key: K = key
        self.value: V = value
        self.left: TreeNode[K, V] | None = None
        self.right: TreeNode[K, V] | None = None
        self.parent: TreeNode[K, V] | None = parent # Hữu ích cho việc xóa
        # self.height: int = 1 # Loại bỏ vì không dùng đến trong BST cơ bản

    def __str__(self) -> str:
        return f"(K:{self.key}, V:{self.value})" # Loại bỏ H:{self.height}

class BinarySearchTree(Generic[K, V]):
    """Triển khai Cây Nhị phân Tìm kiếm (Binary Search Tree - BST) tự tạo."""
    def __init__(self, comparator: Callable[[K, K], int] | None = None):
        """ 
        Hàm so sánh (Comparator) `comparator(a, b)` trả về: 
          - giá trị âm nếu a < b
          - 0 nếu a == b
          - giá trị dương nếu a > b
        Nếu không cung cấp `comparator`, các khóa (key) phải hỗ trợ các phép so sánh tự nhiên (ví dụ: <, >, ==).
        """
        self.root: TreeNode[K, V] | None = None
        self._size: int = 0
        self.comparator = comparator

    def _compare(self, key1: K, key2: K) -> int:
        """So sánh hai khóa dựa trên hàm so sánh được cung cấp hoặc mặc định."""
        if self.comparator:
            return self.comparator(key1, key2)
        else:
            # So sánh mặc định, key phải hỗ trợ __lt__, __gt__, __eq__
            if key1 < key2: return -1
            if key1 > key2: return 1
            return 0

    def get_size(self) -> int:
        "Trả về số lượng nút trong cây." 
        return self._size

    def is_empty(self) -> bool:
        "Kiểm tra xem cây có rỗng không." 
        return self._size == 0

    def insert(self, key: K, value: V) -> None:
        "Chèn một cặp key-value vào cây. Nếu key đã tồn tại, giá trị của nó sẽ được cập nhật." 
        if self.root is None:
            self.root = TreeNode(key, value)
            self._size = 1
            return

        current = self.root
        parent = None
        while current is not None:
            parent = current
            comparison = self._compare(key, current.key)
            if comparison < 0:
                current = current.left
            elif comparison > 0:
                current = current.right
            else: # Key đã tồn tại, cập nhật value
                current.value = value
                return
        
        # Chèn nút mới
        if parent is None: # Trường hợp này không nên xảy ra nếu root không None
            self.root = TreeNode(key, value)
        elif self._compare(key, parent.key) < 0:
            parent.left = TreeNode(key, value, parent)
        else:
            parent.right = TreeNode(key, value, parent)
        self._size += 1
        # Sau khi chèn, có thể cần cập nhật chiều cao và thực hiện cân bằng cây (ví dụ: cho AVL/Red-Black)
        # self._update_height_and_balance(parent) 

    def _search_node(self, key: K) -> TreeNode[K,V] | None:
        "Tìm kiếm một nút dựa trên key. Trả về nút nếu tìm thấy, ngược lại None." 
        current = self.root
        while current is not None:
            comparison = self._compare(key, current.key)
            if comparison < 0:
                current = current.left
            elif comparison > 0:
                current = current.right
            else:
                return current # Tìm thấy nút
        return None # Không tìm thấy nút

    def search(self, key: K) -> V | None:
        "Tìm kiếm một giá trị (value) dựa trên key. Trả về value nếu tìm thấy, ngược lại None." 
        node = self._search_node(key)
        return node.value if node else None

    def contains_key(self, key: K) -> bool:
        "Kiểm tra xem một key có tồn tại trong cây hay không." 
        return self._search_node(key) is not None

    def get_min_key_node(self, node: TreeNode[K,V] | None = None) -> TreeNode[K,V] | None:
        "Tìm nút có khóa (key) nhỏ nhất trong cây con bắt đầu từ `node` (hoặc từ gốc nếu `node` là None)." 
        current = node if node is not None else self.root
        if current is None: return None
        while current.left is not None:
            current = current.left
        return current

    def get_max_key_node(self, node: TreeNode[K,V] | None = None) -> TreeNode[K,V] | None:
        "Tìm nút có khóa (key) lớn nhất trong cây con bắt đầu từ `node` (hoặc từ gốc nếu `node` là None)." 
        current = node if node is not None else self.root
        if current is None: return None
        while current.right is not None:
            current = current.right
        return current

    def _transplant(self, u: TreeNode[K,V], v: TreeNode[K,V] | None) -> None:
        "Thay thế cây con tại nút `u` bằng cây con tại nút `v`." 
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        if v is not None:
            v.parent = u.parent

    def delete(self, key: K) -> bool:
        "Xóa nút có khóa (key) được chỉ định. Trả về True nếu xóa thành công, ngược lại False." 
        node_to_delete = self._search_node(key)
        if node_to_delete is None:
            return False # Key không tồn tại trong cây

        if node_to_delete.left is None:
            self._transplant(node_to_delete, node_to_delete.right)
        elif node_to_delete.right is None:
            self._transplant(node_to_delete, node_to_delete.left)
        else:
            # Nút có 2 con: tìm nút kế vị (successor - nút nhỏ nhất ở cây con phải)
            successor = self.get_min_key_node(node_to_delete.right)
            if successor is None: # Trường hợp này không nên xảy ra nếu cây con phải tồn tại
                # This should ideally not be reached if node_to_delete.right exists.
                # Adding robust error handling or logging might be good here.
                return False 

            if successor.parent != node_to_delete:
                self._transplant(successor, successor.right)
                successor.right = node_to_delete.right
                if successor.right:
                    successor.right.parent = successor
            
            self._transplant(node_to_delete, successor)
            successor.left = node_to_delete.left
            if successor.left:
                 successor.left.parent = successor
        
        self._size -= 1
        # Sau khi xóa, có thể cần cập nhật chiều cao và thực hiện cân bằng cây
        # self._update_height_and_balance_after_delete(parent_of_deleted_or_successor)
        return True

    def in_order_traversal(self) -> LinkedList[Tuple[K, V]]:
        "Thực hiện duyệt cây theo thứ tự giữa (in-order). Trả về một LinkedList các cặp (key, value) dạng Tuple."
        result = LinkedList[Tuple[K,V]]()
        self._in_order_recursive(self.root, result)
        return result

    def _in_order_recursive(self, node: TreeNode[K,V] | None, result: LinkedList[Tuple[K,V]]):
        """Hàm đệ quy hỗ trợ cho duyệt theo thứ tự giữa."""
        if node is not None:
            self._in_order_recursive(node.left, result)
            result.append(Tuple([node.key, node.value]))
            self._in_order_recursive(node.right, result)

    def pre_order_traversal(self) -> LinkedList[Tuple[K, V]]:
        "Thực hiện duyệt cây theo thứ tự trước (pre-order). Trả về một LinkedList các cặp (key, value) dạng Tuple."
        result = LinkedList[Tuple[K,V]]()
        self._pre_order_recursive(self.root, result)
        return result

    def _pre_order_recursive(self, node: TreeNode[K,V] | None, result: LinkedList[Tuple[K,V]]):
        """Hàm đệ quy hỗ trợ cho duyệt theo thứ tự trước."""
        if node is not None:
            result.append(Tuple([node.key, node.value]))
            self._pre_order_recursive(node.left, result)
            self._pre_order_recursive(node.right, result)

    def post_order_traversal(self) -> LinkedList[Tuple[K, V]]:
        "Thực hiện duyệt cây theo thứ tự sau (post-order). Trả về một LinkedList các cặp (key, value) dạng Tuple."
        result = LinkedList[Tuple[K,V]]()
        self._post_order_recursive(self.root, result)
        return result

    def _post_order_recursive(self, node: TreeNode[K,V] | None, result: LinkedList[Tuple[K,V]]):
        """Hàm đệ quy hỗ trợ cho duyệt theo thứ tự sau."""
        if node is not None:
            self._post_order_recursive(node.left, result)
            self._post_order_recursive(node.right, result)
            result.append(Tuple([node.key, node.value]))
    
    # Các phương thức liên quan đến cân bằng cây (ví dụ: AVL) đã được loại bỏ
    # để giữ cho triển khai BST cơ bản và tập trung.

    def __str__(self) -> str:
        # Một cách đơn giản để hiển thị cây (có thể được cải thiện cho đẹp hơn)
        if self.root is None:
            return "BST()"
        lines, _, _, _ = self._display_aux(self.root)
        return "\n".join(lines)

    def _display_aux(self, node):
        """Trả về danh sách các chuỗi, chiều rộng, chiều cao, và tọa độ ngang của gốc.
        Hàm này dùng để hỗ trợ hiển thị cây một cách trực quan.
        Nguồn tham khảo (hoặc ý tưởng tương tự): https://stackoverflow.com/questions/34012886/print-binary-tree-level-by-level-in-python
        """
        # Trường hợp không có con (nút lá).
        if node.right is None and node.left is None:
            line = f'({node.key})'
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Trường hợp chỉ có con trái.
        if node.right is None:
            lines, n, p, x = self._display_aux(node.left)
            s_node = f'({node.key})'
            u_node = len(s_node)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s_node
            second_line = x * ' ' + '/' + (n - x - 1 + u_node) * ' '
            shifted_lines = [line + u_node * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u_node, p + 2, n + u_node // 2

        # Trường hợp chỉ có con phải.
        if node.left is None:
            lines, n, p, x = self._display_aux(node.right)
            s_node = f'({node.key})'
            u_node = len(s_node)
            first_line = s_node + x * '_' + (n - x) * ' '
            second_line = (u_node + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u_node * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u_node, p + 2, u_node // 2

        # Trường hợp có cả hai con.
        left, n, p, x = self._display_aux(node.left)
        right, m, q, y = self._display_aux(node.right)
        s_node = f'({node.key})'
        u_node = len(s_node)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s_node + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u_node + y) * ' ' + '\\' + (m - y - 1) * ' '
        # Nối các dòng từ cây con trái và phải, căn chỉnh cho phù hợp
        # Đảm bảo left và right có cùng số dòng bằng cách thêm các dòng trống nếu cần
        max_len = max(len(left), len(right))
        left_padded = left + [(n) * ' '] * (max_len - len(left))
        right_padded = right + [(m) * ' '] * (max_len - len(right))

        zipped_lines = zip(left_padded, right_padded)
        lines = [first_line, second_line] + [a + u_node * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u_node, max(p, q) + 2, n + u_node // 2

    def get_height(self) -> int:
        """Tính chiều cao của cây. 
        Chiều cao được định nghĩa là số cạnh trên đường đi dài nhất từ gốc đến một nút lá.
        Cây rỗng có chiều cao -1. Cây chỉ có gốc có chiều cao 0."""
        return self._get_height_recursive(self.root)

    def _get_height_recursive(self, node: TreeNode[K,V] | None) -> int:
        """Hàm đệ quy để tính chiều cao của một nút."""
        if node is None:
            return -1 # Chiều cao của một cây con rỗng (hoặc không tồn tại)
        
        left_height = self._get_height_recursive(node.left)
        right_height = self._get_height_recursive(node.right)
        return 1 + max(left_height, right_height) 