import unittest
from src.data_structures.array import Array

class TestArray(unittest.TestCase):
    def test_initialization(self):
        """Kiểm tra khởi tạo mảng với dung lượng và kích thước mặc định/cụ thể."""
        arr_default = Array()
        self.assertEqual(len(arr_default), 0, "Kích thước mảng mặc định phải là 0")
        self.assertEqual(arr_default.capacity, 10, "Dung lượng mảng mặc định phải là 10")

        arr_custom_cap = Array(20)
        self.assertEqual(len(arr_custom_cap), 0, "Kích thước mảng tùy chỉnh phải là 0")
        self.assertEqual(arr_custom_cap.capacity, 20, "Dung lượng mảng tùy chỉnh không khớp")
        
        with self.assertRaises(ValueError, msg="Phải báo lỗi nếu dung lượng không dương"):
            Array(0)
        with self.assertRaises(ValueError, msg="Phải báo lỗi nếu dung lượng âm"):
            Array(-5)

    def test_append_and_get(self):
        """Kiểm tra thêm phần tử và lấy phần tử."""
        arr = Array[int](5)
        arr.append(10)
        arr.append(20)
        arr.append(30)

        self.assertEqual(len(arr), 3, "Kích thước không đúng sau khi append")
        self.assertEqual(arr.get(0), 10, "Get phần tử đầu tiên thất bại")
        self.assertEqual(arr.get(1), 20, "Get phần tử thứ hai thất bại")
        self.assertEqual(arr.get(2), 30, "Get phần tử thứ ba thất bại")

        with self.assertRaises(IndexError, msg="Get ngoài phạm vi (dương) phải báo lỗi"):
            arr.get(3)
        with self.assertRaises(IndexError, msg="Get ngoài phạm vi (âm) phải báo lỗi"):
            arr.get(-1)

    def test_set_value(self):
        """Kiểm tra đặt giá trị tại một chỉ mục."""
        arr = Array[str](5)
        arr.append("a")
        arr.append("b")
        arr.append("c") # size = 3, capacity = 5

        arr.set(1, "B_updated")
        self.assertEqual(arr.get(1), "B_updated", "Set giá trị tại chỉ mục hiện có thất bại")
        self.assertEqual(len(arr), 3, "Kích thước không nên thay đổi khi set tại chỉ mục hiện có")

        # Kiểm tra set tại vị trí self.size nếu còn capacity
        arr.set(3, "d") # size hiện là 3, index 3 là vị trí mới
        self.assertEqual(len(arr), 4, "Kích thước phải tăng khi set tại self.size")
        self.assertEqual(arr.get(3), "d", "Get phần tử mới set tại self.size thất bại")

        with self.assertRaises(IndexError, msg="Set ngoài phạm vi (lớn) phải báo lỗi"):
            arr.set(5, "e") # size là 4, capacity là 5. Index 5 là ngoài phạm vi
        
        arr_full_then_set_at_end = Array[int](2)
        arr_full_then_set_at_end.append(1)
        arr_full_then_set_at_end.append(2) # Đầy capacity
        arr_full_then_set_at_end.set(2, 3) # Set tại self.size, nên resize và thêm vào
        self.assertEqual(len(arr_full_then_set_at_end), 3)
        self.assertEqual(arr_full_then_set_at_end.get(2), 3)
        self.assertTrue(arr_full_then_set_at_end.capacity >= 3)

    def test_resize(self):
        """Kiểm tra việc thay đổi kích thước tự động khi append."""
        arr = Array[int](2) # Dung lượng ban đầu nhỏ
        arr.append(1)
        arr.append(2)
        self.assertEqual(len(arr), 2)
        self.assertEqual(arr.capacity, 2)

        arr.append(3) # Lần append này sẽ kích hoạt resize
        self.assertEqual(len(arr), 3)
        self.assertTrue(arr.capacity >= 3, f"Dung lượng phải lớn hơn hoặc bằng 3 sau resize, hiện tại là {arr.capacity}")
        self.assertEqual(arr.get(0), 1)
        self.assertEqual(arr.get(1), 2)
        self.assertEqual(arr.get(2), 3)

        # Kiểm tra resize nhiều lần
        for i in range(4, 15):
            arr.append(i)
        self.assertEqual(len(arr), 14)
        self.assertTrue(arr.capacity >= 14)
        self.assertEqual(arr.get(13), 14)

    def test_iteration(self):
        """Kiểm tra việc duyệt mảng bằng vòng lặp for."""
        arr = Array[int](5)
        items_to_add = [10, 20, 30, 40]
        for item in items_to_add:
            arr.append(item)
        
        iterated_items = []
        for x in arr:
            iterated_items.append(x)
        self.assertEqual(iterated_items, items_to_add, "Duyệt mảng không trả về đúng các phần tử")

        empty_arr = Array[int]()
        iterated_empty = []
        for x in empty_arr:
            iterated_empty.append(x)
        self.assertEqual(iterated_empty, [], "Duyệt mảng rỗng phải không có phần tử nào")

    def test_copy(self):
        """Kiểm tra việc sao chép mảng."""
        arr1 = Array[int]()
        arr1.append(10)
        arr1.append(20)

        arr2 = arr1.copy()
        self.assertEqual(len(arr1), len(arr2), "Độ dài mảng sao chép phải giống nhau")
        self.assertEqual(arr1.capacity, arr2.capacity, "Dung lượng mảng sao chép phải giống nhau")
        self.assertNotEqual(id(arr1._internal_data), id(arr2._internal_data), 
                          "Dữ liệu nội bộ của mảng sao chép phải là đối tượng khác")

        for i in range(len(arr1)):
            self.assertEqual(arr1.get(i), arr2.get(i), f"Phần tử tại chỉ mục {i} không khớp sau khi sao chép")

        arr2.append(30)
        self.assertNotEqual(len(arr1), len(arr2), "Thay đổi trên bản sao không nên ảnh hưởng đến bản gốc")
        self.assertEqual(arr1.get(0), 10)
        arr2.set(0, 100)
        self.assertEqual(arr1.get(0), 10, "Thay đổi set trên bản sao không nên ảnh hưởng đến bản gốc")
        self.assertEqual(arr2.get(0), 100)

    def test_insert(self):
        """Kiểm tra chèn phần tử vào mảng."""
        arr = Array[int](3)
        arr.append(10) # [10]
        arr.append(30) # [10, 30]
        
        arr.insert(1, 20) # [10, 20, 30]
        self.assertEqual(len(arr), 3)

        arr.insert(0, 5) # [5, 10, 20, 30] -> resize
        self.assertEqual(len(arr), 4)
        self.assertTrue(arr.capacity >= 4)

        arr.insert(4, 40) # [5, 10, 20, 30, 40]
        self.assertEqual(len(arr), 5)

        with self.assertRaises(IndexError):
            arr.insert(10, 100) # Ngoài phạm vi
        with self.assertRaises(IndexError):
            arr.insert(-1, 100) # Ngoài phạm vi

    def test_pop(self):
        """Kiểm tra xóa và trả về phần tử từ mảng."""
        arr = Array[int](5)
        arr.append(10)
        arr.append(20)
        arr.append(30)
        arr.append(40)
        arr.append(50) # [10, 20, 30, 40, 50]

        self.assertEqual(arr.pop(), 50, "Pop phần tử cuối cùng thất bại") # [10, 20, 30, 40]
        self.assertEqual(len(arr), 4)

        self.assertEqual(arr.pop(1), 20, "Pop phần tử tại chỉ mục 1 thất bại") # [10, 30, 40]
        self.assertEqual(len(arr), 3)

        self.assertEqual(arr.pop(0), 10, "Pop phần tử đầu tiên thất bại") # [30, 40]
        self.assertEqual(len(arr), 2)

        self.assertEqual(arr.pop(), 40) # [30]
        self.assertEqual(arr.pop(), 30) # []
        self.assertEqual(len(arr), 0)

        with self.assertRaises(IndexError, msg="Pop từ mảng rỗng phải báo lỗi"):
            arr.pop()
        
        arr_single = Array[int]()
        arr_single.append(100)
        self.assertEqual(arr_single.pop(0), 100)
        with self.assertRaises(IndexError):
            arr_single.pop(0)

if __name__ == '__main__':
    unittest.main() 