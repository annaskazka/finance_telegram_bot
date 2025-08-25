from fastapi import FastAPI, Request
from aiogram import Bot, types
from app.storage.user_manager import UserManager
from app.handlers.menu_handler import MenuHandler
from app.models.user_state import UserState
from dotenv import load_dotenv
import os
from aiogram.exceptions import TelegramBadRequest


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN не задан в .env")

bot = Bot(token=API_TOKEN)
app = FastAPI()
user_manager = UserManager()
menu_handler = MenuHandler(user_manager)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    update = types.Update(**update_data)

    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        return {"ok": False, "error": "Нет message или callback_query"}

    user = user_manager.get_user(user_id)

    if update.message:
        if user.state == UserState.IDLE:
            text, keyboard = menu_handler.handle_command(user_id, update.message.text)
            await bot.send_message(user_id, text, reply_markup=keyboard)

        elif user.state == UserState.ENTERING_AMOUNT:
            try:
                amount = float(update.message.text.replace(",", "."))
                user.selected_amount = amount
                user.state = UserState.ENTERING_COMMENT
                await bot.send_message(
                    user_id,
                    "Сумма сохранена. Введи комментарий к расходу (или оставь пустым).",
                )
            except ValueError:
                await bot.send_message(
                    user_id, "Пожалуйста, введи корректное число, например: 199.99"
                )

        elif user.state == UserState.ENTERING_COMMENT:
            comment = update.message.text or ""
            user.add_expense(user.selected_category, user.selected_amount, comment)

            user.selected_category = None
            user.selected_amount = None
            user.state = UserState.IDLE
            await bot.send_message(
                user_id, "Расход добавлен ✅", reply_markup=menu_handler.get_main_menu()
            )

    elif update.callback_query and update.callback_query.message:
        callback = update.callback_query

        try:
            await bot.answer_callback_query(callback.id)
        except TelegramBadRequest as e:
            if "query is too old" not in str(e):
                raise

        text, keyboard = menu_handler.handle_callback(user_id, callback.data)

        if text:
            try:
                await bot.edit_message_text(
                    text=text,
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    reply_markup=keyboard,
                )
            except Exception:
                await bot.send_message(
                    callback.message.chat.id, text, reply_markup=keyboard
                )

        return {"ok": True}
