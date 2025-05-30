#!/usr/bin/env python3

"""
Triển khai Array (Mảng) tùy chỉnh cho Dự án Đơn giản hóa Nợ.
"""

from typing import TypeVar, Generic, Iterator

T = TypeVar('T')

class Array(Generic[T]):
    """Triển khai một mảng cơ bản với khả năng thay đổi kích thước động."""
    def __init__(self, capacity: int = 10):
        """
        Khởi tạo một mảng mới với dung lượng cho trước.

        Tham số:
            capacity (int): Dung lượng ban đầu của mảng.
        """
        if capacity <= 0:
            raise ValueError("Dung lượng mảng phải là số dương")
        self.capacity: int = capacity
        self.size: int = 0
        # Sử dụng list của Python để lưu trữ dữ liệu nội bộ.
        # Điều này là một chi tiết triển khai; người dùng Array sẽ không tương tác trực tiếp với nó.
        # Mục tiêu là thay thế việc sử dụng list của Python ở các lớp cấp cao hơn bằng Array này.
        self._internal_data: list[T | None] = [None] * capacity

    def __len__(self) -> int:
        """
        Lấy độ dài của mảng (số lượng phần tử hiện có).

        Trả về:
            int: Số lượng phần tử trong mảng.
        """
        return self.size

    def get(self, index: int) -> T:
        """
        Lấy phần tử tại chỉ mục.

        Tham số:
            index (int): Chỉ mục của phần tử cần lấy.

        Trả về:
            T: Phần tử tại chỉ mục đã cho.

        Ngoại lệ:
            IndexError: Nếu chỉ mục nằm ngoài phạm vi.
        """
        if 0 <= index < self.size:
            element = self._internal_data[index]
            return element
        raise IndexError("Chỉ mục mảng nằm ngoài phạm vi")

    def set(self, index: int, value: T) -> None:
        """
        Đặt giá trị cho phần tử tại chỉ mục.
        Nếu index bằng self.size và còn dung lượng, nó sẽ hoạt động giống như append.

        Tham số:
            index (int): Chỉ mục để đặt giá trị.
            value (T): Giá trị cần đặt tại chỉ mục.

        Ngoại lệ:
            IndexError: Nếu chỉ mục nằm ngoài phạm vi hợp lệ để đặt.
        """
        if 0 <= index < self.size:
            self._internal_data[index] = value
        elif index == self.size and self.size < self.capacity:
            self._internal_data[index] = value
            self.size += 1
        elif index == self.size and self.size >= self.capacity: # Cần resize trước
            self._resize()
            self._internal_data[index] = value
            self.size += 1
        else:
            raise IndexError("Chỉ mục mảng nằm ngoài phạm vi để đặt giá trị")

    def append(self, value: T) -> None:
        """
        Thêm giá trị vào cuối mảng.

        Tham số:
            value (T): Giá trị cần thêm.
        """
        if self.size >= self.capacity:
            self._resize()
        self._internal_data[self.size] = value
        self.size += 1

    def _resize(self) -> None:
        """Gấp đôi dung lượng của mảng. Nếu dung lượng là 0, đặt thành 1."""
        old_internal_data = self._internal_data
        new_capacity = self.capacity * 2 if self.capacity > 0 else 1
        self.capacity = new_capacity
        self._internal_data = [None] * self.capacity
        for i in range(self.size):
            self._internal_data[i] = old_internal_data[i]

    def copy(self) -> 'Array[T]':
        """
        Tạo một bản sao nông (shallow copy) của mảng.

        Trả về:
            Array[T]: Một mảng mới với các phần tử tương tự.
        """
        new_array = Array[T](self.capacity)
        new_array.size = self.size
        for i in range(self.size):
            new_array._internal_data[i] = self._internal_data[i]
        return new_array

    def __str__(self) -> str:
        """Trả về biểu diễn chuỗi của mảng, ví dụ: '[1, 2, 3]'."""
        if self.size == 0:
            return "[]"
        items_str = []
        for i in range(self.size):
            items_str.append(str(self._internal_data[i]))
        return "[" + ", ".join(items_str) + "]"

    def __repr__(self) -> str:
        """Trả về biểu diễn chuỗi chính thức của mảng, ví dụ: 'Array([1, 2, 3], capacity=10)'."""
        # Lấy các phần tử thực tế để hiển thị
        items_repr_list = []
        for i in range(self.size):
            items_repr_list.append(repr(self._internal_data[i]))
        items_part = "[" + ", ".join(items_repr_list) + "]"
        return f"Array({items_part}, size={self.size}, capacity={self.capacity})"

    def __iter__(self) -> Iterator[T]:
        """Trả về một iterator cho các phần tử trong mảng."""
        for i in range(self.size):
            # Giả định get(i) sẽ trả về T. Nếu get(i) có thể trả về None không phải T,
            # thì cần xử lý type ở đây hoặc đảm bảo get(i) luôn đúng.
            yield self.get(i)

    def insert(self, index: int, value: T) -> None:
        """
        Chèn giá trị vào vị trí chỉ mục đã cho, dịch chuyển các phần tử kế tiếp sang phải.

        Tham số:
            index (int): Chỉ mục để chèn giá trị.
            value (T): Giá trị cần chèn.

        Ngoại lệ:
            IndexError: Nếu chỉ mục nằm ngoài phạm vi [0, self.size].
        """
        if not (0 <= index <= self.size):
            raise IndexError("Chỉ mục chèn mảng nằm ngoài phạm vi")

        if self.size >= self.capacity:
            self._resize()

        # Dịch chuyển các phần tử từ index đến self.size - 1 sang phải một vị trí
        # Bắt đầu từ cuối để tránh ghi đè
        for i in range(self.size, index, -1):
            self._internal_data[i] = self._internal_data[i-1]
        
        self._internal_data[index] = value
        self.size += 1

    def pop(self, index: int = -1) -> T:
        """
        Xóa và trả về phần tử tại chỉ mục đã cho (mặc định là phần tử cuối cùng).

        Tham số:
            index (int): Chỉ mục của phần tử cần xóa. Mặc định là -1 (phần tử cuối).

        Trả về:
            T: Phần tử đã được xóa.

        Ngoại lệ:
            IndexError: Nếu mảng rỗng hoặc chỉ mục nằm ngoài phạm vi.
        """
        if self.size == 0:
            raise IndexError("Không thể pop từ một mảng rỗng")

        actual_index = index
        if index == -1:
            actual_index = self.size - 1
        
        if not (0 <= actual_index < self.size):
            raise IndexError("Chỉ mục pop mảng nằm ngoài phạm vi")

        value_to_pop = self.get(actual_index)

        # Dịch chuyển các phần tử từ actual_index + 1 đến self.size - 1 sang trái một vị trí
        for i in range(actual_index, self.size - 1):
            self._internal_data[i] = self._internal_data[i+1]
        
        self._internal_data[self.size - 1] = None # Xóa tham chiếu ở vị trí cuối cũ
        self.size -= 1
        return value_to_pop 