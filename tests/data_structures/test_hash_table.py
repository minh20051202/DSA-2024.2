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
        self.assertEqual(len(ht_custom.buckets), 32) # Check Array length
        for i in range(ht_custom.capacity):
            bucket = ht_custom.buckets.get(i)
            self.assertIsNotNone(bucket, f"Bucket {i} should be initialized")
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

        # Test update
        ht.put("apple", 10)
        self.assertEqual(ht.get("apple"), 10)
        self.assertEqual(len(ht), 3) # Size should not change on update

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

        self.assertIsNone(ht.remove(100)) # Remove non-existent key
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
        # Use a small capacity and load factor to trigger resize easily
        ht = HashTable[int, int](capacity=2, load_factor_threshold=0.5)
        self.assertEqual(ht.capacity, 2)

        ht.put(1, 10) # Load = 1/2 = 0.5. No resize yet.
        self.assertEqual(ht.capacity, 2)

        ht.put(2, 20) # Load = 2/2 = 1.0. Resize should occur.
        self.assertTrue(ht.capacity > 2, "Capacity should increase after resize")
        self.assertEqual(ht.capacity, 4) # Default resize doubles capacity
        self.assertEqual(len(ht), 2)
        self.assertEqual(ht.get(1), 10)
        self.assertEqual(ht.get(2), 20)

        ht.put(3, 30) # Load = 3/4 = 0.75. No resize based on 0.5 threshold if threshold is >. 
                      # Oh, threshold is 0.5. So 3/4 > 0.5 means resize.
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
        self.assertEqual(ht.capacity, 5) # Capacity should be retained
        self.assertIsNone(ht.get("x"))
        # Check if buckets are new empty LinkedLists
        for i in range(ht.capacity):
            bucket = ht.buckets.get(i)
            self.assertIsNotNone(bucket)
            self.assertIsInstance(bucket, LinkedList)
            self.assertTrue(bucket.is_empty())

    def test_str_and_repr(self):
        ht = HashTable[str, int](capacity=2)
        ht.put("one", 1)
        # String representation is order-dependent due to hashing
        # For simplicity, check if components are present
        s = str(ht)
        self.assertTrue(s.startswith("{"))
        self.assertTrue(s.endswith("}"))
        self.assertIn("'one': 1", s)

        r = repr(ht)
        self.assertEqual(r, "HashTable(dung_luong=2, so_phan_tu=1)")

        ht.put("two", 2) # Trigger resize if capacity was very small and load factor high
                          # Default capacity for this test is 2, load factor 0.75
                          # Add "one" -> 1/2 = 0.5 load. No resize
                          # Add "two" -> 2/2 = 1.0 load. Resize to 4.
        s_two = str(ht)
        self.assertIn("'one': 1", s_two)
        self.assertIn("'two': 2", s_two)
        self.assertTrue(", " in s_two or len(ht) <=1) # check for separator if more than one item
        
        r_two = repr(ht)
        self.assertEqual(r_two, "HashTable(dung_luong=4, so_phan_tu=2)")

    def test_copy(self):
        ht1 = HashTable[str, int]()
        ht1.put("a", 10)
        ht1.put("b", 20)

        ht2 = ht1.copy()
        self.assertEqual(len(ht1), len(ht2))
        self.assertEqual(ht1.capacity, ht2.capacity)
        self.assertEqual(ht1.load_factor_threshold, ht2.load_factor_threshold)
        self.assertNotEqual(id(ht1.buckets), id(ht2.buckets)) # Buckets array should be new

        self.assertEqual(ht2.get("a"), 10)
        self.assertEqual(ht2.get("b"), 20)

        # Modify copy, original should not change
        ht2.put("c", 30)
        self.assertEqual(len(ht2), 3)
        self.assertEqual(len(ht1), 2)
        self.assertIsNone(ht1.get("c"))

        ht2.put("a", 100)
        self.assertEqual(ht2.get("a"), 100)
        self.assertEqual(ht1.get("a"), 10)

        # Ensure buckets themselves are new LinkedLists (shallow copy of entries is fine)
        # This is harder to test directly without knowing hash values, but put operations
        # on ht2 should not affect ht1's internal LinkedList objects.
        # The test above (modifying ht2.get("a")) implicitly covers some of this if entries are overwritten.

if __name__ == '__main__':
    unittest.main() 