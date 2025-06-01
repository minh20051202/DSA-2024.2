from typing import Generic, TypeVar, Iterable, Iterator

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, data: T):
        self.data: T = data
        self.next: Node[T] | None = None

    def __repr__(self):
        return f"Node({self.data})"

class LinkedList(Generic[T]):
    """
    Danh sách liên kết đơn
    
    Phương thức:
    - __init__(initial_data): Khởi tạo danh sách - O(n) nếu có initial_data, O(1) nếu không
    - append(data): Thêm phần tử vào cuối danh sách - O(1)
    - prepend(data): Thêm phần tử vào đầu danh sách - O(1)
    - remove_first(): Xóa và trả về phần tử đầu tiên - O(1)
    - remove_last(): Xóa và trả về phần tử cuối cùng - O(n)
    - remove_by_value(data): Xóa phần tử đầu tiên có giá trị data - O(n)
    - remove_at_index(index): Xóa phần tử tại vị trí index - O(n)
    - get_at_index(index): Lấy phần tử tại vị trí index - O(n)
    - get_node_at_index(index): Lấy node tại vị trí index - O(n)
    - set_at_index(index, value): Gán giá trị mới cho phần tử tại vị trí index - O(n)
    - get_last(): Lấy phần tử cuối cùng - O(1)
    - contains(data): Kiểm tra sự tồn tại của phần tử - O(n)
    - is_empty(): Kiểm tra danh sách rỗng - O(1)
    - clear(): Xóa toàn bộ danh sách - O(1)
    - __iter__(): Iterator để duyệt danh sách - O(1)
    - __len__(): Lấy độ dài danh sách - O(1)
    """
    
    def __init__(self, initial_data: Iterable[T] | None = None):
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self.length: int = 0
        
        if initial_data:
            for item in initial_data:
                self.append(item)

    def append(self, data: T) -> None:
        new_node = Node(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1

    def prepend(self, data: T) -> None:
        new_node = Node(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.length += 1

    def set_at_index(self, index: int, value: T) -> None:
        """
        Gán giá trị mới cho phần tử tại vị trí index.
        
        Raises:
            IndexError: Nếu index không hợp lệ.
        """
        node = self.get_node_at_index(index)
        node.data = value

    def remove_first(self) -> T:
        if self.head is None:
            raise IndexError("Không thể xóa phần tử từ danh sách rỗng")
        removed_data = self.head.data
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = self.head.next
        self.length -= 1
        return removed_data
    
    def remove_by_value(self, data: T) -> bool:
        if self.head is None:
            return False
        if self.head.data == data:
            if self.head == self.tail:
                self.head = self.tail = None
            else:
                self.head = self.head.next
            self.length -= 1
            return True
        current = self.head
        while current.next and current.next.data != data:
            current = current.next
        if current.next:
            node_to_remove = current.next
            if node_to_remove == self.tail:
                self.tail = current
            current.next = node_to_remove.next
            self.length -= 1
            return True
        return False

    def remove_at_index(self, index: int) -> T:
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số nằm ngoài phạm vi")
        if index == 0:
            return self.remove_first()
        current = self.head
        for _ in range(index - 1):
            assert current is not None
            current = current.next
        assert current is not None and current.next is not None
        node_to_remove = current.next
        removed_data = node_to_remove.data
        if node_to_remove == self.tail:
            self.tail = current
        current.next = node_to_remove.next
        self.length -= 1
        return removed_data

    def get_at_index(self, index: int) -> T:
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số nằm ngoài phạm vi")
        current = self.head
        for _ in range(index):
            assert current is not None
            current = current.next
        assert current is not None
        return current.data

    def get_node_at_index(self, index: int) -> Node[T]:
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số nằm ngoài phạm vi")
        current = self.head
        for _ in range(index):
            assert current is not None
            current = current.next
        assert current is not None
        return current

    def get_last(self) -> T | None:
        if self.tail:
            return self.tail.data
        return None

    def remove_last(self) -> T | None:
        if self.is_empty():
            return None
        if self.head == self.tail:
            assert self.head is not None
            removed_data = self.head.data
            self.head = self.tail = None
        else:
            current = self.head
            while current.next and current.next != self.tail:
                current = current.next
            assert current is not None and self.tail is not None
            removed_data = self.tail.data
            current.next = None
            self.tail = current
        self.length -= 1
        return removed_data

    def contains(self, data: T) -> bool:
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def is_empty(self) -> bool:
        return self.length == 0

    def clear(self) -> None:
        """Xóa toàn bộ danh sách, thiết lập về trạng thái rỗng."""
        self.head = None
        self.tail = None
        self.length = 0

    def __iter__(self) -> Iterator[T]:
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __len__(self) -> int:
        return self.length

