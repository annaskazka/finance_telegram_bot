from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.user_state import UserState
from app.reports.period_type import PeriodType
from app.reports.report_generator import ReportGenerator


class MenuHandler:
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.report_generator = ReportGenerator()
        self.user_selection = {}
        self.report_mode = {}

    def get_main_menu(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Добавить расход", callback_data="add_expense"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Посмотреть отчёт", callback_data="show_report"
                    )
                ],
            ]
        )

    def get_category_menu(self):
        categories = ["Продукты", "Транспорт", "Здоровье", "Досуг", "Другое"]
        inline_keyboard = [
            [InlineKeyboardButton(text=cat, callback_data=f"cat_{cat.lower()}")]
            for cat in categories
        ]
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        )
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    def get_report_menu(self):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📅 День", callback_data="report_day")],
                [InlineKeyboardButton(text="📆 Месяц", callback_data="report_month")],
                [InlineKeyboardButton(text="🗓️ Год", callback_data="report_year")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
            ]
        )

    def create_calendar(self):
        buttons = [
            InlineKeyboardButton(text=str(i), callback_data=f"day:{i}")
            for i in range(1, 32)
        ]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[buttons[i : i + 7] for i in range(0, 31, 7)]
        )
        return keyboard

    def create_month_keyboard(self) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text=str(i), callback_data=f"month:{i}")
            for i in range(1, 13)  # 12 месяцев
        ]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[buttons[i : i + 4] for i in range(0, len(buttons), 4)]
        )
        return keyboard

    def create_year_keyboard(
        self, start: int = 2020, end: int = 2025
    ) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text=str(y), callback_data=f"year:{y}")
            for y in range(start, end + 1)
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        return keyboard

    def handle_command(self, user_id: int, command: str):
        user = self.user_manager.get_user(user_id)
        if command == "/start":
            user.state = UserState.IDLE
            return (
                "Привет! Я твой финансовый ассистент 💰. Выбери действие:",
                self.get_main_menu(),
            )

        return ("Неизвестная команда. Используй кнопки ниже.", self.get_main_menu())

    def handle_callback(self, user_id: int, callback_data: str):
        user = self.user_manager.get_user(user_id)

        if user_id not in self.user_selection:
            self.user_selection[user_id] = {"day": None, "month": None, "year": None}

        if callback_data == "back_to_main":
            user.state = UserState.IDLE
            return ("Выбери действие:", self.get_main_menu())

        if callback_data == "add_expense":
            user.state = UserState.CHOOSING_CATEGORY
            return ("Выбери категорию расхода:", self.get_category_menu())

        if callback_data.startswith("cat_"):
            category = callback_data.split("cat_", 1)[1]
            user.selected_category = category.capitalize()
            user.state = UserState.ENTERING_AMOUNT
            return (
                f"Категория: {user.selected_category}\nВведи сумму расхода (например, 199.99):",
                None,
            )

        if callback_data == "show_report":

            self.user_selection[user_id] = {"day": None, "month": None, "year": None}
            self.report_mode[user_id] = None
            return ("Выбери период отчёта:", self.get_report_menu())

        if callback_data == "report_day":
            self.report_mode[user_id] = PeriodType.DAY
            self.user_selection[user_id] = {"day": None, "month": None, "year": None}
            return ("Выбери день:", self.create_calendar())

        if callback_data == "report_month":
            self.report_mode[user_id] = PeriodType.MONTH
            self.user_selection[user_id] = {"day": None, "month": None, "year": None}
            return ("Выбери месяц:", self.create_month_keyboard())

        if callback_data == "report_year":
            self.report_mode[user_id] = PeriodType.YEAR
            self.user_selection[user_id] = {"day": None, "month": None, "year": None}
            return ("Выбери год:", self.create_year_keyboard())

        if callback_data == "report_back":

            return ("Выбери период отчёта:", self.get_report_menu())

        if callback_data.startswith("day:"):
            day = int(callback_data.split(":")[1])
            self.user_selection[user_id]["day"] = day

            return (
                f"День {day} выбран. Теперь выбери месяц:",
                self.create_month_keyboard(),
            )

        if callback_data.startswith("month:"):
            month = int(callback_data.split(":")[1])
            self.user_selection[user_id]["month"] = month
            mode = self.report_mode.get(user_id)
            if mode == PeriodType.MONTH:

                return (
                    f"Месяц {month} выбран. Теперь выбери год:",
                    self.create_year_keyboard(),
                )
            elif mode == PeriodType.DAY:

                return (
                    f"Месяц {month} выбран. Теперь выбери год:",
                    self.create_year_keyboard(),
                )
            else:

                return ("Сначала выбери тип отчёта:", self.get_report_menu())

        if callback_data.startswith("year:"):
            year = int(callback_data.split(":")[1])
            self.user_selection[user_id]["year"] = year

            sel = self.user_selection[user_id]
            mode = self.report_mode.get(user_id)

            if mode == PeriodType.DAY:
                if None in (sel["day"], sel["month"], sel["year"]):
                    return ("Ошибка: выбери день, месяц и год.", None)
                report_text = self.report_generator.generate_report(
                    user=user,
                    period_type=PeriodType.DAY,
                    day=sel["day"],
                    month=sel["month"],
                    year=sel["year"],
                )
            elif mode == PeriodType.MONTH:
                if None in (sel["month"], sel["year"]):
                    return ("Ошибка: выбери месяц и год.", None)
                report_text = self.report_generator.generate_report(
                    user=user,
                    period_type=PeriodType.MONTH,
                    month=sel["month"],
                    year=sel["year"],
                )
            elif mode == PeriodType.YEAR:
                if sel["year"] is None:
                    return ("Ошибка: выбери год.", None)
                report_text = self.report_generator.generate_report(
                    user=user, period_type=PeriodType.YEAR, year=sel["year"]
                )
            else:
                return ("Сначала выбери тип отчёта.", self.get_report_menu())

            return (report_text, self.get_main_menu())

        return ("Неизвестная команда.", self.get_main_menu())
