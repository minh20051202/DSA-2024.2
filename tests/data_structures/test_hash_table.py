import unittest
from src.data_structures.hash_table import HashTable, HashEntry
from src.data_structures.linked_list import LinkedList

class TestHashTable(unittest.TestCase):
    def test_initialization(self):
        ht = HashTable[str, int]()
        self.assertEqual(ht.capacity, HashTable.DEFAULT_CAPACITY)
        self.assertEqual(len(ht), 0)
        self.assertTrue(ht.is_empty())

        ht_custom = HashTable[str, int](capacity=32, load_factor_threshold=0.5)
        self.assertEqual(ht_custom.capacity, 32)
        self.assertEqual(ht_custom.load_factor_threshold, 0.5)
        self.assertEqual(len(ht_custom.buckets), 32) # Kiểm tra độ dài của mảng
        for i in range(ht_custom.capacity):
            bucket = ht_custom.buckets.get(i)
            self.assertIsNotNone(bucket, f"Bucket {i} phải được khởi tạo")
            self.assertIsInstance(bucket, LinkedList)
            self.assertTrue(bucket.is_empty())

        with self.assertRaises(ValueError):
            HashTable(capacity=0)
        with self.assertRaises(ValueError):
            HashTable(load_factor_threshold=0)
        with self.assertRaises(ValueError):
            HashTable(load_factor_threshold=1.1)

    def test_put_and_get(self):
        ht = HashTable[str, int]()
        ht.put("apple", 1)
        ht.put("banana", 2)
        ht.put("cherry", 3)

        self.assertEqual(len(ht), 3)
        self.assertEqual(ht.get("apple"), 1)
        self.assertEqual(ht.get("banana"), 2)
        self.assertEqual(ht.get("cherry"), 3)
        self.assertIsNone(ht.get("durian"))
        self.assertEqual(ht.get("durian", 0), 0)

        # Kiểm tra cập nhật
        ht.put("apple", 10)
        self.assertEqual(ht.get("apple"), 10)
        self.assertEqual(len(ht), 3) # Kích thước không thay đổi khi cập nhật

    def test_contains_key(self):
        ht = HashTable[str, bool]()
        ht.put("exists", True)
        self.assertTrue(ht.contains_key("exists"))
        self.assertFalse(ht.contains_key("not_exists"))

    def test_remove(self):
        ht = HashTable[int, str]()
        ht.put(1, "one")
        ht.put(2, "two")
        ht.put(10, "ten")

        self.assertEqual(ht.remove(2), "two")
        self.assertEqual(len(ht), 2)
        self.assertIsNone(ht.get(2))
        self.assertFalse(ht.contains_key(2))

        self.assertIsNone(ht.remove(100)) # Xóa khóa không tồn tại
        self.assertEqual(len(ht), 2)

        self.assertEqual(ht.remove(1), "one")
        self.assertEqual(ht.remove(10), "ten")
        self.assertTrue(ht.is_empty())

    def test_keys_and_values(self):
        ht = HashTable[str, int]()
        ht.put("a", 1)
        ht.put("b", 2)
        ht.put("c", 3)

        keys_ll = ht.keys()
        key_list = []
        for k_node in keys_ll: key_list.append(k_node)
        self.assertEqual(len(key_list), 3)
        self.assertIn("a", key_list)
        self.assertIn("b", key_list)
        self.assertIn("c", key_list)

        values_ll = ht.values()
        value_list = []
        for v_node in values_ll: value_list.append(v_node)
        self.assertEqual(len(value_list), 3)
        self.assertIn(1, value_list)
        self.assertIn(2, value_list)
        self.assertIn(3, value_list)

    def test_resize(self):
        # Sử dụng dung lượng nhỏ và hệ số tải để dễ dàng kích hoạt thay đổi kích thước
        ht = HashTable[int, int](capacity=2, load_factor_threshold=0.5)
        self.assertEqual(ht.capacity, 2)

        ht.put(1, 10) # Tải = 1/2 = 0.5. Chưa thay đổi kích thước.
        self.assertEqual(ht.capacity, 2)

        ht.put(2, 20) # Tải = 2/2 = 1.0. Nên thay đổi kích thước.
        self.assertTrue(ht.capacity > 2, "Dung lượng nên tăng sau khi thay đổi kích thước")
        self.assertEqual(ht.capacity, 4) # Thay đổi kích thước mặc định nhân đôi dung lượng
        self.assertEqual(len(ht), 2)
        self.assertEqual(ht.get(1), 10)
        self.assertEqual(ht.get(2), 20)

        ht.put(3, 30) # Tải = 3/4 = 0.75. Không thay đổi kích thước dựa trên ngưỡng 0.5 nếu ngưỡng > 0.5.
                     # Ồ, ngưỡng là 0.5. Vậy 3/4 > 0.5 nghĩa là phải thay đổi kích thước.
        self.assertEqual(ht.capacity, 8) # 4*2 = 8
        self.assertEqual(len(ht), 3)
        self.assertEqual(ht.get(1), 10)
        self.assertEqual(ht.get(2), 20)
        self.assertEqual(ht.get(3), 30)

    def test_dunder_methods(self):
        ht = HashTable[str, str]()
        ht["key1"] = "value1"
        ht["key2"] = "value2"

        self.assertEqual(ht["key1"], "value1")
        self.assertTrue("key2" in ht)
        self.assertFalse("key3" in ht)
        self.assertEqual(len(ht), 2)

        del ht["key1"]
        self.assertFalse("key1" in ht)
        self.assertEqual(len(ht), 1)

        with self.assertRaises(KeyError):
            _ = ht["non_existent_key"]
        with self.assertRaises(KeyError):
            del ht["non_existent_key"]

    def test_clear(self):
        ht = HashTable[str, int](capacity=5)
        ht.put("x", 100)
        ht.put("y", 200)
        self.assertEqual(len(ht), 2)
        
        ht.clear()
        self.assertEqual(len(ht), 0)
        self.assertTrue(ht.is_empty())
        self.assertEqual(ht.capacity, 5) # Dung lượng nên được giữ nguyên
        self.assertIsNone(ht.get("x"))
        # Kiểm tra xem các bucket có phải là các LinkedList rỗng mới không
        for i in range(ht.capacity):
            bucket = ht.buckets.get(i)
            self.assertIsNotNone(bucket)
            self.assertIsInstance(bucket, LinkedList)
            self.assertTrue(bucket.is_empty())

    def test_copy(self):
        ht1 = HashTable[str, int]()
        ht1.put("a", 10)
        ht1.put("b", 20)

        ht2 = ht1.copy()
        self.assertEqual(len(ht1), len(ht2))
        self.assertEqual(ht1.capacity, ht2.capacity)
        self.assertEqual(ht1.load_factor_threshold, ht2.load_factor_threshold)
        self.assertNotEqual(id(ht1.buckets), id(ht2.buckets)) # Mảng buckets phải là mảng mới

        self.assertEqual(ht2.get("a"), 10)
        self.assertEqual(ht2.get("b"), 20)

        # Sửa đổi bản sao, bản gốc không nên thay đổi
        ht2.put("c", 30)
        self.assertEqual(len(ht2), 3)
        self.assertEqual(len(ht1), 2)
        self.assertIsNone(ht1.get("c"))

        ht2.put("a", 100)
        self.assertEqual(ht2.get("a"), 100)
        self.assertEqual(ht1.get("a"), 10)

        # Đảm bảo các bucket là các LinkedList mới (sao chép nông của các entry là được)
        # Điều này khó kiểm tra trực tiếp mà không biết giá trị hash, nhưng các thao tác put
        # trên ht2 không nên ảnh hưởng đến các đối tượng LinkedList nội bộ của ht1.
        # Kiểm tra trên (sửa đổi ht2.get("a")) ngầm bao gồm một phần của điều này nếu các entry được ghi đè.

if __name__ == '__main__':
    unittest.main() 