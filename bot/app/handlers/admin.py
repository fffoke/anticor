import os
from aiogram import   F, Router
from aiogram.filters import CommandStart , Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.types import FSInputFile
from web.models import Report
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
    check_user
)
from aiogram.types import InputFile
import config as c

router = Router()


@router.message(Command('staff_help'))
async def add_oper_step_1(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if await is_admin(tg_id=tg_id) or await is_oper(tg_id=tg_id):
        await message.answer(text=c.HELP_TEXT, parse_mode='HTML')


# Добавить опера
@router.message(Command('add_oper'))
async def add_oper_step_1(message: Message, state: FSMContext):
    if await is_admin(message.from_user.id):
        await state.set_state(GetTgId.tg_id)
        await message.answer(text='''
Здравствуйте.
Для добавления нового оператора в систему введите его Telegram ID.
Если вы не знаете, как узнать  Telegram ID, воспользуйтесь этим ботом: @MyTidBot
 — он покажет идентификатор.
''')
    else:
        await message.answer("У вас нет прав для этой команды.")


@router.message(GetTgId.tg_id)
async def add_oper_step_2(message: Message, state: FSMContext):
    try:
        tg_id = message.text
    except ValueError:
        await message.answer("Пожалуйста, введите корректный числовой Telegram ID.")
        return
    
    await add_oper_req(tg_id=tg_id) 
    await message.answer(f"✅ Оператор с ID {tg_id} успешно добавлен.")
    await state.clear()
