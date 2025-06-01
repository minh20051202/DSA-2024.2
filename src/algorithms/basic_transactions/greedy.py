# Thuật toán Tham lam cho Đơn giản hóa Nợ
from __future__ import annotations

from src.core_type import BasicTransaction
from src.data_structures import LinkedList, HashTable, Tuple
from src.utils.sorting import merge_sort_linked_list
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

class GreedySimplifier:
    """
    Thực hiện đơn giản hóa nợ bằng cách tiếp cận tham lam tối ưu:
    - Tính số dư ròng cho mỗi người
    - Ghép người nợ lớn nhất với người cho vay lớn nhất  
    - Đảm bảo tổng số tiền và số lượng giao dịch tối thiểu
    
    Thuật toán hoạt động theo nguyên tắc tham lam:
    1. Tính toán số dư ròng của mỗi người (tổng nợ - tổng cho vay)
    2. Phân loại thành nhóm nợ (balance < 0) và nhóm cho vay (balance > 0)
    3. Ưu tiên ghép người nợ nhiều nhất với người cho vay nhiều nhất
    4. Tạo giao dịch thanh toán tối thiểu để cân bằng số dư
    
    Độ phức tạp thời gian: O(n log k) với n = số giao dịch, k = số người
    Độ phức tạp không gian: O(k)
    """
    
    def __init__(self, transactions: LinkedList[BasicTransaction]):
        """
        Khởi tạo bộ đơn giản hóa nợ với danh sách giao dịch ban đầu.
        
        Tham số:
            transactions: Danh sách liên kết các giao dịch cơ bản cần đơn giản hóa
        """
        self.initial_transactions = transactions  # Lưu trữ giao dịch gốc để tham chiếu
        self.people_balances = HashTable[str, float]()  # Bảng băm lưu số dư của từng người
        self._calculate_balances()  # Tính toán số dư ban đầu

    def _calculate_balances(self) -> None:
        """
        Tính toán số dư ròng cho mỗi người từ tất cả giao dịch.
        
        Quy tắc tính toán:
        - Người nợ (debtor): số dư giảm theo số tiền nợ (-amount)
        - Người cho vay (creditor): số dư tăng theo số tiền cho vay (+amount)
        
        Sử dụng duyệt tuần tự qua LinkedList với độ phức tạp O(n).
        """
        current = self.initial_transactions.head
        while current:
            tx = current.data
            # Cập nhật số dư cho người nợ (trừ đi số tiền nợ)
            current_debtor_balance = self.people_balances.get(tx.debtor, 0.0)
            self.people_balances.put(tx.debtor, round_money(current_debtor_balance - tx.amount))
            
            # Cập nhật số dư cho người cho vay (cộng thêm số tiền cho vay)
            current_creditor_balance = self.people_balances.get(tx.creditor, 0.0)
            self.people_balances.put(tx.creditor, round_money(current_creditor_balance + tx.amount))
            
            current = current.next

    def simplify(self) -> LinkedList[BasicTransaction]:
        """
        Thực hiện đơn giản hóa nợ bằng thuật toán tham lam tối ưu.
        
        Thuật toán:
        1. Kiểm tra điều kiện dừng (danh sách rỗng)
        2. Phân loại người tham gia thành nhóm nợ và nhóm cho vay
        3. Sắp xếp theo thứ tự ưu tiên (số dư lớn nhất trước)
        4. Ghép đôi và tạo giao dịch thanh toán tối ưu
        5. Cập nhật số dư và tiếp tục cho đến khi hết
        
        Trả về:
            LinkedList[BasicTransaction]: Danh sách giao dịch đã được đơn giản hóa
        """
        # Điều kiện dừng: nếu không có giao dịch nào thì trả về danh sách rỗng
        if self.initial_transactions.is_empty():
            return LinkedList()

        # Bước 1: Phân loại người tham gia thành 2 nhóm
        debtors = LinkedList[Tuple]()    # Danh sách người nợ: (tên, số_dư_âm)
        creditors = LinkedList[Tuple]()  # Danh sách người cho vay: (tên, số_dư_dương)
        
        # Duyệt qua tất cả người và phân loại dựa trên số dư
        for person in self.people_balances.keys():
            balance = self.people_balances.get(person)
            
            # Người nợ: số dư âm (dưới ngưỡng -EPSILON để tránh lỗi làm tròn)
            if balance < -EPSILON:
                debtors.append(Tuple([person, balance]))
            # Người cho vay: số dư dương (trên ngưỡng EPSILON để tránh lỗi làm tròn)
            elif balance > EPSILON:
                creditors.append(Tuple([person, balance]))
            # Bỏ qua những người có số dư gần bằng 0 (đã cân bằng)

        # Bước 2: Sắp xếp để đảm bảo tính xác định và tối ưu
        # Sắp xếp người nợ: tăng dần theo số dư (âm lớn nhất trước - nợ nhiều nhất)
        debtors = merge_sort_linked_list(
            debtors, 
            comparator=lambda t1, t2: t1[1] < t2[1]  # t1[1] là số dư, so sánh tăng dần
        )
        
        # Sắp xếp người cho vay: giảm dần theo số dư (dương lớn nhất trước - cho vay nhiều nhất)
        creditors = merge_sort_linked_list(
            creditors, 
            comparator=lambda t1, t2: t1[1] > t2[1]  # t1[1] là số dư, so sánh giảm dần
        )

        # Bước 3: Thực hiện thuật toán tham lam ghép đôi
        simplified_txs = LinkedList[BasicTransaction]()  # Danh sách giao dịch kết quả
        debtor_node = debtors.head      # Con trỏ đến người nợ hiện tại
        creditor_node = creditors.head  # Con trỏ đến người cho vay hiện tại
        
        # Vòng lặp chính: ghép đôi cho đến khi hết người nợ hoặc người cho vay
        while debtor_node and creditor_node:
            # Lấy thông tin người nợ và người cho vay hiện tại
            debtor_name, debtor_balance = debtor_node.data
            creditor_name, creditor_balance = creditor_node.data
            
            # Tính số tiền thanh toán tối ưu (nguyên tắc tham lam)
            # Chọn min để đảm bảo không vượt quá khả năng của cả 2 bên
            settle_amount = min(-debtor_balance, creditor_balance)
            
            # Chỉ tạo giao dịch nếu số tiền thanh toán đủ lớn (tránh giao dịch vô nghĩa)
            if settle_amount > EPSILON:
                # Tạo giao dịch thanh toán mới
                new_transaction = BasicTransaction(
                    debtor=debtor_name, 
                    creditor=creditor_name, 
                    amount=settle_amount
                )
                simplified_txs.append(new_transaction)
                
                # Cập nhật số dư sau khi thanh toán
                debtor_balance += settle_amount    # Người nợ giảm nợ (balance âm tăng lên)
                creditor_balance -= settle_amount  # Người cho vay giảm khoản cho vay
                
                # Cập nhật lại giá trị trong Tuple (vì Tuple là immutable, phải tạo mới)
                debtor_node.data = Tuple([debtor_name, debtor_balance])
                creditor_node.data = Tuple([creditor_name, creditor_balance])
            
            # Bước 4: Chuyển đến người tiếp theo nếu đã thanh toán xong
            # Nếu người nợ đã hết nợ (số dư gần bằng 0), chuyển sang người nợ tiếp theo
            if abs(debtor_balance) < EPSILON:
                debtor_node = debtor_node.next
                
            # Nếu người cho vay đã được trả hết (số dư gần bằng 0), chuyển sang người cho vay tiếp theo
            if creditor_balance < EPSILON:
                creditor_node = creditor_node.next
        
        # Trả về danh sách giao dịch đã được đơn giản hóa
        return simplified_txs