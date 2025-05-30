from typing import Any, TypeVar, Generic, Callable
from .array import Array

# Biến kiểu cho PriorityQueue dùng chung (generic)
T = TypeVar('T')

class PriorityQueueItem(Generic[T]):
    """Lớp để lưu một mục (item) và độ ưu tiên (priority) của nó trong Hàng Đợi Ưu Tiên (PriorityQueue)."""
    def __init__(self, item: T, priority: Any):
        self.item: T = item
        self.priority: Any = priority # Độ ưu tiên có thể là số hoặc một đối tượng phức tạp

    def __lt__(self, other: 'PriorityQueueItem[T]') -> bool:
        # Mặc định cho min-heap (hàng đợi ưu tiên nhỏ nhất) nếu độ ưu tiên là số.
        # Sẽ bị ghi đè bởi hàm so sánh (comparator) nếu được cung cấp cho PriorityQueue.
        if isinstance(self.priority, (int, float)) and isinstance(other.priority, (int, float)):
            return self.priority < other.priority
        # Nếu không phải số hoặc comparator không được cung cấp, không thể so sánh mặc định
        raise TypeError("Không thể so sánh các độ ưu tiên không phải là số mà không có hàm so sánh (comparator).")

class PriorityQueue(Generic[T]):
    """Triển khai cấu trúc dữ liệu Hàng Đợi Ưu Tiên (PriorityQueue) tự tạo, sử dụng Min-Heap theo mặc định.
    Có thể tùy chỉnh thành Max-Heap hoặc thứ tự ưu tiên khác thông qua hàm so sánh (comparator)."""
    def __init__(self, comparator: Callable[[T, T], bool] | None = None):
        self.heap: Array[PriorityQueueItem[T]] = Array[PriorityQueueItem[T]]()
        # self._size sẽ được quản lý bởi len(self.heap)
        self.comparator: Callable[[T, T], bool] | None = comparator

    def _compare_items(self, item1_wrapper: PriorityQueueItem[T], item2_wrapper: PriorityQueueItem[T]) -> bool:
        """So sánh hai đối tượng PriorityQueueItem dựa trên hàm so sánh (comparator) được cung cấp hoặc theo mặc định."""
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
        return (index - 1) // 2

    def _left_child(self, index: int) -> int:
        return 2 * index + 1

    def _right_child(self, index: int) -> int:
        return 2 * index + 2

    def _swap(self, i: int, j: int) -> None:
        "Hoán đổi hai phần tử trong heap." 
        item_i = self.heap.get(i)
        item_j = self.heap.get(j)
        self.heap.set(i, item_j)
        self.heap.set(j, item_i)

    def _heapify_up(self, index: int) -> None:
        """Điều chỉnh heap từ dưới lên (vun đống lên) sau khi thêm một phần tử (enqueue)."""
        parent_index = self._parent(index)
        while index > 0 and self._compare_items(self.heap.get(index), self.heap.get(parent_index)):
            self._swap(index, parent_index)
            index = parent_index
            parent_index = self._parent(index)

    def _heapify_down(self, index: int) -> None:
        """Điều chỉnh heap từ trên xuống (vun đống xuống) sau khi lấy một phần tử (dequeue)."""
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

    def enqueue(self, item: T, priority: Any) -> None:
        "Thêm một mục (item) vào hàng đợi với độ ưu tiên (priority) được chỉ định." 
        pq_item = PriorityQueueItem(item, priority)
        self.heap.append(pq_item) # Array.append sẽ tự quản lý size và capacity
        self._heapify_up(len(self.heap) - 1)

    def dequeue(self) -> T:
        "Lấy và xóa mục (item) có độ ưu tiên cao nhất khỏi hàng đợi." 
        if self.is_empty():
            raise IndexError("Không thể thực hiện dequeue từ một PriorityQueue rỗng.")
        
        highest_priority_item_wrapper = self.heap.get(0)
        
        if len(self.heap) == 1:
            self.heap.pop() # Xóa phần tử duy nhất
        else:
            last_item_wrapper = self.heap.pop() # Xóa phần tử cuối, Array.size giảm đi 1
            self.heap.set(0, last_item_wrapper) # Đặt phần tử cuối (cũ) vào gốc
            self._heapify_down(0) # Vun đống từ gốc
            
        return highest_priority_item_wrapper.item

    def peek(self) -> T:
        "Xem (không xóa) mục (item) có độ ưu tiên cao nhất trong hàng đợi." 
        if self.is_empty():
            raise IndexError("Không thể thực hiện peek từ một PriorityQueue rỗng.")
        return self.heap.get(0).item

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def __len__(self) -> int:
        return len(self.heap)

    def __str__(self) -> str:
        items_str = []
        # Duyệt qua self.heap (là một Array), Array đã có __iter__
        for pq_item_wrapper in self.heap: # Array.__iter__ sẽ trả về các PriorityQueueItem
            items_str.append(str(pq_item_wrapper.item))
        return f"PriorityQueue([{', '.join(items_str)}])"

    def __repr__(self) -> str:
        return f"PriorityQueue(kich_thuoc={len(self.heap)})" 