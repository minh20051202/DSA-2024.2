#!/usr/bin/env python3

"""
Utility functions and constants for the Debt Simplification Algorithm.
"""

import os
import csv

def load_sample_transactions(sample_path=None):
    """
    Load sample transactions from a CSV file.
    
    Args:
        sample_path (str, optional): Path to the CSV file. Defaults to src/samples/sample_transactions.csv.
        
    Returns:
        tuple: (TransactionGraph, list) containing the transaction graph and list of original transactions
    """
    # Import here to avoid circular import
    from src.data_structures.transaction_graph import TransactionGraph
    
    transaction_graph = TransactionGraph()
    original_transactions = []
    
    # Default path to sample transactions
    if sample_path is None:
        sample_path = os.path.join('src', 'samples', 'sample_transactions.csv')
    
    with open(sample_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            if len(row) >= 3:
                debtor = row[0].strip()
                creditor = row[1].strip()
                amount = float(row[2].strip())
                transaction_graph.add_transaction(debtor, creditor, amount)
                
                # Also store in our list
                original_transactions.append({
                    "debtor": debtor,
                    "creditor": creditor,
                    "amount": amount
                })
    
    return transaction_graph, original_transactions 