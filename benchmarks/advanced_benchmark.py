#!/usr/bin/env python3
"""
Benchmark hiệu năng các thuật toán ĐƠN GIẢN HÓA NỢ NÂNG CAO:
- Đo thời gian chạy, số lượng giao dịch còn lại, và bộ nhớ đỉnh.
- Chạy lặp lại để lấy trung bình và độ lệch chuẩn.
- Chạy tuần tự để đo bộ nhớ chính xác hơn.
"""
import os, sys
import time
import random
import tracemalloc
from statistics import mean, stdev # Thêm stdev
from tabulate import tabulate
from datetime import date, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core_type import AdvancedTransaction, BasicTransaction
from src.data_structures import LinkedList, Tuple
from src.utils.financial_calculator import InterestType, PenaltyType
from src.utils.constants import EPSILON

from src.algorithms.advanced_transactions.greedy import AdvancedGreedySimplifier
from src.algorithms.advanced_transactions.dynamic_programming import AdvancedDynamicProgrammingSimplifier
from src.algorithms.advanced_transactions.min_cost_max_flow import AdvancedMinCostMaxFlowSimplifier
from src.algorithms.advanced_transactions.cycle_detector import AdvancedDebtCycleSimplifier



def generate_advanced_test_case(num_people: int, num_transactions: int,
                                base_date: date, current_date: date,
                                max_amount: float = 1000.0) -> LinkedList[AdvancedTransaction]:
    transaction_list = LinkedList[AdvancedTransaction]()
    people = [f"Person_{i+1}" for i in range(num_people)]

    if num_people < 2 and num_transactions > 0:
        print("Cảnh báo: Không thể tạo giao dịch với ít hơn 2 người.")
        return transaction_list

    for _ in range(num_transactions):
        debtor = random.choice(people)
        possible_creditors = [p for p in people if p != debtor]
        if not possible_creditors:
            continue
        creditor = random.choice(possible_creditors)
        amount = round(random.uniform(1.0, max_amount), 2)

        borrow_days_offset = random.randint(-180, -30) # Vay trong quá khứ, cách base_date
        borrow_date_tx = base_date + timedelta(days=borrow_days_offset)

        due_days_offset = random.randint(-90, 90) # Đến hạn quanh current_date
        due_date_tx = current_date + timedelta(days=due_days_offset)

        if borrow_date_tx > due_date_tx: # Đảm bảo vay trước, đến hạn sau
             # Tạo lại ngày đến hạn xa hơn ngày vay
             extra_days = random.randint(15, 180)
             due_date_tx = borrow_date_tx + timedelta(days=extra_days)
        if due_date_tx < borrow_date_tx : # Hiếm nhưng có thể do offset âm quá lớn
            due_date_tx = borrow_date_tx + timedelta(days=random.randint(30,90))


        interest_rate_tx = round(random.uniform(0.01, 0.15), 4)
        penalty_rate_tx = round(random.uniform(0.0, 50.0), 2)
        interest_type_tx = random.choice(list(InterestType))
        
        if penalty_rate_tx > 1.0 and penalty_rate_tx <= 50.0:
            penalty_type_tx = random.choice([PenaltyType.FIXED, PenaltyType.DAILY])
            if penalty_type_tx == PenaltyType.DAILY and penalty_rate_tx > 5:
                penalty_rate_tx = round(random.uniform(0.1, 5.0), 2)
        elif penalty_rate_tx <= 1.0 and penalty_rate_tx > 0.001: # Cho phép phạt % nhỏ
            penalty_type_tx = PenaltyType.PERCENTAGE
        else:
            penalty_type_tx = PenaltyType.FIXED
            if abs(penalty_rate_tx) < EPSILON: # Nếu rate = 0, type không quá quan trọng
                 penalty_type_tx = random.choice(list(PenaltyType))

        transaction_list.append(AdvancedTransaction(
            debtor, creditor, amount,
            borrow_date_tx, due_date_tx,
            interest_rate_tx, penalty_rate_tx,
            interest_type_tx, penalty_type_tx
        ))
    return transaction_list

def clone_advanced_transactions(original_list: LinkedList[AdvancedTransaction]) -> LinkedList[AdvancedTransaction]:
    cloned_list = LinkedList[AdvancedTransaction]()
    current = original_list.head
    while current:
        tx = current.data
        cloned_list.append(AdvancedTransaction(
            tx.debtor, tx.creditor, tx.amount,
            tx.borrow_date, tx.due_date,
            tx.interest_rate, tx.penalty_rate,
            tx.interest_type, tx.penalty_type
        ))
        current = current.next
    return cloned_list

def run_advanced_benchmark(transactions: LinkedList[AdvancedTransaction],
                           algorithm_name: str,
                           current_date_for_calc: date):
    start_time = time.perf_counter()
    tracemalloc.start()

    cloned_transactions = clone_advanced_transactions(transactions)
    result_list_basic_equiv = LinkedList[BasicTransaction]() # Kết quả cuối cùng để đếm là BasicTransaction

    if algorithm_name == "Advanced Greedy":
        simplifier = AdvancedGreedySimplifier(cloned_transactions, current_date_for_calc)
        result_list_basic_equiv = simplifier.simplify()
    elif algorithm_name == "Advanced DP":
        simplifier = AdvancedDynamicProgrammingSimplifier(cloned_transactions, current_date_for_calc)
        dp_result_tuple = simplifier.simplify()
        if dp_result_tuple and isinstance(dp_result_tuple, Tuple) and len(dp_result_tuple) > 0:
            # dp_result_tuple[0] là LinkedList[BasicTransaction]
            result_list_basic_equiv = dp_result_tuple[0] 
        else:
            print(f"Cảnh báo: Kết quả không hợp lệ hoặc rỗng từ {algorithm_name}")
            result_list_basic_equiv = LinkedList[BasicTransaction]()
    elif algorithm_name == "Advanced Min-Cost Max-Flow":
        simplifier = AdvancedMinCostMaxFlowSimplifier(cloned_transactions, current_date_for_calc)
        result_list_basic_equiv = simplifier.simplify()
    elif algorithm_name == "Advanced Cycle Detection":
        simplifier = AdvancedDebtCycleSimplifier(cloned_transactions, current_date_for_calc)
        # Giả sử simplify_advanced() trả về LinkedList[AdvancedTransaction]
        result_advanced_tx_list = simplifier.simplify_advanced() 
        # Chuyển đổi sang BasicTransaction để đếm cho nhất quán
        if result_advanced_tx_list:
            current_adv_node = result_advanced_tx_list.head
            while current_adv_node:
                adv_tx = current_adv_node.data
                result_list_basic_equiv.append(BasicTransaction(adv_tx.debtor, adv_tx.creditor, adv_tx.amount))
                current_adv_node = current_adv_node.next
    else:
        raise ValueError(f"Unknown advanced algorithm: {algorithm_name}")

    elapsed_time = time.perf_counter() - start_time
    _, memory_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return elapsed_time, len(result_list_basic_equiv), memory_peak // 1024  # KB

def benchmark_average_advanced(transactions: LinkedList[AdvancedTransaction],
                               algorithm_name: str,
                               current_date_for_calc: date,
                               repeat: int = 3):
    num_unique_people = count_unique_people_advanced(transactions)
    
    # Điều chỉnh số lần lặp lại cho DP dựa trên số người thực tế
    if "Advanced DP" in algorithm_name and (num_unique_people > 7 or (num_unique_people * len(transactions) > 100 and num_unique_people > 4)): # Ngưỡng chặt hơn cho advanced
        current_repeat = 1
    else:
        current_repeat = repeat

    results = []
    for i in range(current_repeat):
        # print(f"    Running {algorithm_name} - Iteration {i+1}/{current_repeat}...") # Bật nếu muốn verbose
        try:
            res_tuple = run_advanced_benchmark(transactions, algorithm_name, current_date_for_calc)
            results.append(res_tuple)
        except Exception as e_iter:
            print(f"      ERROR during iteration {i+1} for {algorithm_name}: {e_iter}")
            results.append((float('inf'), float('inf'), float('inf')))

    if not results:
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan')

    valid_results = [r for r in results if r[0] != float('inf')]
    if not valid_results:
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan')

    times = [r[0] for r in valid_results]
    tx_counts = [r[1] for r in valid_results]
    memories = [r[2] for r in valid_results]

    return (
        mean(times),
        stdev(times) if len(times) > 1 else 0.0,
        mean(tx_counts),
        mean(memories),
        stdev(memories) if len(memories) > 1 else 0.0
    )

def count_unique_people_advanced(transactions: LinkedList[AdvancedTransaction]) -> int:
    """Đếm số người duy nhất trong danh sách giao dịch AdvancedTransaction."""
    if transactions.is_empty():
        return 0
    people_set = set()
    current = transactions.head
    while current:
        tx = current.data
        people_set.add(tx.debtor)
        people_set.add(tx.creditor)
        current = current.next
    return len(people_set)

# -----------------------------------
# Hàm chính
# -----------------------------------
def main_advanced_benchmark():
    base_date_bm = date(2023, 1, 1)
    # Ngày tính toán có thể gần hơn để lãi/phạt không quá lớn, hoặc xa hơn để kiểm tra tính toán dài hạn
    current_date_bm = date(2024, 7, 1) # Ví dụ: 1.5 năm sau base_date

    # (num_people, num_transactions)
    input_sizes_advanced = [
        (3, 5),     # Rất nhỏ
        (5, 10),    # Nhỏ
        (7, 20),    # Trung bình
        (10, 30), # Lớn 
    ]

    algorithms_advanced = [
        "Advanced Greedy",
        "Advanced DP",
        "Advanced Min-Cost Max-Flow",
        "Advanced Cycle Detection"
    ]

    print("\n🔍 BENCHMARK COMPARISON OF ADVANCED DEBT SIMPLIFICATION ALGORITHMS")
    print(f"   (Using Base Date: {base_date_bm}, Calculation Date: {current_date_bm})")
    print("=" * 110)

    REPETITIONS = 3 # Mặc định, sẽ được điều chỉnh cho DP

    for num_people_config, num_transactions_config in input_sizes_advanced:
        print(f"\n📊 Test Config: Target {num_people_config} people, {num_transactions_config} transactions")
        print("-" * 110)

        transactions_adv = generate_advanced_test_case(num_people_config, num_transactions_config, base_date_bm, current_date_bm)
        actual_tx_count = len(transactions_adv)
        actual_people_count = count_unique_people_advanced(transactions_adv)
        
        if actual_tx_count == 0 and num_transactions_config > 0 :
            print("   Skipping this config as no transactions were generated.")
            continue
            
        print(f"   Generated: {actual_people_count} unique people, {actual_tx_count} transactions.")

        current_test_case_results = []

        for algo in algorithms_advanced:
            print(f"  Benchmarking {algo}...")
            
            effective_repetitions = REPETITIONS
            # Điều chỉnh mạnh hơn cho Advanced DP vì nó phức tạp hơn nhiều
            if algo == "Advanced DP" and actual_people_count > 6 : # Ngưỡng chặt hơn nữa
                 effective_repetitions = 1
                 print(f"    (Reduced repetitions to {effective_repetitions} for {algo} due to {actual_people_count} people)")
            
            try:
                avg_time, std_time, avg_final_tx, avg_memory_kb, std_memory = benchmark_average_advanced(
                    transactions_adv, algo, current_date_bm, effective_repetitions
                )
                current_test_case_results.append([
                    algo,
                    f"{avg_time:.4f} ± {std_time:.4f} sec" if avg_time != float('nan') else "ERROR",
                    f"{int(round(avg_final_tx))}" if avg_final_tx != float('nan') else "-",
                    f"{int(round(avg_memory_kb))} ± {int(round(std_memory))} KB" if avg_memory_kb != float('nan') else "-"
                ])
            except Exception as e:
                current_test_case_results.append([algo, "EXCEPTION", "-", "-"])
                print(f"    EXCEPTION while running {algo}: {e}")
        
        print(f"\nResults for Actual: {actual_people_count} people, {actual_tx_count} transactions:")
        print(tabulate(current_test_case_results, headers=["Algorithm", "Avg Time (±StdDev)", "Avg Final Tx", "Avg Peak Memory (±StdDev)"]))

# -----------------------------------
# Điểm bắt đầu chương trình
# -----------------------------------
if __name__ == "__main__":
    main_advanced_benchmark()