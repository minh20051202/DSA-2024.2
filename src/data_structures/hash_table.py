from typing import TypeVar, Generic, Iterator, Tuple
from .linked_list import LinkedList
from .array import Array

K = TypeVar('K')
V = TypeVar('V')

class HashEntry(Generic[K, V]):
    """
    Entry cho Hash Table - lưu cặp key-value.
    
    Lớp này đại diện cho một entry trong bảng băm, chứa một cặp key-value.
    Được sử dụng trong chaining để giải quyết collision.
    """
    
    def __init__(self, key: K, value: V):
        """
        Khởi tạo một entry mới với key và value.
        
        Tham số:
            key (K): Khóa của entry.
            value (V): Giá trị tương ứng với khóa.
        """
        self.key: K = key
        self.value: V = value

class HashTable(Generic[K, V]):
    """
    HASH TABLE - BẢNG BĂM
    
    Cấu trúc dữ liệu hash table sử dụng separate chaining để xử lý collision.
    Sử dụng Array để lưu trữ các bucket và LinkedList cho mỗi bucket.
    Tự động resize khi load factor vượt ngưỡng.
    
    PHƯƠNG THỨC:
    - __init__(capacity, load_factor_threshold): Khởi tạo hash table - O(capacity)
    - put(key, value): Thêm/cập nhật cặp key-value - O(1) trung bình, O(n) worst case
    - get(key, default): Lấy giá trị theo key - O(1) trung bình, O(n) worst case
    - remove(key): Xóa entry theo key - O(1) trung bình, O(n) worst case
    - contains_key(key): Kiểm tra key có tồn tại - O(1) trung bình, O(n) worst case
    - keys(): Lấy tất cả keys - O(n)
    - values(): Lấy tất cả values - O(n)
    - items(): Lấy tất cả cặp key-value - O(n)
    - clear(): Xóa toàn bộ entries - O(capacity)
    - copy(): Tạo bản sao nông - O(n)
    - _resize(new_capacity): Thay đổi kích thước hash table - O(n)
    """
    
    DEFAULT_CAPACITY = 16
    DEFAULT_LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = DEFAULT_CAPACITY, 
                 load_factor_threshold: float = DEFAULT_LOAD_FACTOR_THRESHOLD):
        """
        Khởi tạo một hash table mới.
        
        Tham số:
            capacity (int): Dung lượng ban đầu (số bucket).
            load_factor_threshold (float): Ngưỡng load factor để trigger resize.
            
        Ngoại lệ:
            ValueError: Nếu capacity <= 0 hoặc load_factor_threshold không hợp lệ.
        """
        if capacity <= 0:
            raise ValueError("Dung lượng (capacity) phải là số dương")
        if not (0 < load_factor_threshold <= 1.0):
            raise ValueError("Ngưỡng hệ số tải (load factor threshold) phải trong khoảng (0, 1]")
            
        self.capacity: int = capacity
        self.buckets: Array[LinkedList[HashEntry[K,V]] | None] = Array(self.capacity)
        
        # Khởi tạo tất cả buckets với LinkedList rỗng
        for i in range(self.capacity):
            empty_ll = LinkedList[HashEntry[K,V]]()
            # Array.set sẽ tăng size khi index == current_size
            # Sau vòng lặp này, buckets.size sẽ bằng capacity
            self.buckets.set(i, empty_ll)
            
        self.num_elements: int = 0
        self.load_factor_threshold: float = load_factor_threshold

    def _hash(self, key: K) -> int:
        """
        Tính hash value cho key.
        
        Sử dụng hàm hash() built-in của Python và modulo với capacity.
        Đối với custom objects, cần implement __hash__().
        
        Tham số:
            key (K): Key cần tính hash.
            
        Trả về:
            int: Hash value trong khoảng [0, capacity-1].
        """
        return hash(key) % self.capacity

    def _get_bucket(self, key: K) -> LinkedList[HashEntry[K,V]]:
        """
        Lấy bucket (LinkedList) tương ứng với key.
        
        Tham số:
            key (K): Key để tìm bucket.
            
        Trả về:
            LinkedList[HashEntry[K,V]]: Bucket chứa các entries có cùng hash value.
        """
        index = self._hash(key)
        bucket = self.buckets.get(index)
        
        # Xử lý trường hợp bucket là None (không nên xảy ra với khởi tạo đúng)
        if bucket is None:
            new_ll = LinkedList[HashEntry[K,V]]()
            self.buckets.set(index, new_ll)
            return new_ll
            
        assert isinstance(bucket, LinkedList), "Bucket không phải là LinkedList"
        return bucket

    def put(self, key: K, value: V) -> None:
        """
        Thêm hoặc cập nhật cặp key-value trong hash table.
        
        Nếu key đã tồn tại, cập nhật value. Nếu chưa, thêm entry mới.
        Tự động resize nếu load factor vượt ngưỡng.
        
        Tham số:
            key (K): Khóa cần thêm/cập nhật.
            value (V): Giá trị tương ứng.
        """
        bucket = self._get_bucket(key)
        
        # Kiểm tra xem key đã tồn tại trong bucket chưa
        for entry_node in bucket:
            if entry_node.key == key:
                entry_node.value = value  # Cập nhật value
                return
        
        # Key chưa tồn tại, thêm entry mới
        bucket.append(HashEntry(key, value))
        self.num_elements += 1
        self._resize_if_needed()

    def get(self, key: K, default: V | None = None) -> V | None:
        """
        Lấy giá trị của key trong hash table.
        
        Tham số:
            key (K): Khóa cần tìm giá trị.
            default (V | None): Giá trị trả về nếu không tìm thấy key.
            
        Trả về:
            V | None: Giá trị tương ứng với key hoặc default nếu không tìm thấy.
        """
        bucket = self._get_bucket(key)
        for entry_node in bucket:
            if entry_node.key == key:
                return entry_node.value
        return default

    def remove(self, key: K) -> V | None:
        """
        Xóa key và giá trị tương ứng khỏi hash table.
        
        Tham số:
            key (K): Khóa cần xóa.
            
        Trả về:
            V | None: Giá trị bị xóa hoặc None nếu không tìm thấy key.
        """
        bucket = self._get_bucket(key)
        entry_to_remove = None
        
        # Tìm entry cần xóa
        for entry_node in bucket:
            if entry_node.key == key:
                entry_to_remove = entry_node
                break
        
        if entry_to_remove:
            # LinkedList cần có phương thức remove_by_value
            bucket.remove_by_value(entry_to_remove)
            self.num_elements -= 1
            return entry_to_remove.value
        return None

    def contains_key(self, key: K) -> bool:
        """
        Kiểm tra key có tồn tại trong hash table không.
        
        Tham số:
            key (K): Khóa cần kiểm tra.
            
        Trả về:
            bool: True nếu key tồn tại, False nếu không.
        """
        bucket = self._get_bucket(key)
        for entry_node in bucket:
            if entry_node.key == key:
                return True
        return False

    def keys(self) -> LinkedList[K]:
        """
        Lấy tất cả các key trong hash table.
        
        Trả về:
            LinkedList[K]: LinkedList chứa tất cả các key.
        """
        all_keys = LinkedList[K]()
        for bucket in self.buckets:  # Array là iterable
            if bucket:  # bucket có thể là None
                for entry_node in bucket:
                    all_keys.append(entry_node.key)
        return all_keys

    def values(self) -> LinkedList[V]:
        """
        Lấy tất cả các giá trị trong hash table.
        
        Trả về:
            LinkedList[V]: LinkedList chứa tất cả các giá trị.
        """
        all_values = LinkedList[V]()
        for bucket in self.buckets:  # Array là iterable
            if bucket:
                for entry_node in bucket:
                    all_values.append(entry_node.value)
        return all_values

    def items(self) -> LinkedList[Tuple[K, V]]:
        """
        Lấy tất cả các cặp key-value trong hash table.
        
        Trả về:
            LinkedList[Tuple[K, V]]: LinkedList chứa tất cả các cặp key-value.
        """
        all_items = LinkedList[Tuple[K, V]]()
        for bucket in self.buckets:  # Array là iterable
            if bucket:  # bucket có thể là None
                for entry_node in bucket:
                    all_items.append((entry_node.key, entry_node.value))
        return all_items

    def _resize_if_needed(self) -> None:
        """
        Kiểm tra và thực hiện resize nếu load factor vượt ngưỡng.
        
        Load factor = số phần tử / dung lượng.
        Khi load factor > threshold, nhân đôi dung lượng để duy trì hiệu suất.
        """
        current_load_factor = self.num_elements / self.capacity
        if current_load_factor > self.load_factor_threshold:
            self._resize(self.capacity * 2)

    def _resize(self, new_capacity: int) -> None:
        """
        Thay đổi kích thước hash table và rehash tất cả entries.
        
        Tạo hash table mới với capacity mới, sau đó di chuyển tất cả
        entries từ hash table cũ sang mới (rehashing).
        
        Tham số:
            new_capacity (int): Dung lượng mới của hash table.
        """
        # Lưu trữ hash table cũ
        old_buckets_array = self.buckets
        old_capacity = self.capacity
        
        # Tạo hash table mới
        self.capacity = new_capacity
        self.buckets = Array(self.capacity)
        for i in range(self.capacity):
            self.buckets.set(i, LinkedList[HashEntry[K,V]]())
        self.num_elements = 0  # Sẽ được cập nhật lại khi rehash
        
        # Rehash tất cả entries từ hash table cũ
        for i in range(old_capacity):
            bucket = old_buckets_array.get(i)
            if bucket:
                for entry_node in bucket:
                    self.put(entry_node.key, entry_node.value)

    def get_num_elements(self) -> int:
        """
        Lấy số lượng phần tử hiện có trong hash table.
        
        Trả về:
            int: Số lượng cặp key-value trong hash table.
        """
        return self.num_elements
    
    def is_empty(self) -> bool:
        """
        Kiểm tra hash table có rỗng không.
        
        Trả về:
            bool: True nếu hash table rỗng, False nếu không.
        """
        return self.num_elements == 0

    def clear(self) -> None:
        """
        Xóa tất cả các phần tử khỏi hash table.
        
        Đặt lại hash table về trạng thái rỗng ban đầu nhưng giữ nguyên
        dung lượng và load factor threshold.
        """
        self.buckets = Array(self.capacity)
        for i in range(self.capacity):
            self.buckets.set(i, LinkedList[HashEntry[K,V]]())
        self.num_elements = 0

    def copy(self) -> 'HashTable[K, V]':
        """
        Tạo một bản sao nông (shallow copy) của hash table.
        
        Trả về:
            HashTable[K, V]: Hash table mới với các entries tương tự.
        """
        new_table = HashTable[K, V](capacity=self.capacity, 
                                   load_factor_threshold=self.load_factor_threshold)
        for bucket in self.buckets:
            if bucket:
                for entry_node in bucket:
                    new_table.put(entry_node.key, entry_node.value)
        return new_table

    def __setitem__(self, key: K, value: V) -> None:
        """Hỗ trợ syntax: hash_table[key] = value"""
        self.put(key, value)

    def __getitem__(self, key: K) -> V:
        """
        Hỗ trợ syntax: value = hash_table[key]
        
        Tham số:
            key (K): Khóa cần lấy giá trị.
            
        Trả về:
            V: Giá trị tương ứng với key.
            
        Ngoại lệ:
            KeyError: Nếu key không tồn tại.
        """
        value = self.get(key)
        if value is None:
            raise KeyError(f"Không tìm thấy khóa: {key}")
        return value

    def __delitem__(self, key: K) -> None:
        """
        Hỗ trợ syntax: del hash_table[key]
        
        Tham số:
            key (K): Khóa cần xóa.
            
        Ngoại lệ:
            KeyError: Nếu key không tồn tại.
        """
        removed_value = self.remove(key)
        if removed_value is None:
            raise KeyError(f"Không tìm thấy khóa: {key}")
            
    def __contains__(self, key: K) -> bool:
        """Hỗ trợ syntax: key in hash_table"""
        return self.contains_key(key)

    def __len__(self) -> int:
        """Hỗ trợ syntax: len(hash_table)"""
        return self.num_elements

    def __iter__(self) -> Iterator[K]:
        """
        Hỗ trợ iteration over keys: for key in hash_table
        
        Trả về:
            Iterator[K]: Iterator để duyệt qua tất cả các key.
        """
        for bucket in self.buckets:
            if bucket:
                for entry_node in bucket:
                    yield entry_node.key