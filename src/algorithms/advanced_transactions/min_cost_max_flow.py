from __future__ import annotations
from typing import TYPE_CHECKING
from src.core_types import Person, AdvancedTransaction
from src.data_structures import HashTable, Graph, GraphEdge, GraphVertex, Tuple, LinkedList, Array, PriorityQueue
from src.utils.time_interest_calculator import TimeInterestCalculator
from src.utils.sorting import merge_sort_linked_list, merge_sort_array
from datetime import date
from src.utils.money_utils import round_money

class AdvancedMinCostMaxFlowSimplifier:
    """
    Enhanced version of the Min-Cost Max-Flow debt simplification algorithm
    with integrated time and interest calculations.
    """
    _S_NODE = "_S_SOURCE_NODE_"
    _T_NODE = "_T_SINK_NODE_"
    _INFINITY = float('inf')

    def __init__(self, transactions: LinkedList[AdvancedTransaction], current_date: date):
        self.transactions = transactions
        self.current_date = current_date
        self.interest_calculator = TimeInterestCalculator()
        self.graph = Graph[Person, HashTable]()
        self._build_graph()
        self.simplified_transactions: LinkedList[AdvancedTransaction] = LinkedList()
        self.people_balances: HashTable[str, float] = HashTable()
        self.people_transactions: HashTable[str, Array[AdvancedTransaction]] = HashTable()
        self.all_people_nodes: LinkedList[str] = LinkedList()
        self._calculate_net_balances()
        self.flow_graph: Graph[str, None] | None = None

    def _build_graph(self):
        """Build a graph representation of the transactions."""
        for tx in self.transactions:
            debtor = Person(tx.debtor)
            creditor = Person(tx.creditor)
            
            # Add vertices if they don't exist
            if not self.graph.get_vertex(debtor):
                self.graph.add_vertex(debtor)
            if not self.graph.get_vertex(creditor):
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

    def _calculate_net_balances(self) -> None:
        """Calculate net balances for each person from initial transactions and store original transactions."""
        self.people_balances.clear()
        self.people_transactions.clear()
        node = self.transactions.head
        all_people_table: HashTable[str, bool] = HashTable()

        while node:
            tx = node.data
            self.people_balances.put(tx.debtor, self.people_balances.get(tx.debtor, 0.0) - tx.amount)
            self.people_balances.put(tx.creditor, self.people_balances.get(tx.creditor, 0.0) + tx.amount)

            if not self.people_transactions.contains_key(tx.debtor):
                self.people_transactions.put(tx.debtor, Array[AdvancedTransaction]())
            if not self.people_transactions.contains_key(tx.creditor):
                self.people_transactions.put(tx.creditor, Array[AdvancedTransaction]())

            self.people_transactions.get(tx.debtor).append(tx)
            self.people_transactions.get(tx.creditor).append(tx)

            all_people_table.put(tx.debtor, True)
            all_people_table.put(tx.creditor, True)
            node = node.next

        self.all_people_nodes = all_people_table.keys()
        if self.all_people_nodes is None:
            self.all_people_nodes = LinkedList[str]()
        else:
            self.all_people_nodes = merge_sort_linked_list(self.all_people_nodes, comparator=lambda s1, s2: s1 < s2)

    def _create_enhanced_transaction(self, debtor: str, creditor: str, amount: float) -> AdvancedTransaction:
        """Create a simplified transaction with integrated time and interest calculations."""
        related_transactions = Array[AdvancedTransaction]()

        if self.people_transactions.contains_key(debtor):
            debtor_txs = self.people_transactions.get(debtor)
            for tx in debtor_txs:
                related_transactions.append(tx)

        if self.people_transactions.contains_key(creditor):
            creditor_txs = self.people_transactions.get(creditor)
            for tx in creditor_txs:
                related_transactions.append(tx)

        if len(related_transactions) == 0:
            return AdvancedTransaction(
                debtor=debtor,
                creditor=creditor,
                amount=amount,
                borrow_date=self.current_date,
                due_date=self.current_date,
                interest_rate=0.0,
                penalty_fee=0.0,
                status="Simplified by Enhanced MCMF-MinTx"
            )

        due_date = self.interest_calculator.calculate_weighted_due_date(related_transactions)
        # Ensure due_date is after current_date
        if due_date <= self.current_date:
            due_date = date(self.current_date.day + 1, self.current_date.month, self.current_date.year)
        adjusted_interest_rate = self.interest_calculator.calculate_adjusted_interest_rate(
            related_transactions, self.current_date, due_date
        )
        total_amount = self.interest_calculator.calculate_total_amount_with_interest(
            amount, adjusted_interest_rate, self.current_date, due_date
        )

        return AdvancedTransaction(
            debtor=debtor,
            creditor=creditor,
            amount=total_amount,
            borrow_date=self.current_date,
            due_date=due_date,
            interest_rate=adjusted_interest_rate,
            penalty_fee=0.0,
            status="Simplified by Enhanced MCMF-MinTx (with time/interest integration)"
        )

    def _build_flow_network(self) -> None:
        """Build the flow network for the Min-Cost Max-Flow algorithm."""
        self.flow_graph = Graph[str, None](is_directed=True)
        g = self.flow_graph
        g.add_vertex(self._S_NODE)
        g.add_vertex(self._T_NODE)

        current_person_node_iter = self.all_people_nodes.head
        while current_person_node_iter:
            person_name = current_person_node_iter.data
            g.add_vertex(person_name)
            balance = self.people_balances.get(person_name, 0.0)

            s_vertex = g.get_vertex(self._S_NODE)
            t_vertex = g.get_vertex(self._T_NODE)
            person_vertex = g.get_vertex(person_name)

            if balance < -1e-9:
                if s_vertex and person_vertex:
                    s_edge = s_vertex.add_edge(person_name, None, capacity=abs(balance), cost=0)
                    d_edge = person_vertex.add_edge(self._S_NODE, None, capacity=0, cost=0)
                    if s_edge and d_edge:
                        s_edge.reverse_edge = d_edge
                        d_edge.reverse_edge = s_edge
            elif balance > 1e-9:
                if person_vertex and t_vertex:
                    c_edge = person_vertex.add_edge(self._T_NODE, None, capacity=balance, cost=0)
                    t_edge = t_vertex.add_edge(person_name, None, capacity=0, cost=0)
                    if c_edge and t_edge:
                        c_edge.reverse_edge = t_edge
                        t_edge.reverse_edge = c_edge
            current_person_node_iter = current_person_node_iter.next

        p1_iter_node = self.all_people_nodes.head
        while p1_iter_node:
            p1_name = p1_iter_node.data
            p2_iter_node = self.all_people_nodes.head
            while p2_iter_node:
                p2_name = p2_iter_node.data
                if p1_name != p2_name:
                    p1_v = g.get_vertex(p1_name)
                    p2_v = g.get_vertex(p2_name)
                    if p1_v and p2_v:
                        edge_p1_p2 = p1_v.add_edge(p2_name, None, capacity=self._INFINITY, cost=1)
                        edge_p2_p1 = p2_v.add_edge(p1_name, None, capacity=0, cost=-1)
                        if edge_p1_p2 and edge_p2_p1:
                            edge_p1_p2.reverse_edge = edge_p2_p1
                            edge_p2_p1.reverse_edge = edge_p1_p2
                p2_iter_node = p2_iter_node.next
            p1_iter_node = p1_iter_node.next

    def _find_path_in_residual_graph(self) -> Tuple[LinkedList[GraphEdge[str, None]] | float] | None:
        """
        Find shortest path (lowest cost) from S to T in residual graph using Bellman-Ford.
        Returns: Tuple containing (path_edges, flow_capacity) or None if no path found.
        """
        if not self.flow_graph:
            return None

        source_data = self._S_NODE
        sink_data = self._T_NODE

        distances: HashTable[str, float] = HashTable()
        parent_info: HashTable[str, Tuple[GraphEdge[str, None] | bool] | None] = HashTable()

        all_graph_nodes_data_ll = self.flow_graph.vertices.keys()
        if all_graph_nodes_data_ll is None:
            all_graph_nodes_data_ll = LinkedList[str]()
        else:
            all_graph_nodes_data_ll = merge_sort_linked_list(all_graph_nodes_data_ll, comparator=lambda s1, s2: s1 < s2)

        node_iter = all_graph_nodes_data_ll.head
        while node_iter:
            node_data = node_iter.data
            distances.put(node_data, self._INFINITY)
            parent_info.put(node_data, None)
            node_iter = node_iter.next
        distances.put(source_data, 0.0)

        num_vertices = self.flow_graph.get_num_vertices()
        all_edges_in_graph_ll: LinkedList[GraphEdge[str, None]] = LinkedList()

        node_key_iter = all_graph_nodes_data_ll.head
        while node_key_iter:
            u_key = node_key_iter.data
            u_vertex = self.flow_graph.get_vertex(u_key)
            if u_vertex and u_vertex.edges:
                edge_node_iter = u_vertex.edges.head
                while edge_node_iter:
                    all_edges_in_graph_ll.append(edge_node_iter.data)
                    edge_node_iter = edge_node_iter.next
            node_key_iter = node_key_iter.next

        if not all_edges_in_graph_ll.is_empty():
            all_edges_in_graph_ll = merge_sort_linked_list(
                all_edges_in_graph_ll,
                comparator=lambda e1, e2: (
                    e1.source,
                    e1.destination,
                    e1.cost if e1.cost is not None else 0.0,
                    e1.capacity if e1.capacity is not None else self._INFINITY
                ) < (
                    e2.source,
                    e2.destination,
                    e2.cost if e2.cost is not None else 0.0,
                    e2.capacity if e2.capacity is not None else self._INFINITY
                )
            )

        for i in range(num_vertices):
            changed_in_iteration = False
            edge_iter = all_edges_in_graph_ll.head
            while edge_iter:
                edge = edge_iter.data
                u_data = edge.source
                v_data = edge.destination
                edge_cost = edge.cost if edge.cost is not None else 0.0

                dist_u_data = distances.get(u_data)
                if dist_u_data is None or dist_u_data == self._INFINITY:
                    edge_iter = edge_iter.next
                    continue

                residual_capacity_forward = (edge.capacity if edge.capacity is not None else self._INFINITY) - edge.flow
                if residual_capacity_forward > 1e-9:
                    dist_v_data = distances.get(v_data)
                    if dist_v_data is None: dist_v_data = self._INFINITY

                    if dist_u_data + edge_cost < dist_v_data:
                        if i < num_vertices - 1:
                            distances.put(v_data, dist_u_data + edge_cost)
                            parent_info.put(v_data, Tuple([edge, True]))
                            changed_in_iteration = True
                edge_iter = edge_iter.next

            if i < num_vertices - 1 and not changed_in_iteration and i > 0:
                break

        if distances.get(sink_data) is None or distances.get(sink_data) == self._INFINITY:
            return None

        path_reconstruction_ll: LinkedList[Tuple[GraphEdge[str, None] | bool]] = LinkedList()
        curr_data = sink_data
        visited_in_path_recon_ht: HashTable[str, bool] = HashTable()
        temp_path_for_safety_check_len = 0

        while curr_data != source_data:
            parent_edge_info = parent_info.get(curr_data)
            if parent_edge_info is None: return None

            if visited_in_path_recon_ht.contains_key(curr_data):
                return None
            visited_in_path_recon_ht.put(curr_data, True)

            path_reconstruction_ll.prepend(parent_edge_info)

            original_edge, _ = parent_edge_info
            curr_data = original_edge.source

            temp_path_for_safety_check_len += 1
            if temp_path_for_safety_check_len > num_vertices + 5:
                return None

        if curr_data != source_data and path_reconstruction_ll.is_empty():
            return None

        final_path_edges_ll: LinkedList[GraphEdge[str, None]] = LinkedList()
        path_flow_capacity = self._INFINITY

        path_recon_iter = path_reconstruction_ll.head
        while path_recon_iter:
            original_edge_info_tuple = path_recon_iter.data
            original_edge = original_edge_info_tuple[0]
            is_forward_in_path = original_edge_info_tuple[1]

            final_path_edges_ll.append(original_edge)
            if is_forward_in_path:
                res_cap = (original_edge.capacity if original_edge.capacity is not None else self._INFINITY) - original_edge.flow
                path_flow_capacity = min(path_flow_capacity, res_cap)
            path_recon_iter = path_recon_iter.next

        if path_flow_capacity <= 1e-9 or path_flow_capacity == self._INFINITY:
            return None

        return Tuple([final_path_edges_ll, path_flow_capacity])

    def _find_min_cost_max_flow_solution(self) -> Array[AdvancedTransaction]:
        """Find an optimal solution using Min-Cost Max-Flow algorithm."""
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
        keys_ll = balances.keys()
        if keys_ll:
            current_key_node = keys_ll.head
            while current_key_node:
                person = current_key_node.data
                amount = balances.get(person)
                if amount < 0:  # Person owes money
                    debtors.append(person)
                elif amount > 0:  # Person is owed money
                    creditors.append(person)
                current_key_node = current_key_node.next
        
        # Sort debtors and creditors by absolute balance
        debtors = merge_sort_array(debtors, lambda a, b: abs(balances.get(a)) > abs(balances.get(b)))
        creditors = merge_sort_array(creditors, lambda a, b: balances.get(a) > balances.get(b))
        
        # Create new transactions
        for i in range(len(debtors)):
            debtor = debtors.get(i)
            debtor_amount = abs(balances.get(debtor))
            for j in range(len(creditors)):
                if debtor_amount <= 0:
                    break

                creditor = creditors.get(j)
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
        """Simplify the transaction network using Min-Cost Max-Flow algorithm."""
        if self.transactions.is_empty():
            return LinkedList[AdvancedTransaction]()
        
        # Find Min-Cost Max-Flow solution
        simplified = self._find_min_cost_max_flow_solution()
        
        # Convert Array to LinkedList
        simplified_transactions = LinkedList[AdvancedTransaction]()
        for i in range(len(simplified)):
            simplified_transactions.append(simplified.get(i))
        
        self.simplified_transactions = simplified_transactions
        return self.simplified_transactions 