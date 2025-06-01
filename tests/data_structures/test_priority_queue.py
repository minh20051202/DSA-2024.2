import unittest
from src.data_structures.priority_queue import PriorityQueue, PriorityQueueItem

class TestPriorityQueue(unittest.TestCase):
    def test_empty_queue(self):
        pq = PriorityQueue[int]()
        self.assertTrue(pq.is_empty())
        self.assertEqual(len(pq), 0)
        with self.assertRaises(IndexError):
            pq.dequeue()
        with self.assertRaises(IndexError):
            pq.peek()

    def test_enqueue_and_peek_min_heap(self):
        """Kiểm tra enqueue và peek cho min-heap (mặc định)."""
        pq = PriorityQueue[str]() # Mặc định là min-heap dựa trên priority number
        pq.enqueue("task C", 30)
        pq.enqueue("task A", 10)
        pq.enqueue("task B", 20)

        self.assertEqual(len(pq), 3)
        self.assertFalse(pq.is_empty())
        self.assertEqual(pq.peek(), "task A") # Ưu tiên nhỏ nhất đứng đầu

    def test_dequeue_min_heap(self):
        """Kiểm tra dequeue cho min-heap (mặc định)."""
        pq = PriorityQueue[str]()
        pq.enqueue("item Z", 100)
        pq.enqueue("item X", 10)
        pq.enqueue("item Y", 50)

        self.assertEqual(pq.dequeue(), "item X") # 10
        self.assertEqual(pq.dequeue(), "item Y") # 50
        self.assertEqual(pq.dequeue(), "item Z") # 100
        self.assertTrue(pq.is_empty())

    def test_custom_comparator_max_heap(self):
        """Kiểm tra với comparator tùy chỉnh cho max-heap."""
        # Max-heap: comparator(a,b) là a > b
        def max_heap_comparator(item_a, item_b): # item_a và item_b là các item thực tế (vd: int)
            # PriorityQueueItem.priority không được dùng trực tiếp ở đây
            # mà comparator được gọi với item_a.item và item_b.item
            # Trong trường hợp này, item chính là priority (số nguyên)
            return item_a > item_b 

        pq = PriorityQueue[int](comparator=max_heap_comparator)
        # Khi dùng comparator, giá trị priority trong enqueue() không thực sự dùng để so sánh nội bộ
        # mà chỉ để gói item. Comparator sẽ được gọi với chính các item.
        # Để đơn giản, ta có thể dùng item làm priority luôn.
        pq.enqueue(item=30, priority=30)
        pq.enqueue(item=10, priority=10)
        pq.enqueue(item=20, priority=20)
        pq.enqueue(item=50, priority=50)
        pq.enqueue(item=5, priority=5)

        self.assertEqual(pq.peek(), 50) # Max-heap, item lớn nhất đứng đầu
        self.assertEqual(pq.dequeue(), 50)
        self.assertEqual(pq.dequeue(), 30)
        self.assertEqual(pq.dequeue(), 20)
        self.assertEqual(pq.dequeue(), 10)
        self.assertEqual(pq.dequeue(), 5)
        self.assertTrue(pq.is_empty())

    def test_duplicate_priorities(self):
        """Kiểm tra khi có các độ ưu tiên trùng nhau."""
        pq = PriorityQueue[str]()
        pq.enqueue("A1", 10)
        pq.enqueue("B1", 20)
        pq.enqueue("A2", 10) # Độ ưu tiên giống A1
        pq.enqueue("C1", 5)

        # Thứ tự dequeue giữa các item có cùng priority không được đảm bảo chặt chẽ
        # nhưng item có priority nhỏ nhất phải ra trước.
        self.assertEqual(pq.dequeue(), "C1") # 5
        
        # A1 hoặc A2 có thể ra tiếp theo
        first_10 = pq.dequeue()
        self.assertTrue(first_10 == "A1" or first_10 == "A2")
        second_10 = pq.dequeue()
        self.assertTrue(second_10 == "A1" or second_10 == "A2")
        self.assertNotEqual(first_10, second_10)

        self.assertEqual(pq.dequeue(), "B1") # 20
        self.assertTrue(pq.is_empty())

    def test_priority_queue_item_lt(self):
        item1 = PriorityQueueItem("task1", 10)
        item2 = PriorityQueueItem("task2", 20)
        self.assertTrue(item1 < item2)
        self.assertFalse(item2 < item1)
        with self.assertRaises(TypeError):
            PriorityQueueItem("task_str_priority", "low") < item1

if __name__ == '__main__':
    unittest.main()        