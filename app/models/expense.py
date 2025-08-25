from datetime import datetime


class Expense:
    def __init__(self, category: str, amount: float, comment: str = ""):
        self.category: str = category
        self.amount: float = amount
        self.date: datetime = datetime.now()
        self.comment: str = comment

    def to_string(self):
        if self.comment != "":
            return f"{self.category} - {self.amount} Р. - {self.comment}"
        else:
            return f"{self.category} - {self.amount} Р."
