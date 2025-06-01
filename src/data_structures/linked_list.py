"""
Triển khai Linked List (Danh sách liên kết đơn)
"""

from typing import Generic, TypeVar, Iterable, Iterator

T = TypeVar('T')

class Node(Generic[T]):
    """
    Node cho Linked List - đại diện cho một nút trong danh sách liên kết.
    
    Mỗi node chứa dữ liệu và con trỏ tới node tiếp theo trong danh sách.
    """
    
    def __init__(self, data: T):
        """
        Khởi tạo một node mới với dữ liệu cho trước.
        
        Tham số:
            data (T): Dữ liệu được lưu trữ trong node.
        """
        self.data: T = data
        self.next: Node[T] | None = None

class LinkedList(Generic[T]):
    """
    LINKED LIST - DANH SÁCH LIÊN KẾT ĐƠN
    
    PHƯƠNG THỨC:
    - __init__(initial_data): Khởi tạo danh sách - O(n) nếu có initial_data, O(1) nếu không
    - append(data): Thêm phần tử vào cuối danh sách - O(1)
    - prepend(data): Thêm phần tử vào đầu danh sách - O(1)
    - remove_first(): Xóa và trả về phần tử đầu tiên - O(1)
    - remove_last(): Xóa và trả về phần tử cuối cùng - O(n)
    - remove_by_value(data): Xóa phần tử đầu tiên có giá trị data - O(n)
    - remove_at_index(index): Xóa phần tử tại vị trí index - O(n)
    - get_at_index(index): Lấy phần tử tại vị trí index - O(n)
    - get_node_at_index(index): Lấy node tại vị trí index - O(n)
    - get_last(): Lấy phần tử cuối cùng - O(1)
    - contains(data): Kiểm tra sự tồn tại của phần tử - O(n)
    - is_empty(): Kiểm tra danh sách rỗng - O(1)
    - get_length(): Lấy số lượng phần tử - O(1)
    - __iter__(): Iterator để duyệt danh sách - O(1)
    - __len__(): Lấy độ dài danh sách - O(1)
    """
    
    def __init__(self, initial_data: Iterable[T] | None = None):
        """
        Khởi tạo một danh sách liên kết mới.
        
        Tham số:
            initial_data (Iterable[T] | None): Dữ liệu ban đầu để thêm vào danh sách.
                                              None nếu khởi tạo danh sách rỗng.
        """
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self.length: int = 0
        
        # Thêm dữ liệu ban đầu nếu được cung cấp
        if initial_data:
            for item in initial_data:
                self.append(item)

    def append(self, data: T) -> None:
        """
        Thêm phần tử vào cuối danh sách.
        
        Tham số:
            data (T): Dữ liệu cần thêm vào cuối danh sách.
        """
        new_node = Node(data)
        
        if self.head is None:  # Danh sách rỗng
            self.head = new_node
            self.tail = new_node
        else:
            # Danh sách không rỗng, tail luôn tồn tại
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
            
        self.length += 1

    def prepend(self, data: T) -> None:
        """
        Thêm phần tử vào đầu danh sách.
        
        Tham số:
            data (T): Dữ liệu cần thêm vào đầu danh sách.
        """
        new_node = Node(data)
        
        if self.head is None:  # Danh sách rỗng
            self.head = new_node
            self.tail = new_node
        else:
            # Danh sách không rỗng
            new_node.next = self.head
            self.head = new_node
            
        self.length += 1

    def remove_first(self) -> T:
        """
        Xóa và trả về phần tử đầu tiên của danh sách.
        
        Trả về:
            T: Phần tử đầu tiên đã được xóa.
            
        Ngoại lệ:
            IndexError: Nếu danh sách rỗng.
        """
        if self.head is None:
            raise IndexError("Không thể xóa phần tử từ danh sách rỗng")
        
        removed_data = self.head.data
        
        if self.head == self.tail:  # Chỉ có một phần tử
            self.head = None
            self.tail = None
        else:
            # Có nhiều hơn một phần tử
            self.head = self.head.next
        
        self.length -= 1
        return removed_data
    
    def remove_by_value(self, data: T) -> bool:
        """
        Xóa phần tử đầu tiên có giá trị bằng data.
        
        Tham số:
            data (T): Giá trị của phần tử cần xóa.
            
        Trả về:
            bool: True nếu xóa thành công, False nếu không tìm thấy.
        """
        if self.head is None:
            return False

        # Kiểm tra phần tử đầu tiên
        if self.head.data == data:
            if self.head == self.tail:  # Chỉ có một phần tử
                self.head = None
                self.tail = None
            else:
                self.head = self.head.next
            self.length -= 1
            return True

        # Tìm kiếm trong các phần tử còn lại
        current = self.head
        while current.next and current.next.data != data:
            current = current.next
        
        if current.next:  # Tìm thấy phần tử cần xóa
            node_to_remove = current.next
            
            # Cập nhật tail nếu phần tử bị xóa là phần tử cuối
            if node_to_remove == self.tail:
                self.tail = current
                
            current.next = node_to_remove.next
            self.length -= 1
            return True
            
        return False  # Không tìm thấy phần tử

    def remove_at_index(self, index: int) -> T:
        """
        Xóa phần tử tại vị trí index được chỉ định.
        
        Tham số:
            index (int): Vị trí của phần tử cần xóa.
            
        Trả về:
            T: Phần tử đã được xóa.
            
        Ngoại lệ:
            IndexError: Nếu index nằm ngoài phạm vi [0, length-1].
        """
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số nằm ngoài phạm vi")
        
        # Xóa phần tử đầu tiên
        if index == 0:
            return self.remove_first()

        # Tìm node trước node cần xóa
        current = self.head
        for _ in range(index - 1):
            assert current is not None  # Không nên xảy ra với index hợp lệ
            current = current.next

        # current giờ trỏ tới node trước node cần xóa
        assert current is not None and current.next is not None
        node_to_remove = current.next
        removed_data = node_to_remove.data
        
        # Cập nhật tail nếu node bị xóa là tail
        if node_to_remove == self.tail:
            self.tail = current
            
        current.next = node_to_remove.next
        self.length -= 1
        return removed_data

    def get_at_index(self, index: int) -> T:
        """
        Lấy phần tử tại vị trí index được chỉ định.
        
        Tham số:
            index (int): Vị trí của phần tử cần lấy.
            
        Trả về:
            T: Phần tử tại vị trí index.
            
        Ngoại lệ:
            IndexError: Nếu index nằm ngoài phạm vi [0, length-1].
        """
        if not (0 <= index < self.length):
            raise IndexError("Chỉ số nằm ngoài phạm vi")
            
        current = self.head
        for _ in range(index):
            assert current is not None  # Không nên xảy ra với index hợp lệ
            current = current.next
            
        assert current is not None
        return current.data

    def get_node_at_index(self, index: int) -> Node[T] | None:
        """
        Lấy node tại vị trí index được chỉ định.
        
        Tham số:
            index (int): Vị trí của node cần lấy.
            
        Trả về:
            Node[T] | None: Node tại vị trí index, hoặc None nếu index không hợp lệ.
        """
        if not (0 <= index < self.length):
            return None
            
        current = self.head
        for _ in range(index):
            if current is None:  # Không nên xảy ra với length nhất quán
                return None
            current = current.next
            
        return current

    def get_last(self) -> T | None:
        """
        Lấy phần tử cuối cùng của danh sách.
        
        Trả về:
            T | None: Phần tử cuối cùng, hoặc None nếu danh sách rỗng.
        """
        if self.tail:
            return self.tail.data
        return None

    def remove_last(self) -> T | None:
        """
        Xóa và trả về phần tử cuối cùng của danh sách.
        
        Trả về:
            T | None: Phần tử cuối cùng đã xóa, hoặc None nếu danh sách rỗng.
        """
        if self.is_empty():
            return None
        
        if self.head == self.tail:  # Chỉ có một phần tử
            assert self.head is not None
            removed_data = self.head.data
            self.head = None
            self.tail = None
        else:
            # Tìm node trước tail
            current = self.head
            while current and current.next and current.next != self.tail:
                current = current.next
            
            assert current is not None and self.tail is not None
            removed_data = self.tail.data
            current.next = None  # Bỏ liên kết đến tail cũ
            self.tail = current  # Cập nhật tail mới

        self.length -= 1
        return removed_data

    def contains(self, data: T) -> bool:
        """
        Kiểm tra xem một phần tử có tồn tại trong danh sách hay không.
        
        Tham số:
            data (T): Giá trị cần kiểm tra.
            
        Trả về:
            bool: True nếu phần tử tồn tại, False nếu không.
        """
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def is_empty(self) -> bool:
        """
        Kiểm tra xem danh sách có rỗng hay không.
        
        Trả về:
            bool: True nếu danh sách rỗng, False nếu không.
        """
        return self.length == 0

    def get_length(self) -> int:
        """
        Lấy số lượng phần tử trong danh sách.
        
        Trả về:
            int: Số lượng phần tử hiện có trong danh sách.
        """
        return self.length

    def __iter__(self) -> Iterator[T]:
        """
        Trả về iterator để duyệt qua các phần tử trong danh sách.
        
        Trả về:
            Iterator[T]: Iterator cho các phần tử trong danh sách.
        """
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __len__(self) -> int:
        """
        Lấy độ dài của danh sách.
        
        Trả về:
            int: Số lượng phần tử trong danh sách.
        """
        return self.length
    
    def get_at(self, index):
        "Trả về dữ liệu của phần tử tại vị trí (index) được chỉ định trong danh sách."
        current = self.head
        for i in range(index):
            if current is None:
                raise IndexError("Index out of bounds")
            current = current.next
        if current is None:
            raise IndexError("Index out of bounds")
        return current.data

    def set_at(self, index: int, value: T) -> None:
        "Gán giá trị mới cho phần tử tại vị trí (index) được chỉ định trong danh sách."
        current = self.head
        for i in range(index):
            if current is None:
                raise IndexError("Index out of bounds")  # Vượt quá độ dài danh sách
            current = current.next
        if current is None:
            raise IndexError("Index out of bounds")
        current.data = value