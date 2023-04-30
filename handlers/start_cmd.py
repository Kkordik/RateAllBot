from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import DATABASE_FILE, BOT_TOKEN, LANGUAGES, LANGUAGES2
from texts import text
from database.Classes import *
from keyboards import start_keyboard

bot = Bot(token=BOT_TOKEN)


async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    userdb = UserDb(user_id)
    await userdb.search_add_user()

    keyboard = start_keyboard(userdb)
    print("ok", userdb.lang)
    await bot.send_message(chat_id, text=text[userdb.lang]["start_message"], parse_mode="HTML", reply_markup=keyboard,
                           disable_web_page_preview=True)


async def edit_language(message: types.Message):
    chat_id = message.chat.id

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for lang in LANGUAGES:
        keyboard.add(types.KeyboardButton(LANGUAGES[lang]))

    await bot.send_message(chat_id, text["choose_lang"], reply_markup=keyboard)


async def choose_language(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.text

    userdb = UserDb(user_id)
    await userdb.search_add_user()
    await userdb.insert_language(LANGUAGES2[lang])

    keyboard = start_keyboard(userdb)
    await bot.send_message(chat_id, text=text[userdb.lang]["start_message"], parse_mode="HTML", reply_markup=keyboard,
                           disable_web_page_preview=True)


def register_start_cmd_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(choose_language, lambda message: message.text in LANGUAGES2)
    dp.register_message_handler(edit_language, lambda message: message.text in [text["ru"]["edit_lang"],
                                                                                text["en"]["edit_lang"],
                                                                                text["uk"]["edit_lang"]])