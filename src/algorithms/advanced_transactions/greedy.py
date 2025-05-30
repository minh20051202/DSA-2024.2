from __future__ import annotations
from datetime import date
from src.core_types import Person, AdvancedTransaction
from src.data_structures import LinkedList, HashTable, Array, Tuple, Graph
from src.utils.time_interest_calculator import TimeInterestCalculator
from src.utils.sorting import merge_sort_array
from src.utils.money_utils import round_money

class AdvancedGreedySimplifier:
    """
    Enhanced version of the greedy debt simplification algorithm
    with integrated time and interest calculations.
    """
    def __init__(self, transactions: LinkedList[AdvancedTransaction], current_date: date):
        self.transactions = transactions
        self.current_date = current_date
        self.interest_calculator = TimeInterestCalculator()
        self.graph = Graph[Person, HashTable]()
        self._build_graph()
        self.simplified_transactions: LinkedList[AdvancedTransaction] = LinkedList()

    def _build_graph(self):
        """Build a graph representation of the transactions."""
        for tx in self.transactions:
            debtor = Person(tx.debtor)
            creditor = Person(tx.creditor)
            
            # Add vertices if they don't exist
            if not self.graph.has_vertex(debtor):
                self.graph.add_vertex(debtor)
            if not self.graph.has_vertex(creditor):
                self.graph.add_vertex(creditor)
            
            # Calculate total amount with interest
            total_amount = TimeInterestCalculator.calculate_total_amount_with_interest(
                tx.amount,
                tx.interest_rate,
                tx.borrow_date,
                tx.due_date
            )
            
            # Add edge with transaction data using HashTable
            edge_data = HashTable()
            edge_data.put('amount', round_money(total_amount))
            edge_data.put('interest_rate', tx.interest_rate)
            edge_data.put('borrow_date', tx.borrow_date)
            edge_data.put('due_date', tx.due_date)
            edge_data.put('penalty_fee', tx.penalty_fee if hasattr(tx, 'penalty_fee') else 0)
            
            self.graph.add_edge(debtor, creditor, edge_data)

    def _find_greedy_solution(self) -> Array[AdvancedTransaction]:
        """Find a greedy solution for the transaction network."""
        # Calculate net balances for each person
        balances = HashTable[str, float]()
        for tx in self.transactions:
            debtor_balance = balances.get(tx.debtor, 0.0) - tx.amount
            creditor_balance = balances.get(tx.creditor, 0.0) + tx.amount
            balances.put(tx.debtor, debtor_balance)
            balances.put(tx.creditor, creditor_balance)
        
        # Create new transactions based on net balances
        simplified = Array[AdvancedTransaction]()
        debtors = Array[str]()
        creditors = Array[str]()
        
        # Separate debtors and creditors
        for person, amount in balances.items():
            if amount < 0:  # Person owes money
                debtors.append(person)
            elif amount > 0:  # Person is owed money
                creditors.append(person)
        
        # Sort debtors and creditors by absolute balance
        debtors = merge_sort_array(debtors, lambda a, b: abs(balances.get(a)) > abs(balances.get(b)))
        creditors = merge_sort_array(creditors, lambda a, b: balances.get(a) > balances.get(b))
        
        # Create new transactions
        for debtor in debtors:
            debtor_amount = abs(balances.get(debtor))
            for creditor in creditors:
                if debtor_amount <= 0:
                    break
                    
                creditor_amount = balances.get(creditor)
                if creditor_amount <= 0:
                    continue
                
                transfer_amount = min(debtor_amount, creditor_amount)
                if transfer_amount > 0:
                    # Calculate weighted average interest rate and dates
                    weighted_interest = 0.0
                    weighted_borrow_date = date(2000, 1, 1)  # Epoch date
                    weighted_due_date = date(2000, 1, 1)  # Epoch date
                    total_weight = 0.0
                    
                    for tx in self.transactions:
                        if tx.debtor == debtor or tx.creditor == creditor:
                            weight = tx.amount
                            weighted_interest += tx.interest_rate * weight
                            weighted_borrow_date = max(weighted_borrow_date, tx.borrow_date)
                            weighted_due_date = max(weighted_due_date, tx.due_date)
                            total_weight += weight
                    
                    if total_weight > 0:
                        weighted_interest /= total_weight
                    
                    simplified.append(AdvancedTransaction(
                        debtor=debtor,
                        creditor=creditor,
                        amount=round_money(transfer_amount),
                        interest_rate=round(weighted_interest, 4),
                        borrow_date=weighted_borrow_date,
                        due_date=weighted_due_date
                    ))
                    
                    debtor_amount -= transfer_amount
                    balances.put(creditor, creditor_amount - transfer_amount)
        
        return simplified

    def simplify(self) -> LinkedList[AdvancedTransaction]:
        """Simplify the transaction network using a greedy approach."""
        if self.transactions.is_empty():
            return LinkedList[AdvancedTransaction]()
        
        # Find greedy solution
        simplified = self._find_greedy_solution()
        
        # Convert Array to LinkedList
        simplified_transactions = LinkedList[AdvancedTransaction]()
        for i in range(simplified.get_length()):
            simplified_transactions.append(simplified.get(i))
        
        self.simplified_transactions = simplified_transactions
        return self.simplified_transactions