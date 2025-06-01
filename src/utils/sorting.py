from src.data_structures.linked_list import LinkedList
from typing import TypeVar, List as PyList, Callable
from src.data_structures.array import Array

# Type variable cho các hàm sắp xếp generic
T = TypeVar('T')

def merge_sort(array: PyList[T], comparator: Callable[[T, T], bool] | None = None) -> PyList[T]:
    """Triển khai MergeSort. hàm so sánh (comparator) `comparator(a,b)` trả về True nếu a < b."""
    if len(array) <= 1:
        return array
        
    mid = len(array) // 2
    left_half = merge_sort(array[:mid], comparator)
    right_half = merge_sort(array[mid:], comparator)
    
    return _merge(left_half, right_half, comparator)

def _merge(left: PyList[T], right: PyList[T], comparator: Callable[[T, T], bool] | None) -> PyList[T]:
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        # Mặc định so sánh dùng < nếu không có hàm so sánh (comparator)
        should_take_left = False
        if comparator:
            should_take_left = comparator(left[i], right[j]) # True nếu left[i] < right[j]
        else:
            try:
                should_take_left = left[i] < right[j]
            except TypeError:
                 raise TypeError("Không thể so sánh các phần tử nếu không có hàm so sánh (comparator) hoặc __lt__")

        if should_take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort(array: PyList[T], comparator: Callable[[T, T], bool] | None = None) -> None:
    """Triển khai QuickSort (sắp xếp tại chỗ - in-place). hàm so sánh (comparator) `comparator(a,b)` trả về True nếu a < b."""
    _quick_sort_recursive(array, 0, len(array) - 1, comparator)

def _quick_sort_recursive(array: PyList[T], low: int, high: int, comparator: Callable[[T, T], bool] | None) -> None:
    if low < high:
        pivot_index = _partition(array, low, high, comparator)
        _quick_sort_recursive(array, low, pivot_index - 1, comparator)
        _quick_sort_recursive(array, pivot_index + 1, high, comparator)
        
def _partition(array: PyList[T], low: int, high: int, comparator: Callable[[T, T], bool] | None) -> int:
    pivot = array[high]
    i = low - 1 # Chỉ số của phần tử nhỏ hơn pivot
    
    for j in range(low, high):
        should_swap = False
        if comparator:
            # array[j] <= pivot tương đương với comparator(array[j], pivot) HOẶC array[j] == pivot
            # Nếu comparator(a,b) là a < b, thì (a <= b) là (a < b hoặc a == b)
            should_swap = comparator(array[j], pivot) or array[j] == pivot
        else:
            try:
                should_swap = array[j] <= pivot
            except TypeError:
                raise TypeError("Không thể so sánh các phần tử nếu không có hàm so sánh (comparator) hoặc __le__")

        if should_swap:
            i += 1
            array[i], array[j] = array[j], array[i] # Hoán đổi
            
    array[i + 1], array[high] = array[high], array[i + 1] # Đưa pivot về đúng vị trí
    return i + 1

def heap_sort(array: PyList[T], comparator: Callable[[T, T], bool] | None = None) -> None:
    """Triển khai HeapSort (sắp xếp tại chỗ - in-place).
    Hàm so sánh (comparator) `comparator(a,b)` trả về True nếu `a` nên được coi là "lớn hơn" hoặc có "ưu tiên cao hơn" `b` (cho max-heap).
    Nếu không có comparator, mặc định sử dụng `a > b`."""
    n = len(array)
    
    # Xây dựng max-heap.
    effective_comparator = comparator
    if comparator is None:
        # Tạo hàm so sánh (comparator) mặc định cho max-heap nếu không có
        def default_max_heap_comparator(a, b): 
            try: return a > b
            except TypeError: raise TypeError("Không thể so sánh > cho heap_sort nếu không có hàm so sánh (comparator)")
        effective_comparator = default_max_heap_comparator

    for i in range(n // 2 - 1, -1, -1):
        _heapify_down_for_sort(array, n, i, effective_comparator)
        
    # Trích xuất từng phần tử từ heap
    for i in range(n - 1, 0, -1):
        array[0], array[i] = array[i], array[0] # Hoán đổi root (max) với phần tử cuối
        _heapify_down_for_sort(array, i, 0, effective_comparator) # Heapify lại trên heap đã thu nhỏ
        
def _heapify_down_for_sort(array: PyList[T], n: int, i: int, comparator: Callable[[T, T], bool]) -> None:
    """Hàm heapify cho HeapSort. 
    Hàm so sánh (comparator) `comparator(a,b)` trả về True nếu `a` nên được coi là "lớn hơn" hoặc có "ưu tiên cao hơn" `b`."""
    largest_or_smallest = i # Chỉ số của phần tử lớn nhất (cho max-heap) hoặc nhỏ nhất (cho min-heap)
    left = 2 * i + 1
    right = 2 * i + 2
    
    # So sánh với left child
    if left < n and comparator(array[left], array[largest_or_smallest]):
        largest_or_smallest = left
        
    # So sánh với right child
    if right < n and comparator(array[right], array[largest_or_smallest]):
        largest_or_smallest = right
        
    if largest_or_smallest != i:
        array[i], array[largest_or_smallest] = array[largest_or_smallest], array[i]
        _heapify_down_for_sort(array, n, largest_or_smallest, comparator) 

# --- Merge Sort for LinkedList ---

def _merge_linked_lists(left: 'LinkedList[T]', right: 'LinkedList[T]', comparator: Callable[[T, T], bool] | None) -> 'LinkedList[T]':
    """Trộn hai LinkedList đã sắp xếp thành một LinkedList mới đã sắp xếp."""
    merged = LinkedList[T]()
    left_node = left.head
    right_node = right.head

    while left_node is not None and right_node is not None:
        should_take_left = False
        if comparator:
            should_take_left = comparator(left_node.data, right_node.data)
        else:
            try:
                # Mặc định so sánh dùng <
                should_take_left = left_node.data < right_node.data
            except TypeError:
                raise TypeError("Không thể so sánh các phần tử LinkedList nếu không có hàm so sánh (comparator) hoặc __lt__")

        if should_take_left:
            merged.append(left_node.data)
            left_node = left_node.next
        else:
            merged.append(right_node.data)
            right_node = right_node.next

    # Nối các phần tử còn lại (nếu có)
    while left_node is not None:
        merged.append(left_node.data)
        left_node = left_node.next
    
    while right_node is not None:
        merged.append(right_node.data)
        right_node = right_node.next
        
    return merged

def merge_sort_linked_list(linked_list_to_sort: 'LinkedList[T]', comparator: Callable[[T, T], bool] | None = None) -> 'LinkedList[T]':
    """
    Sắp xếp một LinkedList bằng thuật toán MergeSort.
    Trả về một LinkedList mới đã được sắp xếp. LinkedList gốc không bị thay đổi.
    comparator(a,b) trả về True nếu a < b.
    """
    if linked_list_to_sort.is_empty() or len(linked_list_to_sort) <= 1:
        # Trả về một bản sao của danh sách nếu nó rỗng hoặc chỉ có 1 phần tử
        copy_list = LinkedList[T]()
        for item in linked_list_to_sort:
            copy_list.append(item)
        return copy_list
    
    # Chia danh sách thành hai nửa (điều này cần phải tạo bản sao hoặc cẩn thận không thay đổi list gốc)
    # Cách tiếp cận an toàn hơn là tạo các danh sách mới cho left_half và right_half từ dữ liệu
    left_half_data, right_half_data = _split_linked_list_to_data_lists(linked_list_to_sort)

    sorted_left_half = merge_sort_linked_list(left_half_data, comparator)
    sorted_right_half = merge_sort_linked_list(right_half_data, comparator)
    
    return _merge_linked_lists(sorted_left_half, sorted_right_half, comparator)

# Helper for merge_sort_linked_list to avoid modifying original list during split
# and to ensure we are dealing with new lists for recursion.
def _split_linked_list_to_data_lists(source_list: 'LinkedList[T]') -> tuple['LinkedList[T]', 'LinkedList[T]']:
    left_list = LinkedList[T]()
    right_list = LinkedList[T]()
    if source_list.is_empty() or source_list.head is None:
        return left_list, right_list

    if source_list.head.next is None: # Single element list
        left_list.append(source_list.head.data)
        return left_list, right_list

    slow = source_list.head
    fast = source_list.head.next

    # Move fast two steps and slow one step
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    
    # slow is now at the node before the midpoint (or the midpoint itself in odd length lists)
    # Populate left_list up to and including slow's data
    current = source_list.head
    while current is not None:
        left_list.append(current.data)
        if current == slow:
            break
        current = current.next
    
    # Populate right_list from slow.next onwards
    if slow.next is not None:
        current = slow.next
        while current is not None:
            right_list.append(current.data)
            current = current.next
            
    return left_list, right_list

# --- Merge Sort for Array ---

def merge_sort_array(custom_array: Array[T], comparator: Callable[[T, T], bool] | None = None) -> Array[T]:
    """Triển khai MergeSort cho Array tùy chỉnh.
    Hàm so sánh (comparator) `comparator(a,b)` trả về True nếu a < b."""
    n = len(custom_array)
    if n <= 1:
        # Trả về một bản sao của Array nếu nó rỗng hoặc chỉ có 1 phần tử
        # Điều này quan trọng để đảm bảo không trả về cùng một đối tượng có thể thay đổi
        new_arr = Array[T](capacity=n if n > 0 else 1) 
        for i in range(n):
            new_arr.append(custom_array.get(i))
        return new_arr
        
    mid = n // 2
    
    left_half_arr = Array[T](capacity=mid if mid > 0 else 1)
    for i in range(mid):
        left_half_arr.append(custom_array.get(i))
        
    right_half_arr = Array[T](capacity=n - mid if (n - mid) > 0 else 1)
    for i in range(mid, n):
        right_half_arr.append(custom_array.get(i))
    
    sorted_left_half = merge_sort_array(left_half_arr, comparator)
    sorted_right_half = merge_sort_array(right_half_arr, comparator)
    
    return _merge_array(sorted_left_half, sorted_right_half, comparator)

def _merge_array(left: Array[T], right: Array[T], comparator: Callable[[T, T], bool] | None) -> Array[T]:
    result_capacity = len(left) + len(right)
    result_arr = Array[T](capacity=result_capacity if result_capacity > 0 else 1)
    i = 0 # index cho left
    j = 0 # index cho right
    
    len_left = len(left)
    len_right = len(right)

    while i < len_left and j < len_right:
        should_take_left = False
        left_val = left.get(i)
        right_val = right.get(j)

        if comparator:
            should_take_left = comparator(left_val, right_val)
        else:
            try:
                should_take_left = left_val < right_val
            except TypeError:
                 raise TypeError("Không thể so sánh các phần tử Array nếu không có hàm so sánh (comparator) hoặc __lt__")

        if should_take_left:
            result_arr.append(left_val)
            i += 1
        else:
            result_arr.append(right_val)
            j += 1
            
    # Nối các phần tử còn lại từ left (nếu có)
    while i < len_left:
        result_arr.append(left.get(i))
        i += 1
        
    # Nối các phần tử còn lại từ right (nếu có)
    while j < len_right:
        result_arr.append(right.get(j))
        j += 1
        
    return result_arr 