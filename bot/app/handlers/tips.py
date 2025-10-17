import os
from aiogram import   F, Router
from aiogram.filters import CommandStart , Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.types import FSInputFile
from web.models import Report
from asgiref.sync import sync_to_async
from app.midelware import AddTip
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

router = Router()


# получить совет 
@router.callback_query(F.data == 'get_tip')
async def get_tip(callback: CallbackQuery):
    tip = await get_tip_req()
    msg = ''.join(tip)
    await callback.message.edit_text(text=tip, reply_markup = kb.main)

# Начало добовления совета
@router.message(Command('add_tip'))
async def add_tip(message: Message, state:  FSMContext):
    if await is_oper(message.from_user.id):
        await message.answer(text='Напишите совет который хотите добавить: ')
        await state.set_state(AddTip.tip)
    else:
        await message.answer(text='У вас нет прав для этой команды.')


@router.message(AddTip.tip)
async def get_tip_text(message: Message, state:  FSMContext):
    tip = message.text
    await add_tip_req(tip=tip)
    await message.answer(f"✅ Совет с описанием \n'{tip}'\nуспешно добавлен")
    await state.clear()

    