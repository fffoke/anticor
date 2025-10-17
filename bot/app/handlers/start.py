from aiogram import   F, Router
from aiogram.filters import CommandStart , Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from app.midelware import CreateReport, GetTgId
from aiogram.fsm.context import FSMContext
from bot.config import bot, dp
import asyncio
from pathlib import Path
from app.api import creat_category
import string
from bot.app.database.models import User , Oper, Admin
from bot.app.database.request import (
    is_admin, add_oper_req, get_opers, is_oper, 
    add_admin, get_tip_req, get_user, add_tip_req,
    check_user, create_tip
)
from aiogram.types import InputFile

router = Router()

welcome_text = (
        "👋 <b>Добро пожаловать в Антикоррупционный Бот!</b>\n\n"
        "📣 Здесь вы можете:\n"
        "• Сообщить о факте коррупции 📝\n"
        "• Получить полезные советы 💡\n"
        "• Пройти верификацию и стать частью честного общества 🪪\n"
        "• В экстренной ситуации вызвать помощь 🚨\n\n"
        "Выберите действие ниже 👇"
    )

# команда старт
@router.message(CommandStart())
async def start(message: Message):
    await message.answer(text=welcome_text, reply_markup= kb.main, parse_mode='HTML')
    await add_admin()
    await create_tip()

# команда старт
@router.callback_query(F.data=='start')
async def start(callback: CallbackQuery):
    await callback.message.edit_text(text=welcome_text, reply_markup= kb.main, parse_mode='HTML')


@router.callback_query(F.data =='about_project')
async def about_project(callback: CallbackQuery):
    text = (
        "🌐 <b>Антикоррупционный Бот</b>\n\n"
        "Этот бот создан для помощи гражданам в борьбе с коррупцией.\n\n"
        "🧭 <b>Вот что вы можете сделать:</b>\n"
        "• 📝 <b>Создать жалобу</b> — сообщите о факте коррупции, приложите фото и геолокацию.\n"
        "• 💡 <b>Получить совет</b> — получите полезные рекомендации о том, как действовать законно.\n"
        "• 🪪 <b>Мои данные</b> — просмотрите или подтвердите свою верификацию.\n"
        "• 🚨 <b>SOS сигнал</b> — быстро отправьте сигнал в экстренной ситуации.\n\n"
        "💙 Мы благодарим вас за активную гражданскую позицию и веру в честное будущее!"
    )
    await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup = kb.back)