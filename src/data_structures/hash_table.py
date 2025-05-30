from typing import TypeVar, Generic
from .linked_list import LinkedList
from .array import Array # Import Array tùy chỉnh

K = TypeVar('K')
V = TypeVar('V')

class HashEntry(Generic[K, V]):
    """Lớp để lưu cặp key-value trong HashTable, hỗ trợ chaining."""
    def __init__(self, key: K, value: V):
        self.key: K = key
        self.value: V = value

    def __str__(self):
        return f"({self.key}: {self.value})"

class HashTable(Generic[K, V]):
    DEFAULT_CAPACITY = 16
    DEFAULT_LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = DEFAULT_CAPACITY, 
                 load_factor_threshold: float = DEFAULT_LOAD_FACTOR_THRESHOLD):
        if capacity <= 0:
            raise ValueError("Dung lượng (capacity) phải là số dương")
        if not (0 < load_factor_threshold <= 1.0):
            raise ValueError("Ngưỡng hệ số tải (load factor threshold) phải trong khoảng (0, 1]")
            
        self.capacity: int = capacity
        self.buckets: Array[LinkedList[HashEntry[K,V]] | None] = Array(self.capacity)
        for i in range(self.capacity):
            # Array.set sẽ tăng self.buckets.size nếu i == self.buckets.size
            # Điều này không mong muốn ở đây, ta muốn khởi tạo các bucket cho dung lượng đã có.
            # Phải đảm bảo Array.set không tăng size khi index < self.buckets.size
            # Hoặc Array được khởi tạo với size = capacity và các phần tử None, sau đó ta set.
            # Array hiện tại khởi tạo _internal_data với capacity, nhưng size là 0.
            # Ta cần set và tự tăng size của Array nếu cần, hoặc Array hỗ trợ khởi tạo với size.
            # Cách tiếp cận an toàn: đảm bảo Array có size bằng capacity sau vòng lặp này.
            empty_ll = LinkedList[HashEntry[K,V]]()
            if i < self.buckets.size: # Nếu Array.set không tăng size khi index < size
                 self.buckets.set(i, empty_ll)
            else: # Nếu i >= self.buckets.size, set sẽ hoạt động như append và tăng size
                 self.buckets.set(i, empty_ll) # Điều này sẽ tăng self.buckets.size lên i+1
        # Sau vòng lặp, self.buckets.size phải bằng self.capacity
        # Nếu Array.set(index, value) tự tăng size khi index == size, thì vòng lặp trên là đúng.
        # Nếu Array.set chỉ cập nhật, cần append N lần hoặc sửa Array.
        # Giả định Array.set(index,value) khi index == Array.size sẽ tăng Array.size.
        # Array.set(i, value) của chúng ta làm điều này (tăng size nếu index == self.size)
        # và Array() khởi tạo với size=0. Đoạn code trên sẽ làm Array có size = capacity.
            
        self.num_elements: int = 0
        self.load_factor_threshold: float = load_factor_threshold

    def _hash(self, key: K) -> int:
        """Hàm băm đơn giản. Cần cải thiện cho các kiểu dữ liệu phức tạp hơn.
        Đối với các đối tượng tùy chỉnh, chúng cần triển khai __hash__()."""
        return hash(key) % self.capacity

    def _get_bucket(self, key: K) -> LinkedList[HashEntry[K,V]]:
        """Lấy bucket (LinkedList) tương ứng với key."""
        index = self._hash(key)
        bucket = self.buckets.get(index) # Sử dụng Array.get()
        # Kiểm tra này vẫn quan trọng, mặc dù Array.get() sẽ raise IndexError nếu index ngoài phạm vi
        # nhưng bucket có thể là None nếu Array được phép chứa None hợp lệ (mà nó được phép)
        if bucket is None:
            # Trường hợp này lý thuyết không nên xảy ra nếu khởi tạo đúng
            # và self.capacity không đổi giữa chừng mà self.buckets không được cập nhật
            new_ll = LinkedList[HashEntry[K,V]]()
            self.buckets.set(index, new_ll) # Sử dụng Array.set()
            return new_ll
        assert isinstance(bucket, LinkedList), "Bucket không phải là LinkedList"
        return bucket

    def put(self, key: K, value: V) -> None:
        "Thêm hoặc cập nhật cặp key-value." 
        bucket = self._get_bucket(key)
        
        # Kiểm tra xem key đã tồn tại trong bucket chưa
        for entry_node in bucket: # LinkedList hỗ trợ __iter__
            if entry_node.key == key:
                entry_node.value = value # Cập nhật value
                return
        
        # Nếu key chưa tồn tại, thêm entry mới vào bucket
        bucket.append(HashEntry(key, value))
        self.num_elements += 1
        self._resize_if_needed()

    def get(self, key: K, default: V | None = None) -> V | None:
        "Lấy giá trị của key. Trả về `default` (mặc định là None) nếu không tìm thấy." 
        bucket = self._get_bucket(key)
        for entry_node in bucket:
            if entry_node.key == key:
                return entry_node.value
        return default

    def remove(self, key: K) -> V | None:
        "Xóa key và giá trị tương ứng. Trả về giá trị bị xóa hoặc None nếu không tìm thấy." 
        bucket = self._get_bucket(key)
        entry_to_remove = None
        for entry_node in bucket:
            if entry_node.key == key:
                entry_to_remove = entry_node
                break
        
        if entry_to_remove:
            bucket.remove_by_value(entry_to_remove) # LinkedList cần có phương thức remove_by_value
            self.num_elements -= 1
            return entry_to_remove.value
        return None

    def contains_key(self, key: K) -> bool:
        "Kiểm tra key có trong bảng không." 
        bucket = self._get_bucket(key)
        for entry_node in bucket:
            if entry_node.key == key:
                return True
        return False

    def keys(self) -> LinkedList[K]:
        "Trả về một LinkedList chứa tất cả các key trong HashTable." 
        all_keys = LinkedList[K]()
        for bucket in self.buckets: # Array là iterable
            if bucket: # bucket là LinkedList[HashEntry[K,V]] | None
                for entry_node in bucket:
                    all_keys.append(entry_node.key)
        return all_keys

    def values(self) -> LinkedList[V]:
        "Trả về một LinkedList chứa tất cả các giá trị trong HashTable." 
        all_values = LinkedList[V]()
        for bucket in self.buckets: # Array là iterable
            if bucket:
                for entry_node in bucket:
                    all_values.append(entry_node.value)
        return all_values

    def _resize_if_needed(self) -> None:
        "Kiểm tra và thực hiện thay đổi kích thước (resize) nếu hệ số tải (load factor) vượt ngưỡng cho phép." 
        current_load_factor = self.num_elements / self.capacity
        if current_load_factor > self.load_factor_threshold:
            self._resize(self.capacity * 2) # Nhân đôi dung lượng (capacity)

    def _resize(self, new_capacity: int) -> None:
        "Thực hiện thay đổi kích thước (resize) của bảng băm." 
        old_buckets_array = self.buckets # Đây là Array
        old_capacity = self.capacity
        
        self.capacity = new_capacity
        # Khởi tạo self.buckets mới là một Array mới
        self.buckets = Array(self.capacity)
        for i in range(self.capacity):
            self.buckets.set(i, LinkedList[HashEntry[K,V]]()) # Đảm bảo Array có size = capacity
        self.num_elements = 0 # Sẽ được cập nhật lại khi thực hiện băm lại (rehash)
        
        # Duyệt qua old_buckets_array (là một Array)
        for i in range(old_capacity): # Duyệt qua dung lượng cũ của Array
            bucket = old_buckets_array.get(i) # Lấy bucket từ Array cũ
            if bucket:
                for entry_node in bucket:
                    self.put(entry_node.key, entry_node.value) # Băm lại (rehash) và thêm (put) lại phần tử

    def get_num_elements(self) -> int:
        "Trả về số lượng phần tử (key-value pairs) hiện có trong HashTable." 
        return self.num_elements
    
    def is_empty(self) -> bool:
        "Kiểm tra xem HashTable có rỗng không." 
        return self.num_elements == 0

    def clear(self) -> None:
        """Xóa tất cả các phần tử khỏi HashTable, đặt lại về trạng thái rỗng ban đầu nhưng giữ nguyên dung lượng."""
        # Giữ nguyên capacity và load_factor_threshold
        self.buckets = Array(self.capacity)
        for i in range(self.capacity):
            self.buckets.set(i, LinkedList[HashEntry[K,V]]()) # Đảm bảo Array có size = capacity
        self.num_elements = 0

    def __setitem__(self, key: K, value: V):
        self.put(key, value)

    def __getitem__(self, key: K) -> V:
        value = self.get(key)
        if value is None:
            raise KeyError(f"Không tìm thấy khóa: {key}")
        return value

    def __delitem__(self, key: K):
        removed_value = self.remove(key)
        if removed_value is None:
            raise KeyError(f"Không tìm thấy khóa: {key}")
            
    def __contains__(self, key: K) -> bool:
        return self.contains_key(key)

    def __len__(self) -> int:
        return self.num_elements

    def __str__(self) -> str:
        items_str = []
        for bucket in self.buckets: # Array là iterable
            if bucket and not bucket.is_empty():
                for entry in bucket:
                    items_str.append(f"{repr(entry.key)}: {repr(entry.value)}") 
        return "{" + ", ".join(items_str) + "}"

    def __repr__(self) -> str:
        return f"HashTable(dung_luong={self.capacity}, so_phan_tu={self.get_num_elements()})" 

    def copy(self) -> 'HashTable[K, V]':
        """Tạo một bản sao nông (shallow copy) của HashTable."""
        new_table = HashTable[K, V](capacity=self.capacity, 
                                     load_factor_threshold=self.load_factor_threshold)
        for bucket in self.buckets: # Array là iterable
            if bucket:
                for entry_node in bucket:
                    new_table.put(entry_node.key, entry_node.value)
        return new_table 