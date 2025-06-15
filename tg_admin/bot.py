import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
from dotenv import load_dotenv
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from functools import wraps

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

# --- Авторизация ---
authorized_users = set()

class AuthStates(StatesGroup):
    waiting_for_key = State()

# Проверка авторизации
async def check_auth(message: Message):
    if message.from_user.id not in authorized_users:
        await message.answer("Введите admin_key для доступа:")
        return False
    return True

# /start с авторизацией
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if message.from_user.id in authorized_users:
        await message.answer(
            "Добро пожаловать в админ-панель!\nВыберите действие:",
            reply_markup=main_menu
        )
    else:
        await message.answer("Введите admin_key для доступа:")
        await state.set_state(AuthStates.waiting_for_key)

# Обработка ввода admin_key
@dp.message(AuthStates.waiting_for_key)
async def process_admin_key(message: Message, state: FSMContext):
    if message.text.strip() == ADMIN_KEY:
        authorized_users.add(message.from_user.id)
        await message.answer("Успешная авторизация!", reply_markup=main_menu)
        await state.clear()
    else:
        await message.answer("Неверный ключ. Попробуйте снова:")

# Декоратор для авторизации
def require_auth(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in authorized_users:
            await message.answer("Сначала авторизуйтесь через /start")
            return
        return await handler(message, *args, **kwargs)
    return wrapper


def require_auth_callback(handler):
    @wraps(handler)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if callback.from_user.id not in authorized_users:
            await callback.message.answer("Сначала авторизуйтесь через /start")
            await callback.answer()
            return
        return await handler(callback, *args, **kwargs)
    return wrapper

@dp.callback_query(lambda c: c.data == "show_sessions")
@require_auth_callback
async def cb_show_sessions(callback: CallbackQuery):
    await get_sessions_impl(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_times")
@require_auth_callback
async def cb_show_times(callback: CallbackQuery):
    await get_times_impl(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "delete_session_menu")
@require_auth_callback
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

# --- Получить все сессии ---
async def get_sessions_impl(message: Message):
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

@dp.message(Command("sessions"))
@require_auth
async def get_sessions(message: Message):
    await get_sessions_impl(message)

# --- Получить время до конца сессий ---
async def get_times_impl(message: Message):
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

@dp.message(Command("times"))
@require_auth
async def get_times(message: Message):
    await get_times_impl(message)

# Удалить сессию по id
@dp.message(Command("delete_session"))
@require_auth
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
@require_auth_callback
async def process_delete_session_callback(callback: CallbackQuery):
    session_id = callback.data.split(":", 1)[1]
    await delete_session_by_id(callback, session_id)
    await callback.answer("Сессия удалена", show_alert=False)

async def delete_session_by_id(source, session_id):
    # source: Message или CallbackQuery
    if isinstance(source, CallbackQuery):
        user_id = source.from_user.id
        send = source.message.answer
    else:
        user_id = source.from_user.id
        send = source.answer
    if user_id not in authorized_users:
        await send("Сначала авторизуйтесь через /start")
        return
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_URL}/root/close", headers={"Master-Key": ADMIN_KEY}, params={"session_id": session_id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                text = data.get("message", "Удалено")
                if not text.strip():
                    text = "Нет ответа от сервера."
                await send(text)
            else:
                await send(f"Ошибка: {resp.status}")
    await send_main_menu(source.message if isinstance(source, CallbackQuery) else source)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import asyncio
    asyncio.run(dp.start_polling(bot))
