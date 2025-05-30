from __future__ import annotations

from src.core_types import AdvancedTransaction, Person
from src.data_structures import LinkedList, HashTable, PriorityQueue, Tuple, Array, Graph
from src.utils.sorting import merge_sort_linked_list, merge_sort_array
from src.utils.time_interest_calculator import TimeInterestCalculator
from src.utils.money_utils import round_money
from datetime import date

# DPValueTuple: Represents the value stored in the DP table for a given state.
# (total_accumulated_financial_cost, total_accumulated_simplified_tx_count, combined_simplified_tx_list)
DPValueTuple = Tuple[float | int | LinkedList[AdvancedTransaction]]

# DPTable Key: (Date of event, CustomTuple of balances)
# DPTable Value: DPValueTuple as defined above.
DPTable = HashTable[Tuple[date], DPValueTuple]

class AdvancedDynamicProgrammingSimplifier:
    """
    Enhanced Timeline-based Dynamic Programming debt simplification algorithm 
    with integrated time and interest calculations.
    
    Key enhancements:
    1. Integrated TimeInterestCalculator for accurate interest and penalty calculations
    2. Enhanced transaction creation with weighted due dates and adjusted interest rates
    3. Proper handling of overdue transactions with penalties
    4. Comprehensive tracking of original transactions for enhanced settlement creation
    """

    def __init__(self, transactions: LinkedList[AdvancedTransaction], current_date: date):
        self.transactions = transactions
        self.current_date = current_date
        self.interest_calculator = TimeInterestCalculator()
        self.graph = Graph[Person, HashTable]()
        self._build_graph()
        self.people: HashTable[str, Person] = HashTable()
        
        # Track original transactions per person for enhanced settlement creation
        self.person_original_transactions: HashTable[str, Array[AdvancedTransaction]] = HashTable()
        
        self.sorted_transactions_by_due_date: LinkedList[AdvancedTransaction] = self._sort_transactions_by_due_date(transactions)
        
        self.person_names_sorted: LinkedList[str] = LinkedList[str]() 
        self._initialize_people()

        # Build timeline events
        self.timeline_events: LinkedList[Tuple[date | LinkedList[AdvancedTransaction]]] = self._build_timeline_events()
        
        self.dp_table: DPTable = HashTable()
        
    def _transaction_due_date_comparator(self, t1: AdvancedTransaction, t2: AdvancedTransaction) -> bool:
        """Compare transactions by due_date, then by amount, debtor, creditor for consistency."""
        if t1.due_date == t2.due_date:
            if t1.amount != t2.amount:
                return t1.amount < t2.amount
            if t1.debtor != t2.debtor:
                return t1.debtor < t2.debtor
            return t1.creditor < t2.creditor
        return t1.due_date < t2.due_date

    def _sort_transactions_by_due_date(self, transactions: LinkedList[AdvancedTransaction]) -> LinkedList[AdvancedTransaction]:
        """Sort LinkedList of transactions using merge_sort_linked_list with custom comparator."""
        if transactions is None or transactions.is_empty():
            return LinkedList()
        return merge_sort_linked_list(transactions, comparator=self._transaction_due_date_comparator)

    def _initialize_people(self) -> None:
        """Initialize HashTable self.people, LinkedList self.person_names_sorted, and track original transactions."""
        unique_names_table: HashTable[str, bool] = HashTable()

        current_tx_node = self.sorted_transactions_by_due_date.head
        while current_tx_node:
            tx = current_tx_node.data
            unique_names_table.put(tx.debtor, True)
            unique_names_table.put(tx.creditor, True)
            
            if not self.people.contains_key(tx.debtor):
                self.people.put(tx.debtor, Person(tx.debtor))
            if not self.people.contains_key(tx.creditor):
                self.people.put(tx.creditor, Person(tx.creditor))
            
            # Track original transactions for enhanced settlement creation
            if not self.person_original_transactions.contains_key(tx.debtor):
                self.person_original_transactions.put(tx.debtor, Array[AdvancedTransaction]())
            if not self.person_original_transactions.contains_key(tx.creditor):
                self.person_original_transactions.put(tx.creditor, Array[AdvancedTransaction]())
            
            self.person_original_transactions.get(tx.debtor).append(tx)
            self.person_original_transactions.get(tx.creditor).append(tx)
            
            current_tx_node = current_tx_node.next
        
        names_ll = unique_names_table.keys()
        if names_ll is None or names_ll.is_empty():
            self.person_names_sorted = LinkedList[str]()
            return

        self.person_names_sorted = merge_sort_linked_list(names_ll, comparator=lambda a, b: a < b)

    def _build_timeline_events(self) -> LinkedList[Tuple[date | LinkedList[AdvancedTransaction]]]:
        """
        Build timeline events using custom data structures.
        Each event is a Tuple (Date, LinkedList[AdvancedTransaction] of transactions due on that date).
        """
        # Use custom HashTable instead of Python dict
        events_table: HashTable[date, LinkedList[AdvancedTransaction]] = HashTable()
        
        current_tx_node = self.sorted_transactions_by_due_date.head
        while current_tx_node:
            tx = current_tx_node.data
            due_date_of_tx = tx.due_date
            
            if not events_table.contains_key(due_date_of_tx):
                events_table.put(due_date_of_tx, LinkedList[AdvancedTransaction]())
            
            tx_list_for_date = events_table.get(due_date_of_tx)
            if tx_list_for_date is not None:
                tx_list_for_date.append(tx)
            
            current_tx_node = current_tx_node.next
        
        if events_table.is_empty():
            return LinkedList[Tuple[date | LinkedList[AdvancedTransaction]]]()
        
        # Sort dates using custom LinkedList and create timeline
        all_dates = events_table.keys()  # This returns LinkedList[Date]
        sorted_dates = merge_sort_linked_list(all_dates, comparator=lambda a, b: a < b)
        
        timeline: LinkedList[Tuple[date | LinkedList[AdvancedTransaction]]] = LinkedList()
        
        current_date_node = sorted_dates.head
        while current_date_node:
            date_key = current_date_node.data
            transactions_for_date = events_table.get(date_key)
            
            if transactions_for_date is not None and not transactions_for_date.is_empty():
                # Create custom Tuple with Date and LinkedList[AdvancedTransaction]
                # Convert to list for Tuple constructor
                event_data = [date_key, transactions_for_date]
                event_tuple = Tuple(event_data)
                timeline.append(event_tuple)
            
            current_date_node = current_date_node.next
        
        return timeline

    def _get_current_balances_tuple(self, people_balances: HashTable[str, float]) -> Tuple[float]:
        """
        Convert current balance state (from HashTable) to a Tuple of floats.
        Uses self.person_names_sorted to ensure consistent ordering.
        """
        # Collect balances in a list first
        balance_values = []
        current_name_node = self.person_names_sorted.head
        while current_name_node:
            name = current_name_node.data
            balance_values.append(people_balances.get(name, 0.0))
            current_name_node = current_name_node.next
        
        return Tuple(balance_values)

    def _deep_copy_balances(self, source_balances: HashTable[str, float]) -> HashTable[str, float]:
        """Create a deep copy of the balances HashTable."""
        copy_balances = HashTable[str, float]()
        if source_balances and not source_balances.is_empty():
            keys = source_balances.keys()
            if keys:
                node = keys.head
                while node:
                    key = node.data
                    copy_balances.put(key, source_balances.get(key, 0.0))
                    node = node.next
        return copy_balances

    def _calculate_enhanced_transaction_amount(self, tx: AdvancedTransaction, processing_date: date) -> Tuple[float | float]:
        """
        Calculate the actual amount owed including interest and penalties.
        Returns Tuple(actual_amount, penalty_cost)
        """
        base_amount_with_interest = self.interest_calculator.calculate_total_amount_with_interest(
            tx.amount, tx.interest_rate, tx.borrow_date, tx.due_date
        )
        
        penalty_cost = 0.0
        if processing_date > tx.due_date:
            # Calculate penalty for overdue transaction
            penalty_cost = self.interest_calculator.calculate_penalty_amount(
                base_amount_with_interest, tx.penalty_fee, tx.due_date, processing_date
            )
        
        total_amount = base_amount_with_interest + penalty_cost
        return Tuple([total_amount, penalty_cost])

    def _create_enhanced_settlement_transaction(self, debtor_name: str, creditor_name: str,
                                              settle_amount: float, processing_date: date) -> AdvancedTransaction:
        """
        Create an enhanced settlement transaction with integrated time and interest calculations.
        Similar to the enhanced greedy approach but adapted for DP context.
        """
        related_transactions = Array[AdvancedTransaction]()

        # Collect related transactions for both debtor and creditor
        if self.person_original_transactions.contains_key(debtor_name):
            debtor_txs = self.person_original_transactions.get(debtor_name)
            for tx in debtor_txs:
                related_transactions.append(tx)

        if self.person_original_transactions.contains_key(creditor_name):
            creditor_txs = self.person_original_transactions.get(creditor_name)
            for tx in creditor_txs:
                # Avoid duplicates
                already_added = False
                for existing_tx in related_transactions:
                    if (existing_tx.debtor == tx.debtor and
                        existing_tx.creditor == tx.creditor and
                        abs(existing_tx.amount - tx.amount) < 1e-9 and
                        existing_tx.due_date == tx.due_date):
                        already_added = True
                        break
                if not already_added:
                    related_transactions.append(tx)

        # If no related transactions, create basic settlement
        if len(related_transactions) == 0:
            return AdvancedTransaction(
                debtor=debtor_name,
                creditor=creditor_name,
                amount=settle_amount,
                borrow_date=processing_date,
                due_date=processing_date,
                interest_rate=0.0,
                penalty_fee=0.0,
                status=f"DP Settlement on {processing_date} (no original transactions)"
            )

        # Calculate enhanced due date and interest rate using TimeInterestCalculator
        enhanced_due_date = self.interest_calculator.calculate_weighted_due_date(related_transactions)
        adjusted_interest_rate = self.interest_calculator.calculate_adjusted_interest_rate(
            related_transactions, processing_date, enhanced_due_date
        )
        
        # Calculate total amount with enhanced interest
        total_amount_with_interest = self.interest_calculator.calculate_total_amount_with_interest(
            settle_amount, adjusted_interest_rate, processing_date, enhanced_due_date
        )

        return AdvancedTransaction(
            debtor=debtor_name,
            creditor=creditor_name,
            amount=total_amount_with_interest,
            borrow_date=processing_date,
            due_date=enhanced_due_date,
            interest_rate=adjusted_interest_rate,
            penalty_fee=0.0,
            status=f"Enhanced DP Settlement on {processing_date} (with time/interest integration)"
        )

    def _find_optimal_settlements(self, current_processing_date: date, 
                                  transactions_due_today: LinkedList[AdvancedTransaction], 
                                  current_balances: HashTable[str, float]
                                 ) -> Tuple[LinkedList[AdvancedTransaction] | Tuple[float | int] | HashTable[str, float]]: 
        """
        Enhanced process transactions due today and perform greedy settlement with time/interest integration.
        Returns: Tuple containing (simplified_transactions_today, 
                 Tuple(cost_incurred_today, tx_count_created_today), 
                 next_balances_map)
        """
        
        temp_simplified_tx_today = LinkedList[AdvancedTransaction]()
        financial_cost_incurred_today = 0.0
        num_tx_created_today = 0

        # Deep copy current balances to avoid reference issues
        balances_after_today_dues = self._deep_copy_balances(current_balances)
        
        # Apply due transactions to balances with enhanced interest and penalty calculations
        tx_node = transactions_due_today.head
        while tx_node:
            tx = tx_node.data
            
            # Calculate enhanced amount with interest and penalties
            enhanced_amount_result = self._calculate_enhanced_transaction_amount(tx, current_processing_date)
            actual_amount = enhanced_amount_result.data[0] if hasattr(enhanced_amount_result, 'data') else enhanced_amount_result[0]
            penalty_cost = enhanced_amount_result.data[1] if hasattr(enhanced_amount_result, 'data') else enhanced_amount_result[1]
            
            # Add penalty cost to total financial cost
            financial_cost_incurred_today += penalty_cost
            
            # Update balances with actual calculated amount
            current_debtor_balance = balances_after_today_dues.get(tx.debtor, 0.0)
            current_creditor_balance = balances_after_today_dues.get(tx.creditor, 0.0)
            
            balances_after_today_dues.put(tx.debtor, current_debtor_balance - actual_amount)
            balances_after_today_dues.put(tx.creditor, current_creditor_balance + actual_amount)
            
            tx_node = tx_node.next

        # Perform enhanced greedy settlement using priority queues
        # Create comparators for min-heap (debtors) and max-heap (creditors)
        def debtor_comparator(tuple1: Tuple[str | float], tuple2: Tuple[str | float]) -> bool:
            """Min-heap comparator for debtors (largest debt first for efficiency)"""
            balance1 = tuple1.data[1] if hasattr(tuple1, 'data') else tuple1[1]
            balance2 = tuple2.data[1] if hasattr(tuple2, 'data') else tuple2[1]
            return abs(balance1) > abs(balance2)  # Prioritize larger debts
        
        def creditor_comparator(tuple1: Tuple[str | float], tuple2: Tuple[str | float]) -> bool:
            """Max-heap comparator for creditors (largest credit first)"""
            balance1 = tuple1.data[1] if hasattr(tuple1, 'data') else tuple1[1]
            balance2 = tuple2.data[1] if hasattr(tuple2, 'data') else tuple2[1]
            return balance1 > balance2  # Max-heap: larger (more positive) values have priority
        
        # Initialize priority queues with proper comparators
        debtors_pq = PriorityQueue[Tuple[str | float]](comparator=debtor_comparator)
        creditors_pq = PriorityQueue[Tuple[str | float]](comparator=creditor_comparator)

        # Populate priority queues
        balance_keys = balances_after_today_dues.keys()
        if balance_keys:
            bal_node = balance_keys.head
            while bal_node:
                person = bal_node.data
                balance = balances_after_today_dues.get(person, 0.0)
                if balance < -1e-9:  # Debtor (negative balance)
                    debtor_tuple = Tuple([person, balance])
                    debtors_pq.enqueue(debtor_tuple, abs(balance))
                elif balance > 1e-9:  # Creditor (positive balance)
                    creditor_tuple = Tuple([person, balance])
                    creditors_pq.enqueue(creditor_tuple, balance)
                bal_node = bal_node.next
        
        next_balances_after_settlement = self._deep_copy_balances(balances_after_today_dues)

        # Enhanced greedy settlement: match highest debtor with highest creditor
        while not debtors_pq.is_empty() and not creditors_pq.is_empty():
            top_debtor_tuple = debtors_pq.dequeue()
            top_creditor_tuple = creditors_pq.dequeue()

            # Access tuple elements using array-like indexing
            debtor_name = top_debtor_tuple.data[0] if hasattr(top_debtor_tuple, 'data') else top_debtor_tuple[0]
            debtor_amount_owed_neg = top_debtor_tuple.data[1] if hasattr(top_debtor_tuple, 'data') else top_debtor_tuple[1]
            creditor_name = top_creditor_tuple.data[0] if hasattr(top_creditor_tuple, 'data') else top_creditor_tuple[0]
            creditor_amount_due_pos = top_creditor_tuple.data[1] if hasattr(top_creditor_tuple, 'data') else top_creditor_tuple[1]
            
            debtor_amount_owed = abs(debtor_amount_owed_neg)
            settlement_amount = min(debtor_amount_owed, creditor_amount_due_pos)

            if settlement_amount > 1e-9:
                # Create enhanced settlement transaction
                enhanced_settlement = self._create_enhanced_settlement_transaction(
                    debtor_name, creditor_name, settlement_amount, current_processing_date
                )
                temp_simplified_tx_today.append(enhanced_settlement)
                num_tx_created_today += 1

                # Update balances after settlement
                current_debtor_bal = next_balances_after_settlement.get(debtor_name, 0.0)
                current_creditor_bal = next_balances_after_settlement.get(creditor_name, 0.0)
                
                next_balances_after_settlement.put(debtor_name, current_debtor_bal + settlement_amount)
                next_balances_after_settlement.put(creditor_name, current_creditor_bal - settlement_amount)

                # Re-queue if there are remaining amounts
                remaining_debt = debtor_amount_owed - settlement_amount
                remaining_credit = creditor_amount_due_pos - settlement_amount

                if remaining_debt > 1e-9:
                    remaining_debtor_tuple = Tuple([debtor_name, -remaining_debt])
                    debtors_pq.enqueue(remaining_debtor_tuple, remaining_debt)
                if remaining_credit > 1e-9:
                    remaining_creditor_tuple = Tuple([creditor_name, remaining_credit])
                    creditors_pq.enqueue(remaining_creditor_tuple, remaining_credit)
        
        # Create cost metrics tuple
        cost_metrics_today = Tuple([financial_cost_incurred_today, num_tx_created_today])
        
        # Return as custom Tuple
        return_data = [temp_simplified_tx_today, cost_metrics_today, next_balances_after_settlement]
        return Tuple(return_data)

    def solve_dp(self, event_idx: int, current_balances_map: HashTable[str, float]) -> DPValueTuple:
        """Enhanced recursive DP solver with memoization and time/interest integration."""
        # Base case: no more events to process
        if event_idx >= self.timeline_events.get_length():
            return Tuple([0.0, 0, LinkedList[AdvancedTransaction]()])

        # Check memoization
        balances_tuple_key = self._get_current_balances_tuple(current_balances_map)
        current_event = self.timeline_events.get_at_index(event_idx)
        
        # Access tuple elements properly
        current_event_date = current_event.data[0] if hasattr(current_event, 'data') else current_event[0]
        
        memo_key_data = [current_event_date, balances_tuple_key]
        memo_key = Tuple(memo_key_data)

        if self.dp_table.contains_key(memo_key):
            return self.dp_table.get(memo_key)

        # Process current event with enhanced settlement
        transactions_due_this_event_date = current_event.data[1] if hasattr(current_event, 'data') else current_event[1]

        enhanced_settlement_result = self._find_optimal_settlements(
            current_event_date, 
            transactions_due_this_event_date, 
            current_balances_map
        )
        
        # Access settlement result elements
        settlements_today_ll = enhanced_settlement_result.data[0] if hasattr(enhanced_settlement_result, 'data') else enhanced_settlement_result[0]
        cost_metrics_today = enhanced_settlement_result.data[1] if hasattr(enhanced_settlement_result, 'data') else enhanced_settlement_result[1]
        next_event_balances_map = enhanced_settlement_result.data[2] if hasattr(enhanced_settlement_result, 'data') else enhanced_settlement_result[2]
        
        today_financial_cost = cost_metrics_today.data[0] if hasattr(cost_metrics_today, 'data') else cost_metrics_today[0]
        today_tx_count = cost_metrics_today.data[1] if hasattr(cost_metrics_today, 'data') else cost_metrics_today[1]

        # Recursively solve for future events
        future_result = self.solve_dp(event_idx + 1, next_event_balances_map)
        
        future_financial_cost = future_result.data[0] if hasattr(future_result, 'data') else future_result[0]
        future_tx_count = future_result.data[1] if hasattr(future_result, 'data') else future_result[1]
        future_tx_list = future_result.data[2] if hasattr(future_result, 'data') else future_result[2]

        # Combine results
        total_accumulated_financial_cost = today_financial_cost + future_financial_cost
        total_accumulated_tx_count = today_tx_count + future_tx_count
        
        # Combine transaction lists
        combined_simplified_tx_list = LinkedList[AdvancedTransaction]()
        
        # Add today's enhanced settlements
        current_settlement_node = settlements_today_ll.head
        while current_settlement_node:
            combined_simplified_tx_list.append(current_settlement_node.data)
            current_settlement_node = current_settlement_node.next
        
        # Add future transactions
        current_future_tx_node = future_tx_list.head
        while current_future_tx_node:
            combined_simplified_tx_list.append(current_future_tx_node.data)
            current_future_tx_node = current_future_tx_node.next

        result_data = [
            total_accumulated_financial_cost, 
            total_accumulated_tx_count, 
            combined_simplified_tx_list
        ]
        result_for_current_state: DPValueTuple = Tuple(result_data)

        # Memoize result
        self.dp_table.put(memo_key, result_for_current_state)
        return result_for_current_state

    def simplify(self) -> LinkedList[AdvancedTransaction]:
        """Enhanced main simplification method with time/interest integration."""
        if self.transactions.is_empty():
            return LinkedList[AdvancedTransaction]()

        # Clear memoization table
        self.dp_table.clear()

        # Initialize balances (all start at 0.0)
        initial_balances_map = HashTable[str, float]()
        current_person_node = self.person_names_sorted.head
        while current_person_node:
            person_name = current_person_node.data
            initial_balances_map.put(person_name, 0.0)
            current_person_node = current_person_node.next
        
        # Check if we have any timeline events
        if self.timeline_events.is_empty():
            return LinkedList[AdvancedTransaction]()

        # Solve using enhanced DP
        final_result = self.solve_dp(0, initial_balances_map)
        
        # Access final result elements
        _final_cost = final_result.data[0] if hasattr(final_result, 'data') else final_result[0]
        _final_tx_count = final_result.data[1] if hasattr(final_result, 'data') else final_result[1]
        simplified_transactions_ll = final_result.data[2] if hasattr(final_result, 'data') else final_result[2]
        
        # Sort final results for consistency
        if not simplified_transactions_ll.is_empty():
            simplified_transactions_ll = merge_sort_linked_list(
                simplified_transactions_ll,
                comparator=lambda tx1, tx2: (tx1.debtor, tx1.creditor, tx1.amount) < (tx2.debtor, tx2.creditor, tx2.amount)
            )

        return simplified_transactions_ll

    def get_enhanced_summary_statistics(self) -> dict:
        """Return enhanced summary statistics about the DP simplification process."""
        original_count = len(self.transactions)
        
        # Run simplification to get results
        simplified_transactions = self.simplify()
        simplified_count = len(simplified_transactions)

        total_original_amount = 0.0
        total_simplified_amount = 0.0

        # Calculate total original amounts with interest and penalties
        current_tx_node = self.transactions.head
        while current_tx_node:
            tx = current_tx_node.data
            enhanced_amount_result = self._calculate_enhanced_transaction_amount(tx, self.current_date)
            actual_amount = enhanced_amount_result.data[0] if hasattr(enhanced_amount_result, 'data') else enhanced_amount_result[0]
            total_original_amount += actual_amount
            current_tx_node = current_tx_node.next

        # Calculate total simplified amounts
        current_simplified_node = simplified_transactions.head
        while current_simplified_node:
            tx = current_simplified_node.data
            total_simplified_amount += tx.amount
            current_simplified_node = current_simplified_node.next

        return {
            "original_transaction_count": original_count,
            "simplified_transaction_count": simplified_count,
            "reduction_count": original_count - simplified_count,
            "reduction_percentage": ((original_count - simplified_count) / original_count * 100) if original_count > 0 else 0,
            "total_original_amount_with_interest": total_original_amount,
            "total_simplified_amount": total_simplified_amount,
            "current_date": self.current_date,
            "algorithm": "Enhanced Timeline DP with Time/Interest Integration"
        }

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

    def _find_dp_solution(self) -> Array[AdvancedTransaction]:
        """Find an optimal solution using dynamic programming."""
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


if __name__ == '__main__':
    pass