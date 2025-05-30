#!/usr/bin/env python3
"""
Benchmark script for comparing performance of debt simplification algorithms.
Tests all 4 algorithms with various input sizes and scenarios.
"""

import time
import random
from typing import List, Tuple
from src.core_types import BasicTransaction
from src.data_structures import LinkedList
from src.algorithms.basic_transactions.greedy import GreedySimplifier
from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier
from src.algorithms.basic_transactions.min_cost_max_flow import MinCostMaxFlowSimplifier
from src.algorithms.basic_transactions.cycle_detector import DebtCycleSimplifier

def generate_test_case(num_people: int, num_transactions: int, max_amount: float = 1000.0) -> LinkedList[BasicTransaction]:
    """
    Generate a random test case with specified number of people and transactions.
    
    Args:
        num_people: Number of unique people in the network
        num_transactions: Number of transactions to generate
        max_amount: Maximum amount for any transaction
        
    Returns:
        LinkedList[BasicTransaction]: List of generated transactions
    """
    transactions = LinkedList[BasicTransaction]()
    people = [f"Person_{i}" for i in range(num_people)]
    
    for _ in range(num_transactions):
        debtor = random.choice(people)
        creditor = random.choice([p for p in people if p != debtor])
        amount = round(random.uniform(1.0, max_amount), 2)
        
        transactions.append(BasicTransaction(
            debtor=debtor,
            creditor=creditor,
            amount=amount
        ))
    
    return transactions

def count_transactions(transactions: LinkedList[BasicTransaction]) -> int:
    """
    Count the number of transactions in a LinkedList.
    
    Args:
        transactions: LinkedList of transactions to count
        
    Returns:
        int: Number of transactions
    """
    count = 0
    current = transactions.head
    while current:
        count += 1
        current = current.next
    return count

def run_benchmark(transactions: LinkedList[BasicTransaction], algorithm_name: str) -> Tuple[float, int]:
    """
    Run a single benchmark test for a specific algorithm.
    
    Args:
        transactions: Input transactions to simplify
        algorithm_name: Name of the algorithm to test
        
    Returns:
        Tuple[float, int]: (execution_time, num_simplified_transactions)
    """
    start_time = time.time()
    
    if algorithm_name == "Greedy":
        simplifier = GreedySimplifier(transactions)
    elif algorithm_name == "Dynamic Programming":
        simplifier = DynamicProgrammingSimplifier(transactions)
    elif algorithm_name == "Min-Cost Max-Flow":
        simplifier = MinCostMaxFlowSimplifier(transactions)
    elif algorithm_name == "Cycle Detection":
        simplifier = DebtCycleSimplifier(transactions)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    result = simplifier.simplify()
    end_time = time.time()
    
    return (end_time - start_time, result.get_length())

def main():
    # Test configurations
    test_cases = [
        (5, 10),    # Small: 5 people, 10 transactions
        (10, 20),   # Medium: 10 people, 20 transactions
        (20, 40),   # Large: 20 people, 40 transactions
        (50, 100),  # Very large: 50 people, 100 transactions
    ]
    
    algorithms = [
        "Greedy",
        "Dynamic Programming",
        "Min-Cost Max-Flow",
        "Cycle Detection"
    ]
    
    # Run benchmarks
    print("\nDebt Simplification Algorithms Benchmark")
    print("=" * 80)
    
    for num_people, num_transactions in test_cases:
        print(f"\nTest Case: {num_people} people, {num_transactions} transactions")
        print("-" * 60)
        
        # Generate test case
        transactions = generate_test_case(num_people, num_transactions)
        
        # Run each algorithm
        for algo in algorithms:
            try:
                execution_time, num_simplified = run_benchmark(transactions, algo)
                print(f"{algo:20} | Time: {execution_time:.4f}s | Simplified to: {num_simplified} transactions")
            except Exception as e:
                print(f"{algo:20} | Error: {str(e)}")
        
        print("-" * 60)

if __name__ == "__main__":
    main() 