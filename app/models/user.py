from typing import List
from .expense import Expense
from .user_state import UserState


class User:
    def __init__(self, user_id: int):
        self.user_id: int = user_id
        self.expenses: List[Expense] = []
        self.state: UserState = UserState.IDLE
        self.selected_category = None
        self.selected_amount = None

    def add_expense(self, category, amount, comment):
        expense = Expense(category, amount, comment)
        self.expenses.append(expense)

    def get_expenses(self):
        return self.expenses
