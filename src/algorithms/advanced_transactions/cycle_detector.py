from __future__ import annotations
from typing import TYPE_CHECKING
from src.core_types import Person, AdvancedTransaction
from src.data_structures import LinkedList, HashTable, Array, Tuple, Graph
from src.utils.sorting import merge_sort_array
from src.utils.time_interest_calculator import TimeInterestCalculator
from datetime import date
from src.utils.money_utils import round_money

class AdvancedDebtCycleSimplifier:
    """
    Enhanced version of the debt cycle detection and simplification algorithm
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

    def _find_cycles(self) -> Array[Array[AdvancedTransaction]]:
        """Find all cycles in the transaction graph."""
        cycles = Array[Array[AdvancedTransaction]]()
        visited = HashTable[Person, bool]()
        
        def dfs(vertex: Person, path: Array[Person], start: Person):
            if visited.contains_key(vertex):
                if vertex == start and path.get_length() > 2:
                    # Found a cycle
                    cycle_transactions = Array[AdvancedTransaction]()
                    for i in range(path.get_length() - 1):
                        edge_data = self.graph.get_edge_data(path.get(i), path.get(i + 1))
                        cycle_transactions.append(AdvancedTransaction(
                            debtor=path.get(i).name,
                            creditor=path.get(i + 1).name,
                            amount=edge_data.get('amount'),
                            interest_rate=edge_data.get('interest_rate'),
                            borrow_date=edge_data.get('borrow_date'),
                            due_date=edge_data.get('due_date'),
                            penalty_fee=edge_data.get('penalty_fee')
                        ))
                    cycles.append(cycle_transactions)
                return
            
            visited.put(vertex, True)
            path.append(vertex)
            
            for neighbor in self.graph.get_neighbors(vertex):
                if not path.contains(neighbor) or neighbor == start:
                    dfs(neighbor, path, start)
            
            path.remove_at(path.get_length() - 1)
            visited.remove(vertex)
        
        for vertex in self.graph.get_vertices():
            if not visited.contains_key(vertex):
                dfs(vertex, Array[Person](), vertex)
        
        return cycles

    def _simplify_cycle(self, cycle: Array[AdvancedTransaction]) -> Array[AdvancedTransaction]:
        """Simplify a cycle of transactions."""
        if cycle.is_empty():
            return Array[AdvancedTransaction]()
        
        # Calculate total amounts for each person
        balances = HashTable[str, float]()
        for i in range(cycle.get_length()):
            tx = cycle.get(i)
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
                    
                    for tx in cycle:
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
        """Simplify the transaction network by finding and resolving cycles."""
        if self.transactions.is_empty():
            return LinkedList[AdvancedTransaction]()
        
        # Find all cycles
        cycles = self._find_cycles()
        
        # Simplify each cycle
        simplified_transactions = LinkedList[AdvancedTransaction]()
        for i in range(cycles.get_length()):
            cycle = cycles.get(i)
            simplified = self._simplify_cycle(cycle)
            for j in range(simplified.get_length()):
                simplified_transactions.append(simplified.get(j))
        
        # Add remaining transactions that are not part of any cycle
        for tx in self.transactions:
            is_in_cycle = False
            for i in range(cycles.get_length()):
                cycle = cycles.get(i)
                for j in range(cycle.get_length()):
                    if tx == cycle.get(j):
                        is_in_cycle = True
                        break
                if is_in_cycle:
                    break
            if not is_in_cycle:
                simplified_transactions.append(tx)
        
        self.simplified_transactions = simplified_transactions
        return self.simplified_transactions 