#!/usr/bin/env python3

"""
Các hàm tiện ích và hằng số cho Thuật Toán Đơn Giản Hóa Nợ.
"""

import os
import csv

def load_sample_transactions(sample_path=None):
    """
    Tải các giao dịch mẫu từ file CSV.
    
    Args:
        sample_path (str, optional): Đường dẫn đến file CSV. Mặc định là src/samples/sample_transactions.csv.
        
    Returns:
        tuple: (TransactionGraph, list) chứa đồ thị giao dịch và danh sách các giao dịch gốc
    """
    # Import ở đây để tránh import vòng
    from src.data_structures.transaction_graph import TransactionGraph
    
    transaction_graph = TransactionGraph()
    original_transactions = []
    
    # Đường dẫn mặc định đến file giao dịch mẫu
    if sample_path is None:
        sample_path = os.path.join('src', 'samples', 'sample_transactions.csv')
    
    with open(sample_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Bỏ qua header
        
        for row in reader:
            if len(row) >= 3:
                debtor = row[0].strip()
                creditor = row[1].strip()
                amount = float(row[2].strip())
                transaction_graph.add_transaction(debtor, creditor, amount)
                
                # Lưu vào danh sách của chúng ta
                original_transactions.append({
                    "debtor": debtor,
                    "creditor": creditor,
                    "amount": amount
                })
    
    return transaction_graph, original_transactions 