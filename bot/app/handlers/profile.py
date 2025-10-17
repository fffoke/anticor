import os
from aiogram import   F, Router
from aiogram.filters import CommandStart , Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.types import FSInputFile
from web.models import Report
from asgiref.sync import sync_to_async
from app.midelware import Verify
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
    check_user, create_user
)
from aiogram.types import InputFile

router = Router()


@router.callback_query(F.data == 'my_profile')
async def my_profile(callback: CallbackQuery):
    tg_id = callback.message.from_user.id
    user = await get_user(tg_id=tg_id)
    if user:
        text = (
            f"🪪 <b>Ваш профиль</b>\n\n"
            f"👤 Имя: {user.name}\n"
            f"🆔 ИИН: {user.iin}\n"
            f"💬 Telegram ID: {user.tg_id}\n\n"
            f"✅ Статус: Верифицирован"
            )
        await callback.message.edit_text(text=text, reply_markup= kb.main, parse_mode='HTML')
        return
    else:
        text = (
            "❌ <b>Вы еще не верифицированы!</b>\n\n"
            "Для прохождения верификации отправьте свои данные.\n"
            "Поля:\n- Имя\n- ИИН"
        )
        await callback.message.edit_text(text=text, reply_markup= kb.verify, parse_mode='HTML')
        return


@router.callback_query(F.data == 'verify')
async def verify(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Verify.iin)
    sent_msg = await callback.message.edit_text(
        text= 'Введите ваш ИИН'
    )
    await state.update_data(bot_message_id=sent_msg.message_id)
    await callback.answer()


@router.message(Verify.iin)
async def get_iin(message: Message, state: FSMContext):
    iin = message.text.strip()

    if not iin.isdigit():
        await message.answer("Введите валидный ИИН!", reply_markup=kb.verify)
        return
    
    if len(str(iin)) == 12:
        await state.update_data(iin=iin)
        await state.set_state(Verify.name)
        data = await state.get_data()
        await message.delete()
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data['bot_message_id'],  # предыдущее сообщение бота
            text="Введите ваше Имя: ",
        )   
    else:
        print(len(str(iin)))
        await message.answer(text='⚠️ ИИН должен содержать ровно 12 цифр!', reply_markup= kb.verify)
        return

@router.message(Verify.name)
async def reg_user(message: Message, state: FSMContext):
    data = await state.get_data()
    iin = data['iin']
    tg_id = message.from_user.id
    name = message.text
    user = await create_user(tg_id=tg_id, name=name, iin=iin)
    await message.delete()
    await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data['bot_message_id'],  
            text="Вы успешно верифецировались!",
            reply_markup=kb.verify
        )
