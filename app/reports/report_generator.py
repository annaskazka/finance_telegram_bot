from .period_type import PeriodType
from datetime import datetime


class ReportGenerator:
    def generate_report(self, user, period_type, day=None, month=None, year=None):

        today = datetime.today()
        if day is None:
            day = today.day
        if month is None:
            month = today.month
        if year is None:
            year = today.year

        expenses = self.filter_expenses(
            user, period_type, day=day, month=month, year=year
        )
        sums_dict = self.sum_by_category(expenses)
        return self.format_report(sums_dict, period_type, day, month, year)

    def filter_expenses(self, user, period_type, day=None, month=None, year=None):
        filtered = []
        for exp in user.get_expenses():
            if period_type == PeriodType.DAY and day and month and year:
                if (
                    exp.date.day == day
                    and exp.date.month == month
                    and exp.date.year == year
                ):
                    filtered.append(exp)
            elif period_type == PeriodType.MONTH and month and year:
                if exp.date.month == month and exp.date.year == year:
                    filtered.append(exp)
            elif period_type == PeriodType.YEAR and year:
                if exp.date.year == year:
                    filtered.append(exp)
        return filtered

    def sum_by_category(self, expenses):
        sums = {}
        for exp in expenses:
            sums[exp.category] = sums.get(exp.category, 0) + exp.amount
        return sums

    def format_report(self, sums_dict, period_type, day=None, month=None, year=None):
        if period_type == PeriodType.DAY:
            header = f"Расходы за {day:02}.{month:02}.{year}"
        elif period_type == PeriodType.MONTH:
            months = {
                1: "январь",
                2: "февраль",
                3: "март",
                4: "апрель",
                5: "май",
                6: "июнь",
                7: "июль",
                8: "август",
                9: "сентябрь",
                10: "октябрь",
                11: "ноябрь",
                12: "декабрь",
            }
            header = f"Расходы за {months.get(month, 'неизвестно')} {year}"
        elif period_type == PeriodType.YEAR:
            header = f"Расходы за {year}"
        else:
            header = "Расходы"

        if not sums_dict:
            return header + "\nНет расходов за выбранный период."

        lines = [f"{cat}: {amount} ₽" for cat, amount in sums_dict.items()]
        total = sum(sums_dict.values())
        lines.append(f"Итого: {total} ₽")
        report_text = header + "\n" + "\n".join(lines)
        return report_text
