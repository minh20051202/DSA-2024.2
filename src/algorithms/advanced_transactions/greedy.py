from __future__ import annotations
from datetime import date
from typing import Any

from src.core_type import BasicTransaction, AdvancedTransaction
from src.data_structures import LinkedList, HashTable, Tuple
from src.utils.sorting import merge_sort_linked_list
from src.utils.constants import EPSILON
from src.utils.money_utils import round_money

class AdvancedGreedySimplifier:
    """
    Đơn giản hóa nợ nâng cao với các yếu tố tài chính (thời gian, lãi suất, phí phạt).
    """

    def __init__(self, 
                 transactions: LinkedList[AdvancedTransaction],
                 current_date: date):
        self.initial_transactions = transactions
        self.current_date = current_date
        self.people_balances = HashTable[str, float]()
        self.transaction_details = LinkedList[Tuple]()
        self._calculate_balances()

    def _calculate_balances(self) -> None:
        current = self.initial_transactions.head
        while current:
            tx: AdvancedTransaction = current.data
            breakdown = tx.get_debt_breakdown(self.current_date)
            actual_debt = breakdown['total']

            detail = Tuple([
                tx.debtor, 
                tx.creditor,
                breakdown['principal'],
                breakdown['interest'],
                breakdown['penalty'],
                actual_debt,
                tx.get_priority_score(self.current_date),
                tx.is_overdue(self.current_date)
            ])
            self.transaction_details.append(detail)

            self._update_balance(tx.debtor, -actual_debt)
            self._update_balance(tx.creditor, actual_debt)

            current = current.next

    def _update_balance(self, person: str, amount: float) -> None:
        current_balance = self.people_balances.get(person, 0.0)
        new_balance = round_money(current_balance + amount)
        self.people_balances.put(person, new_balance)

    def simplify(self) -> LinkedList[BasicTransaction]:
        if self.initial_transactions.is_empty():
            return LinkedList()

        debtors = LinkedList[Tuple]()
        creditors = LinkedList[Tuple]()

        for person in self.people_balances.keys():
            balance = self.people_balances.get(person)
            if balance < -EPSILON:
                debtors.append(Tuple([person, balance]))
            elif balance > EPSILON:
                creditors.append(Tuple([person, balance]))

        debtors = merge_sort_linked_list(debtors, lambda t1, t2: t1[1] < t2[1])
        creditors = merge_sort_linked_list(creditors, lambda t1, t2: t1[1] > t2[1])

        simplified_txs = LinkedList[BasicTransaction]()
        debtor_node, creditor_node = debtors.head, creditors.head

        while debtor_node and creditor_node:
            debtor_name, debtor_balance = debtor_node.data
            creditor_name, creditor_balance = creditor_node.data
            settle_amount = min(-debtor_balance, creditor_balance)

            if settle_amount > EPSILON:
                simplified_txs.append(
                    BasicTransaction(debtor=debtor_name, creditor=creditor_name, amount=settle_amount)
                )
                debtor_balance += settle_amount
                creditor_balance -= settle_amount
                debtor_node.data = Tuple([debtor_name, debtor_balance])
                creditor_node.data = Tuple([creditor_name, creditor_balance])

            if abs(debtor_balance) < EPSILON:
                debtor_node = debtor_node.next
            if abs(creditor_balance) < EPSILON:
                creditor_node = creditor_node.next

        return simplified_txs
