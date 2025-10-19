import os
import django
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
from asgiref.sync import sync_to_async
from django.conf import settings

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anti_corruption.settings')
django.setup()



BASE_DIR = Path(__file__).resolve().parent.parent.parent
router = Router()

#                       Создания репорта
# 1 шаг создания репорта
@router.callback_query(F.data == 'create_report')
async def create_report(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReport.title)
    sent_msg = await callback.message.edit_text("Введите заголовок жалобы:")
    await state.update_data(bot_message_id=sent_msg.message_id)

    await callback.answer()

# 2 шаг получения загаловка
@router.message(CreateReport.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.delete()  
    await state.set_state(CreateReport.text)
    data = await state.get_data()

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data['bot_message_id'],  
        text="Опишите жалобу подробно:",
    )   

# обработка текста
@router.message(CreateReport.text)
async def get_title(message: Message , state: FSMContext):
    await state.update_data(text=message.text)
    await message.delete()
    await state.set_state(CreateReport.image)
    data = await state.get_data()
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data['bot_message_id'],  
        text="Отправьте изоброжения жалобы или нажмите пропустить:",
        reply_markup=kb.skip
    )   

# обработак фотки (пропустить)
@router.callback_query(CreateReport.image, F.data == "skip")
async def skip_image(callback: CallbackQuery, state: FSMContext):
    await state.update_data(image=None)
    await state.set_state(CreateReport.location)
    data = await state.get_data()
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=data['bot_message_id'],
        text="📍 Отправьте местоположение происшествия.", 
    )

# обработка фотки
@router.message(CreateReport.image, F.photo)
async def get_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)

    
    images_dir = Path(settings.MEDIA_ROOT) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    
    saved_path = images_dir / f"{photo.file_unique_id}.jpg"
    await bot.download_file(file_info.file_path, saved_path)

    relative_path = f"images/{photo.file_unique_id}.jpg"

    data = await state.get_data()
    await state.update_data(image=relative_path)  

    await message.delete()
    await state.set_state(CreateReport.location)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data['bot_message_id'],
        text="📍 Отправьте местоположение происшествия.",
    )







# Создаем обьект класса Report из Django ORM
@router.message(CreateReport.location, F.location)
async def get_location(message: Message, state: FSMContext):
    data = await state.get_data()
    image_path = data.get("image")

    
    if image_path and os.path.exists(Path(settings.MEDIA_ROOT) / image_path):
        category = await asyncio.to_thread(creat_category, image_path, data["text"], data["title"])
    else:
        category = await asyncio.to_thread(creat_category, None, data["text"], data["title"])

    
    report = await sync_to_async(Report.objects.create)(
        category=category.replace('*', ''),
        title=data['title'],
        text=data['text'],
        image=image_path,  
        latitude=message.location.latitude,
        longitude=message.location.longitude,
        is_decided=False
    )

    await message.delete()
    await state.clear()

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data['bot_message_id'],
        text="✅ Жалоба успешно сохранена!\nСпасибо за ваш вклад 💙",
        reply_markup=kb.main
    )

    # уведомляем операторов
    opers = await get_opers()

    photo_path = None
    if image_path:
        photo_path = Path(settings.MEDIA_ROOT) / image_path

    for oper in opers:
        try:
            caption = f"""
⚠️ Поступила новая *важная жалоба*.

📝 **Заголовок:** {report.title}

📄 **Описание:** {report.text[:200]}{'...' if len(report.text) > 200 else ''}

📍 **Местоположение:** https://2gis.kz/geo/{report.latitude},{report.longitude}

Пожалуйста, ознакомьтесь с жалобой и примите необходимые меры.
"""

            if report.category == 'CRITICAL' and photo_path and photo_path.exists():
                photo = FSInputFile(photo_path)
                await bot.send_photo(
                    int(oper.tg_id),
                    photo=photo,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(int(oper.tg_id), text=caption, parse_mode="Markdown")

        except Exception as e:
            print(f"Ошибка отправки оператору {oper.tg_id}: {e}")
                             

        

