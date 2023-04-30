import asyncio
import aiomysql
from multicolorcaptcha import CaptchaGenerator
import time
import os
import random

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import DATABASE_FILE, BOT_TOKEN
from handlers.register_start_handlers import register_start_handlers
from database.Classes import pool


async def main(loop):
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # register_admin_handlers(dp)
    register_start_handlers(dp)

    await dp.start_polling()

    pool.close()
    await pool.wait_closed()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
