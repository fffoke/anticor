import os
from aiogram import   F, Router
from aiogram.filters import CommandStart , Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.types import FSInputFile
from web.models import Report, Sos
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

@router.callback_query(F.data=='sos')
async def create_sos(callback: CallbackQuery):
    user = await get_user(callback.message.from_user.id)
    if user:
        await callback.message.answer(text='Отправить сигнал SOS', reply_markup=kb.sos)
    else:
        await callback.message.edit_text(text='У вас не верифецированный аккаунт', reply_markup= kb.main)
        return
@router.message(lambda msg: msg.location)
async def sos(message: Message):
    tg_id = message.from_user.id
    user = await get_user(tg_id)
    if user:
        sos = await sync_to_async(Sos.objects.create)(
            name = user.name,
            iin = user.iin,
            latitude=message.location.latitude,
            longitude=message.location.longitude,
            tg_id = tg_id
        )
        opers = await get_opers()
        for oper in opers:
            await bot.send_message(chat_id=int(oper.tg_id), 
                                   text=
                                   f'''
\t\t\t\t🚨 
<b>Поступил сигнал SOS!</b>
Пользователь отправил экстренное уведомление о происшествии.

👤 <b>Имя:</b> {sos.name}  
🆔 <b>ИИН:</b> {sos.iin}  
💬 <b>Telegram ID:</b> {sos.tg_id}
📍 <b>Местоположение:</b>  
<a href="https://2gis.kz/geo/{sos.latitude},{sos.longitude}">Открыть в 2ГИС</a>
⚠️ <b>Необходима немедленная проверка!</b>  
Пожалуйста, свяжитесь с пользователем и передайте информацию соответствующим службам.
''', parse_mode='HTML', disable_web_page_preview=True)
    else:
        await message.edit_text(text='У вас не верифецированный аккаунт', reply_markup= kb.main)
        return