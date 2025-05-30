from typing import Generic, TypeVar, Iterable

# Biến kiểu cho LinkedList dùng chung (generic)
T = TypeVar('T')

class Node(Generic[T]):
    """Nút (Node) cho Danh sách Liên kết (LinkedList)."""
    def __init__(self, data: T):
        self.data: T = data
        self.next: Node[T] | None = None

    def __str__(self) -> str:
        return str(self.data)

class LinkedList(Generic[T]):
    """Triển khai cấu trúc dữ liệu Danh sách Liên kết (LinkedList) tự tạo."""
    def __init__(self, initial_data: Iterable[T] | None = None):
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self.length: int = 0
        if initial_data:
            for item in initial_data:
                self.append(item)

    def append(self, data: T) -> None:
        "Thêm phần tử vào cuối danh sách. Độ phức tạp: O(1)." 
        new_node = Node(data)
        if self.head is None: # Trường hợp danh sách rỗng
            self.head = new_node
            self.tail = new_node
        else:
            # self.tail should always be valid if self.head is not None
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1

    def prepend(self, data: T) -> None:
        "Thêm phần tử vào đầu danh sách. Độ phức tạp: O(1)."
        new_node = Node(data)
        if self.head is None: # Trường hợp danh sách rỗng
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1

    def remove_first(self) -> T:
        """
        Xóa và trả về phần tử đầu tiên của danh sách. 
        Độ phức tạp: O(1).
        Raise IndexError nếu danh sách rỗng.
        """
        if self.head is None:
            raise IndexError("Không thể pop từ danh sách rỗng.")
        
        removed_data = self.head.data
        
        if self.head == self.tail:  # Trường hợp chỉ có 1 phần tử
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next
        
        self.length -= 1
        return removed_data
    
    def remove_by_value(self, data: T) -> bool:
        "Xóa phần tử đầu tiên có giá trị `data`. Độ phức tạp: O(N). Trả về True nếu xóa thành công, ngược lại False." 
        if self.head is None:
            return False

        if self.head.data == data:
            if self.head == self.tail: # Trường hợp chỉ có 1 phần tử
                self.head = None
                self.tail = None
            else:
                self.head = self.head.next
            self.length -= 1
            return True

        current = self.head
        while current.next and current.next.data != data:
            current = current.next
        
        if current.next: # Tìm thấy phần tử cần xóa
            if current.next == self.tail:
                self.tail = current # Cập nhật tail nếu phần tử bị xóa là tail
            current.next = current.next.next
            self.length -= 1
            return True
        return False # Không tìm thấy phần tử có giá trị data

    def remove_at_index(self, index: int) -> T:
        "Xóa phần tử tại vị trí (index) được chỉ định. Độ phức tạp: O(N). Trả về giá trị của phần tử bị xóa." 
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số (index) nằm ngoài phạm vi cho phép.")
        
        if index == 0:
            if self.head is None: # Không nên xảy ra nếu length > 0
                 raise RuntimeError("Lỗi logic: head là None mặc dù length > 0.")
            removed_data = self.head.data
            if self.head == self.tail: # Trường hợp chỉ có 1 phần tử
                self.head = None
                self.tail = None
            else:
                self.head = self.head.next
            self.length -= 1
            return removed_data

        current = self.head
        for _ in range(index - 1):
            if current:
                current = current.next
            else: # Không nên xảy ra
                raise RuntimeError("Lỗi logic khi duyệt LinkedList để xóa theo chỉ số.")

        if current and current.next: # current là nút đứng trước nút cần xóa
            removed_node = current.next
            removed_data = removed_node.data
            if removed_node == self.tail: # Nếu nút bị xóa là tail, cập nhật tail
                self.tail = current
            current.next = removed_node.next # Bỏ qua nút bị xóa
            self.length -= 1
            return removed_data
        # Trường hợp này không nên xảy ra nếu index hợp lệ và length > 0
        raise RuntimeError("Không thể xóa phần tử tại chỉ số (index) đã cho.")

    def get_at_index(self, index: int) -> T:
        "Lấy phần tử tại vị trí (index) được chỉ định. Độ phức tạp: O(N)." 
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số (index) nằm ngoài phạm vi cho phép.")
        current = self.head
        for _ in range(index):
            if current:
                current = current.next
            else: # Không nên xảy ra
                raise RuntimeError("Lỗi logic khi duyệt LinkedList để lấy phần tử theo chỉ số.")
        if current: 
            return current.data
        # Trường hợp này không nên xảy ra nếu index hợp lệ
        raise RuntimeError("Không thể lấy phần tử tại chỉ số (index) đã cho.")

    def get_node_at_index(self, index: int) -> Node[T] | None:
        "Lấy nút (Node) tại vị trí (index) được chỉ định. Độ phức tạp: O(N). Trả về None nếu index không hợp lệ." 
        if not (0 <= index < self.length):
            # Có thể raise IndexError thay vì trả về None nếu muốn hành vi nghiêm ngặt hơn
            return None 
        current = self.head
        for _ in range(index):
            if current:
                current = current.next
            else: # Không nên xảy ra nếu logic của các hàm gọi là đúng
                return None 
        return current

    def get_last(self) -> T | None:
        "Lấy phần tử cuối cùng của danh sách. Độ phức tạp: O(1). Trả về None nếu danh sách rỗng." 
        if self.tail:
            return self.tail.data
        return None

    def remove_last(self) -> T | None:
        "Xóa và trả về phần tử cuối cùng. Độ phức tạp: O(N) trong trường hợp xấu nhất (cần duyệt để tìm tail mới). O(1) nếu chỉ có 1 phần tử." 
        if self.is_empty():
            return None # Hoặc có thể raise IndexError("Không thể xóa phần tử cuối từ danh sách rỗng")
        
        removed_data: T
        if self.head == self.tail: # Trường hợp chỉ có một phần tử
            if self.head is None: # Kiểm tra an toàn, mặc dù is_empty đã check
                raise RuntimeError("Lỗi logic: head là None trong remove_last dù danh sách được cho là có 1 phần tử.")
            removed_data = self.head.data
            self.head = None
            self.tail = None
        else:
            # Duyệt để tìm nút ngay trước tail
            current = self.head
            # Kiểm tra current.next tồn tại trước khi truy cập current.next.next
            while current and current.next and current.next != self.tail:
                current = current.next
            
            if current and self.tail: # current giờ là nút đứng trước tail
                removed_data = self.tail.data
                current.next = None # Bỏ liên kết đến tail cũ
                self.tail = current # Cập nhật tail mới
            else: # Không nên xảy ra trong một danh sách nhất quán có độ dài > 1
                raise RuntimeError("Lỗi logic trong remove_last cho danh sách có nhiều phần tử.")

        self.length -= 1
        return removed_data

    def contains(self, data: T) -> bool:
        "Kiểm tra xem một phần tử có tồn tại trong danh sách hay không. Độ phức tạp: O(N)." 
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def is_empty(self) -> bool:
        "Kiểm tra xem danh sách có rỗng hay không. Độ phức tạp: O(1)." 
        return self.length == 0

    def get_length(self) -> int:
        "Trả về số lượng phần tử trong danh sách. Độ phức tạp: O(1)." 
        return self.length

    def __iter__(self):
        "Trả về một iterator để duyệt qua các phần tử trong danh sách." 
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __str__(self) -> str:
        "Trả về biểu diễn chuỗi của danh sách liên kết." 
        items = []
        current = self.head
        while current:
            items.append(str(current.data))
            current = current.next
        return " -> ".join(items) if items else "LinkedList()"

    def __repr__(self) -> str:
        "Trả về biểu diễn chuỗi chính thức của danh sách liên kết, có thể dùng để tạo lại đối tượng." 
        return f"LinkedList([{', '.join(repr(item) for item in self)}])"

    def __len__(self) -> int:
        "Trả về độ dài của danh sách liên kết, cho phép sử dụng hàm len()." 
        return self.length