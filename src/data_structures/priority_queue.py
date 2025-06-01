from typing import Any, TypeVar, Generic, Callable
from .array import Array

# Biến kiểu cho PriorityQueue dùng chung (generic)
T = TypeVar('T')

class PriorityQueueItem(Generic[T]):
    """
    Lớp để lưu một mục (item) và độ ưu tiên (priority) của nó trong Hàng Đợi Ưu Tiên.
    
    Thuộc tính:
        item (T): Dữ liệu thực tế được lưu trữ.
        priority (Any): Độ ưu tiên của item, có thể là số hoặc đối tượng phức tạp.
    """
    
    def __init__(self, item: T, priority: Any):
        """
        Khởi tạo một mục trong hàng đợi ưu tiên.

        Tham số:
            item (T): Dữ liệu cần lưu trữ.
            priority (Any): Độ ưu tiên của item.
        """
        self.item: T = item
        self.priority: Any = priority

    def __lt__(self, other: 'PriorityQueueItem[T]') -> bool:
        """
        So sánh độ ưu tiên với một PriorityQueueItem khác.
        Mặc định cho min-heap (hàng đợi ưu tiên nhỏ nhất) nếu độ ưu tiên là số.

        Tham số:
            other (PriorityQueueItem[T]): Item khác để so sánh.

        Trả về:
            bool: True nếu item này có độ ưu tiên nhỏ hơn item khác.

        Ngoại lệ:
            TypeError: Nếu không thể so sánh các độ ưu tiên không phải số.
        """
        if isinstance(self.priority, (int, float)) and isinstance(other.priority, (int, float)):
            return self.priority < other.priority
        raise TypeError("Không thể so sánh các độ ưu tiên không phải là số mà không có hàm so sánh (comparator).")

class PriorityQueue(Generic[T]):
    """
    PRIORITY QUEUE - HÀNG ĐỢI ƯU TIÊN
    
    Cấu trúc dữ liệu hàng đợi ưu tiên được triển khai bằng binary heap.
    Mặc định là min-heap (phần tử có độ ưu tiên nhỏ nhất được lấy ra trước).
    Có thể tùy chỉnh thành max-heap hoặc thứ tự ưu tiên khác thông qua hàm so sánh.
    
    PHƯƠNG THỨC:
    - __init__(comparator): Khởi tạo hàng đợi với hàm so sánh tùy chọn - O(1)
    - enqueue(item, priority): Thêm phần tử vào hàng đợi - O(log n)
    - dequeue(): Lấy và xóa phần tử có độ ưu tiên cao nhất - O(log n)
    - peek(): Xem phần tử có độ ưu tiên cao nhất - O(1)
    - is_empty(): Kiểm tra hàng đợi có rỗng không - O(1)
    - __len__(): Trả về số lượng phần tử - O(1)
    """
    
    def __init__(self, comparator: Callable[[T, T], bool] | None = None):
        """
        Khởi tạo hàng đợi ưu tiên mới.

        Tham số:
            comparator (Callable[[T, T], bool] | None): Hàm so sánh tùy chọn.
                Nhận 2 item và trả về True nếu item1 có độ ưu tiên cao hơn item2.
        """
        self.heap: Array[PriorityQueueItem[T]] = Array[PriorityQueueItem[T]]()
        self.comparator: Callable[[T, T], bool] | None = comparator

    def __len__(self) -> int:
        """
        Lấy số lượng phần tử trong hàng đợi.

        Trả về:
            int: Số lượng phần tử trong hàng đợi.
        """
        return len(self.heap)

    def is_empty(self) -> bool:
        """
        Kiểm tra xem hàng đợi có rỗng không.

        Trả về:
            bool: True nếu hàng đợi rỗng, False nếu có phần tử.
        """
        return len(self.heap) == 0

    def enqueue(self, item: T, priority: Any) -> None:
        """
        Thêm một mục vào hàng đợi với độ ưu tiên được chỉ định.

        Tham số:
            item (T): Dữ liệu cần thêm vào hàng đợi.
            priority (Any): Độ ưu tiên của item.
        """
        pq_item = PriorityQueueItem(item, priority)
        self.heap.append(pq_item)
        self._heapify_up(len(self.heap) - 1)

    def dequeue(self) -> T:
        """
        Lấy và xóa mục có độ ưu tiên cao nhất khỏi hàng đợi.

        Trả về:
            T: Item có độ ưu tiên cao nhất.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.
        """
        if self.is_empty():
            raise IndexError("Không thể thực hiện dequeue từ một PriorityQueue rỗng.")
        
        highest_priority_item_wrapper = self.heap.get(0)
        
        if len(self.heap) == 1:
            self.heap.pop()
        else:
            last_item_wrapper = self.heap.pop()
            self.heap.set(0, last_item_wrapper)
            self._heapify_down(0)
            
        return highest_priority_item_wrapper.item

    def peek(self) -> T:
        """
        Xem mục có độ ưu tiên cao nhất trong hàng đợi mà không xóa nó.

        Trả về:
            T: Item có độ ưu tiên cao nhất.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.
        """
        if self.is_empty():
            raise IndexError("Không thể thực hiện peek từ một PriorityQueue rỗng.")
        return self.heap.get(0).item

    def _compare_items(self, item1_wrapper: PriorityQueueItem[T], item2_wrapper: PriorityQueueItem[T]) -> bool:
        """
        So sánh hai đối tượng PriorityQueueItem dựa trên hàm so sánh được cung cấp hoặc theo mặc định.

        Tham số:
            item1_wrapper (PriorityQueueItem[T]): Item thứ nhất để so sánh.
            item2_wrapper (PriorityQueueItem[T]): Item thứ hai để so sánh.

        Trả về:
            bool: True nếu item1 có độ ưu tiên cao hơn item2.

        Ngoại lệ:
            TypeError: Nếu không thể so sánh mà không có hàm comparator.
        """
        if self.comparator:
            return self.comparator(item1_wrapper.item, item2_wrapper.item)
        else:
            try:
                return item1_wrapper < item2_wrapper
            except TypeError as e:
                raise TypeError(
                    "PriorityQueue cần một hàm so sánh (comparator) nếu độ ưu tiên (priority) của các mục (item) không phải là số, "
                    "hoặc nếu bạn muốn một thứ tự ưu tiên tùy chỉnh. "
                    "Hàm so sánh nên nhận 2 mục (item) và trả về True nếu item1 có độ ưu tiên cao hơn item2."
                ) from e

    def _parent(self, index: int) -> int:
        """
        Tính chỉ số của nút cha trong heap.

        Tham số:
            index (int): Chỉ số của nút con.

        Trả về:
            int: Chỉ số của nút cha.
        """
        return (index - 1) // 2

    def _left_child(self, index: int) -> int:
        """
        Tính chỉ số của nút con trái trong heap.

        Tham số:
            index (int): Chỉ số của nút cha.

        Trả về:
            int: Chỉ số của nút con trái.
        """
        return 2 * index + 1

    def _right_child(self, index: int) -> int:
        """
        Tính chỉ số của nút con phải trong heap.

        Tham số:
            index (int): Chỉ số của nút cha.

        Trả về:
            int: Chỉ số của nút con phải.
        """
        return 2 * index + 2

    def _swap(self, i: int, j: int) -> None:
        """
        Hoán đổi hai phần tử trong heap.

        Tham số:
            i (int): Chỉ số của phần tử thứ nhất.
            j (int): Chỉ số của phần tử thứ hai.
        """
        item_i = self.heap.get(i)
        item_j = self.heap.get(j)
        self.heap.set(i, item_j)
        self.heap.set(j, item_i)

    def _heapify_up(self, index: int) -> None:
        """
        Điều chỉnh heap từ dưới lên (vun đống lên) sau khi thêm một phần tử.
        Đảm bảo tính chất heap được duy trì bằng cách so sánh với nút cha và hoán đổi nếu cần.

        Tham số:
            index (int): Chỉ số của phần tử cần điều chỉnh.
        """
        parent_index = self._parent(index)
        while index > 0 and self._compare_items(self.heap.get(index), self.heap.get(parent_index)):
            self._swap(index, parent_index)
            index = parent_index
            parent_index = self._parent(index)

    def _heapify_down(self, index: int) -> None:
        """
        Điều chỉnh heap từ trên xuống (vun đống xuống) sau khi lấy một phần tử.
        Đảm bảo tính chất heap được duy trì bằng cách so sánh với các nút con và hoán đổi nếu cần.

        Tham số:
            index (int): Chỉ số của phần tử cần điều chỉnh.
        """
        highest_priority_idx = index
        left_idx = self._left_child(index)
        right_idx = self._right_child(index)
        current_heap_size = len(self.heap)

        if left_idx < current_heap_size and self._compare_items(self.heap.get(left_idx), self.heap.get(highest_priority_idx)):
            highest_priority_idx = left_idx

        if right_idx < current_heap_size and self._compare_items(self.heap.get(right_idx), self.heap.get(highest_priority_idx)):
            highest_priority_idx = right_idx

        if highest_priority_idx != index:
            self._swap(index, highest_priority_idx)
            self._heapify_down(highest_priority_idx)