import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()  # загружаем переменные из .env
TG_TOKEN = os.getenv("TG_TOKEN")

API_URL = "http://127.0.0.1:8000"  # адрес FastAPI
ADMIN_KEY = os.getenv("ADMIN_KEY")

print(TG_TOKEN)
bot = Bot(token=TG_TOKEN)

dp = Dispatcher()

# Главное меню с кнопками
main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Все сессии", callback_data="show_sessions"),
            InlineKeyboardButton(text="Время до конца", callback_data="show_times")
        ],
        [
            InlineKeyboardButton(text="Удалить сессию", callback_data="delete_session_menu")
        ]
    ]
)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в админ-панель!\nВыберите действие:",
        reply_markup=main_menu
    )

@dp.callback_query(lambda c: c.data == "show_sessions")
async def cb_show_sessions(callback: CallbackQuery):
    await get_sessions(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_times")
async def cb_show_times(callback: CallbackQuery):
    await get_times(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "delete_session_menu")
async def cb_delete_session_menu(callback: CallbackQuery):
    # Показываем меню удаления сессии (тот же код, что и в /delete_session)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/root/session", headers={"Master-Key": ADMIN_KEY}) as resp:
            if resp.status == 200:
                data = await resp.json()
                if not data:
                    await callback.message.answer("Нет активных сессий.", reply_markup=main_menu)
                    await callback.answer()
                    return
                kb = []
                for session_id, info in data.items():
                    model = info.get("model", {})
                    items = model.get("data", [])
                    responsible = "-"
                    if items and isinstance(items[0], dict):
                        responsible = items[0].get("PC", {}).get("Responsible", "-")
                    btn_text = f"{session_id[:6]}... ({responsible})"
                    kb.append([InlineKeyboardButton(text=btn_text, callback_data=f"delete_session:{session_id}")])
                markup = InlineKeyboardMarkup(inline_keyboard=kb)
                await callback.message.answer("Выберите сессию для удаления:", reply_markup=markup)
            else:
                await callback.message.answer(f"Ошибка: {resp.status}", reply_markup=main_menu)
    await callback.answer()

# После каждой команды выводим главное меню
async def send_main_menu(message):
    await message.answer("Выберите действие:", reply_markup=main_menu)
# Получить все сессии
@dp.message(Command("sessions"))
async def get_sessions(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/root/session", headers={"Master-Key": ADMIN_KEY}) as resp:
            if resp.status == 200:
                data = await resp.json()
                if not data:
                    await message.answer("Нет активных сессий.")
                    await send_main_menu(message)
                    return
                lines = []
                for session_id, info in data.items():
                    last_activity = info.get("last_activity", "нет данных")
                    model = info.get("model", {})
                    items = model.get("data", [])
                    count = len(items)
                    responsible = "-"
                    if count > 0 and isinstance(items[0], dict):
                        responsible = items[0].get("PC", {}).get("Responsible", "-")
                    lines.append(
                        f"ID: <code>{session_id}</code>\n"
                        f"Последняя активность: <b>{last_activity}</b>\n"
                        f"Объектов: <b>{count}</b>\n"
                        f"Ответственный: <i>{responsible}</i>\n"
                        "----------------------"
                    )
                await message.answer("\n".join(lines), parse_mode="HTML")
            else:
                await message.answer(f"Ошибка: {resp.status}")
    await send_main_menu(message)

# Получить время до конца сессий
@dp.message(Command("times"))
async def get_times(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/root/time", headers={"Master-Key": ADMIN_KEY}) as resp:
            if resp.status == 200:
                data = await resp.json()
                if not data or not any(data):
                    await message.answer("Нет активных сессий.")
                    await send_main_menu(message)
                    return

                lines = []
                for line in data:
                    try:
                        prefix, time_str = line.rsplit(" осталось ", 1)
                        session_id = prefix.split()[-1]
                        t = time_str.split(".")[0]
                        h, m, s = map(int, t.split(":"))
                        if h:
                            t_fmt = f"{h} ч {m} мин {s} сек"
                        elif m:
                            t_fmt = f"{m} мин {s} сек"
                        else:
                            t_fmt = f"{s} сек"
                        lines.append(
                            f"ID: <code>{session_id}</code>\n"
                            f"До конца: <b>{t_fmt}</b>\n"
                            "----------------------"
                        )
                    except Exception:
                        lines.append(line)
                await message.answer("\n".join(lines), parse_mode="HTML")
            else:
                await message.answer(f"Ошибка: {resp.status}")
    await send_main_menu(message)

# Удалить сессию по id
@dp.message(Command("delete_session"))
async def delete_session(message: Message):
    parts = message.text.split()
    if len(parts) == 1:
        # Показываем список сессий с кнопками
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/root/session", headers={"Master-Key": ADMIN_KEY}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not data:
                        await message.answer("Нет активных сессий.")
                        await send_main_menu(message)
                        return
                    kb = []
                    for session_id, info in data.items():
                        model = info.get("model", {})
                        items = model.get("data", [])
                        responsible = "-"
                        if items and isinstance(items[0], dict):
                            responsible = items[0].get("PC", {}).get("Responsible", "-")
                        btn_text = f"{session_id[:6]}... ({responsible})"
                        kb.append([InlineKeyboardButton(text=btn_text, callback_data=f"delete_session:{session_id}")])
                    markup = InlineKeyboardMarkup(inline_keyboard=kb)
                    await message.answer("Выберите сессию для удаления:", reply_markup=markup)
                else:
                    await message.answer(f"Ошибка: {resp.status}")
        return
    if len(parts) != 2:
        await message.answer("Формат: /delete_session <id>")
        return
    session_id = parts[1].strip("<>")
    await delete_session_by_id(message, session_id)

@dp.callback_query(lambda c: c.data and c.data.startswith("delete_session:"))
async def process_delete_session_callback(callback: CallbackQuery):
    session_id = callback.data.split(":", 1)[1]
    await delete_session_by_id(callback.message, session_id)
    await callback.answer("Сессия удалена", show_alert=False)

async def delete_session_by_id(message, session_id):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_URL}/root/close", headers={"Master-Key": ADMIN_KEY}, params={"session_id": session_id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                text = data.get("message", "Удалено")
                if not text.strip():
                    text = "Нет ответа от сервера."
                await message.answer(text)
            else:
                await message.answer(f"Ошибка: {resp.status}")
    await send_main_menu(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio
    asyncio.run(dp.start_polling(bot))
