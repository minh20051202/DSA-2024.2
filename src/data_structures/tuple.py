from __future__ import annotations
from typing import Generic, TypeVar, Iterable, Iterator, Any

from .array import Array

T = TypeVar('T')

class Tuple(Generic[T]):
    """
    TUPLE - BỘ GIÁ TRỊ
    
    Cấu trúc dữ liệu tuple bất biến (immutable) tùy chỉnh, có thể hash được.
    Tuple lưu trữ một tập hợp các phần tử theo thứ tự và không thể thay đổi sau khi tạo.
    Hỗ trợ indexing, iteration và có thể được sử dụng làm key trong dictionary.
    
    PHƯƠNG THỨC:
    - __init__(items): Khởi tạo tuple từ một iterable - O(n)
    - __getitem__(index): Truy cập phần tử theo chỉ số - O(1)
    - __len__(): Trả về số lượng phần tử - O(1)
    - __iter__(): Trả về iterator để duyệt qua các phần tử - O(1)
    - __hash__(): Tính và trả về hash value - O(n) lần đầu, O(1) các lần sau
    - __eq__(other): So sánh bằng với tuple khác - O(n)
    """
    
    def __init__(self, items: Iterable[Any]):
        """
        Khởi tạo một tuple mới từ một iterable.

        Tham số:
            items (Iterable[Any]): Một iterable chứa các phần tử để tạo tuple.
        """
        temp_array = Array[Any]()
        for item in items:
            temp_array.append(item)
        
        self._items: Array[Any] = Array(temp_array.size)
        for i in range(temp_array.size):
            self._items.set(i, temp_array.get(i))
        
        self._hash: int | None = None

    def __len__(self) -> int:
        """
        Lấy số lượng phần tử trong tuple.

        Trả về:
            int: Số lượng phần tử trong tuple.
        """
        return len(self._items)

    def __getitem__(self, index: int) -> Any:
        """
        Truy cập phần tử tại chỉ số được chỉ định.

        Tham số:
            index (int): Chỉ số của phần tử cần truy cập.

        Trả về:
            Any: Phần tử tại chỉ số đã cho.

        Ngoại lệ:
            IndexError: Nếu chỉ số nằm ngoài phạm vi tuple.
        """
        if not 0 <= index < len(self._items):
            raise IndexError("Tuple index out of range")
        return self._items.get(index)

    def __iter__(self) -> Iterator[Any]:
        """
        Trả về iterator để duyệt qua các phần tử trong tuple.

        Trả về:
            Iterator[Any]: Iterator cho các phần tử trong tuple.
        """
        return iter(self._items)

    def __eq__(self, other: object) -> bool:
        """
        So sánh bằng với một đối tượng khác.

        Tham số:
            other (object): Đối tượng khác để so sánh.

        Trả về:
            bool: True nếu hai tuple bằng nhau, False nếu khác nhau.
            NotImplemented: Nếu đối tượng khác không phải là Tuple.
        """
        if not isinstance(other, Tuple):
            return NotImplemented
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __hash__(self) -> int:
        """
        Tính và trả về hash value của tuple.
        Hash value được cache để tối ưu hiệu suất khi gọi nhiều lần.

        Trả về:
            int: Hash value của tuple.
        """
        if self._hash is None:
            elements = []
            for i in range(len(self._items)):
                elements.append(self._items.get(i))
            self._hash = hash(tuple(elements))
        return self._hash
