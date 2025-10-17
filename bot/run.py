import logging
import os
import sys
import asyncio


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "anti_corruption.settings")

import django
django.setup()

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from bot.app.handlers.__init__ import all_handlers
from aiogram.types import FSInputFile
from bot.config import bot, dp
from bot.app.database.models import asyn_main



async def main():
    for router in all_handlers:
        dp.include_router(router)
    await asyn_main()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())  
    except KeyboardInterrupt:
        print('EXIT')