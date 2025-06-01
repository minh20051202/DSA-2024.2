#!/usr/bin/env python3
"""
Benchmark hiệu năng các thuật toán ĐƠN GIẢN HÓA NỢ CƠ BẢN:
- Đo thời gian chạy, số lượng giao dịch còn lại, và bộ nhớ đỉnh.
- Chạy lặp lại để lấy trung bình kết quả.
- Chạy tuần tự để đo bộ nhớ chính xác hơn.
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import random
import tracemalloc
from statistics import mean, stdev
from tabulate import tabulate

from src.core_type import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.greedy import GreedySimplifier
from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier
from src.algorithms.basic_transactions.min_cost_max_flow import MinCostMaxFlowSimplifier
from src.algorithms.basic_transactions.cycle_detector import DebtCycleSimplifier

def generate_basic_test_case(num_people: int, num_transactions: int, max_amount: float = 1000.0) -> LinkedList[BasicTransaction]:
    transaction_list = LinkedList[BasicTransaction]()
    people = [f"Person_{i+1}" for i in range(num_people)] # Đánh số từ 1 cho dễ nhìn
    
    if num_people < 2 and num_transactions > 0:
        print("Cảnh báo: Không thể tạo giao dịch với ít hơn 2 người.")
        return transaction_list

    for _ in range(num_transactions):
        debtor = random.choice(people)
        # Đảm bảo creditor khác debtor
        possible_creditors = [p for p in people if p != debtor]
        if not possible_creditors: # Trường hợp chỉ có 1 người và num_transactions > 0 (ít xảy ra với check ở trên)
            continue
        creditor = random.choice(possible_creditors)
        amount = round(random.uniform(1.0, max_amount), 2)
        transaction_list.append(BasicTransaction(debtor, creditor, amount))
    
    return transaction_list

def clone_basic_transactions(original_list: LinkedList[BasicTransaction]) -> LinkedList[BasicTransaction]:
    cloned_list = LinkedList[BasicTransaction]()
    current = original_list.head
    while current:
        tx = current.data
        cloned_list.append(BasicTransaction(tx.debtor, tx.creditor, tx.amount))
        current = current.next
    return cloned_list

def run_basic_benchmark(transactions: LinkedList[BasicTransaction], algorithm_name: str):
    start_time = time.perf_counter()
    tracemalloc.start()

    cloned_transactions = clone_basic_transactions(transactions)
    result_list = LinkedList[BasicTransaction]()

    if algorithm_name == "Greedy":
        simplifier = GreedySimplifier(cloned_transactions)
        result_list = simplifier.simplify()
    elif algorithm_name == "Dynamic Programming":
        simplifier = DynamicProgrammingSimplifier(cloned_transactions)
        # DP cơ bản trả về LinkedList[BasicTransaction] trực tiếp
        result_list = simplifier.simplify()
    elif algorithm_name == "Min-Cost Max-Flow":
        simplifier = MinCostMaxFlowSimplifier(cloned_transactions)
        result_list = simplifier.simplify()
    elif algorithm_name == "Cycle Detection":
        simplifier = DebtCycleSimplifier(cloned_transactions)
        result_list = simplifier.simplify()
    else:
        raise ValueError(f"Unknown basic algorithm: {algorithm_name}")

    elapsed_time = time.perf_counter() - start_time
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return elapsed_time, len(result_list), peak_mem // 1024  # KB

def benchmark_average_basic(transactions: LinkedList[BasicTransaction], 
                            algorithm_name: str, 
                            repeat: int = 3):
    
    # Điều chỉnh số lần lặp lại cho DP dựa trên kích thước input
    num_unique_people = count_unique_people_basic(transactions)
    # Heuristic: Nếu số người > 7 hoặc (số người * số giao dịch) > một ngưỡng nào đó
    if "Dynamic Programming" in algorithm_name and (num_unique_people > 7 or (num_unique_people * len(transactions) > 150 and num_unique_people > 5)):
        current_repeat = 1
        # print(f"    (Reduced repetitions to {current_repeat} for {algorithm_name} due to complexity with {num_unique_people} people, {len(transactions)} txs)")
    else:
        current_repeat = repeat

    results = []
    for i in range(current_repeat):
        # print(f"    Running {algorithm_name} - Iteration {i+1}/{current_repeat}...") # Có thể bật lại nếu muốn verbose
        try:
            res_tuple = run_basic_benchmark(transactions, algorithm_name)
            results.append(res_tuple)
        except Exception as e_iter:
            print(f"      ERROR during iteration {i+1} for {algorithm_name}: {e_iter}")
            results.append((float('inf'), float('inf'), float('inf')))


    if not results:
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan') # Thêm std_devs

    valid_results = [r for r in results if r[0] != float('inf')]
    if not valid_results:
        return float('nan'), float('nan'), float('nan'), float('nan'), float('nan')

    times = [r[0] for r in valid_results]
    tx_counts = [r[1] for r in valid_results]
    memories = [r[2] for r in valid_results]

    return (
        mean(times),
        stdev(times) if len(times) > 1 else 0.0, # Độ lệch chuẩn thời gian
        mean(tx_counts),
        mean(memories),
        stdev(memories) if len(memories) > 1 else 0.0 # Độ lệch chuẩn bộ nhớ
    )

def count_unique_people_basic(transactions: LinkedList[BasicTransaction]) -> int:
    """Đếm số người duy nhất trong danh sách giao dịch BasicTransaction."""
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
def main_basic_benchmark():
    # Cấu hình các tập dữ liệu cần benchmark
    # (num_people, num_transactions)
    input_sizes_basic = [
        (5, 10),     # Nhỏ
        (10, 20),    # Trung bình 
        (20, 40),    # Khá lớn
        (40, 70),    # Lớn 
        (70, 100),   # Rất Lớn 
    ]

    # Danh sách các thuật toán CƠ BẢN cần kiểm thử
    algorithms_basic = [
        "Greedy",
        "Dynamic Programming",
        "Min-Cost Max-Flow",
        "Cycle Detection"
    ]

    print("\n🔍 BENCHMARK COMPARISON OF BASIC DEBT SIMPLIFICATION ALGORITHMS")
    print("=" * 110) # Tăng độ rộng bảng

    REPETITIONS = 3 # Số lần lặp lại mặc định

    for num_people_config, num_transactions_config in input_sizes_basic:
        print(f"\n📊 Test Config: Target {num_people_config} people, {num_transactions_config} transactions")
        print("-" * 110)

        transactions_basic = generate_basic_test_case(num_people_config, num_transactions_config)
        actual_tx_count = len(transactions_basic)
        actual_people_count = count_unique_people_basic(transactions_basic)
        
        if actual_tx_count == 0 and num_transactions_config > 0 :
            print("   Skipping this config as no transactions were generated (e.g., num_people < 2).")
            continue
            
        print(f"   Generated: {actual_people_count} unique people, {actual_tx_count} transactions.")


        current_test_case_results = []

        for algo in algorithms_basic:
            print(f"  Benchmarking {algo}...")
            
            effective_repetitions = REPETITIONS
            if algo == "Dynamic Programming" and actual_people_count > 7:
                 effective_repetitions = 1
                 print(f"    (Reduced repetitions to {effective_repetitions} for {algo} due to {actual_people_count} people)")
            
            try:
                avg_time, std_time, avg_final_tx, avg_memory_kb, std_memory = benchmark_average_basic(
                    transactions_basic, algo, effective_repetitions
                )
                current_test_case_results.append([
                    algo,
                    f"{avg_time:.4f} ± {std_time:.4f} sec" if avg_time != float('nan') else "ERROR",
                    f"{int(round(avg_final_tx))}" if avg_final_tx != float('nan') else "-", # Làm tròn số giao dịch trung bình
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
    main_basic_benchmark()