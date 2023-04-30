import pyrogram
from pyrogram import Client

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import DATABASE_FILE, BOT_TOKEN, FAKE_RATES, api_hash, api_id
from texts import text
from database.Classes import *
from keyboards import rate_keyboard

bot = Bot(token=BOT_TOKEN)


async def forward_user(message: types.Message):
    print("forward_user")
    chat_id = message.chat.id
    user_id = message.from_user.id

    userdb = UserDb(user_id)
    await userdb.search_add_user()
    sended_message = await bot.send_message(chat_id, text[userdb.lang]["wait"])

    user = message.forward_from
    object_id = user.id
    mention = user.username
    if mention is None:
        mention = user.first_name
        username = mention
    else:
        username = "@{}".format(mention)
    if user.is_bot:
        obj_type = "bot"
    else:
        obj_type = "user"

    objectdb = ObjectDb(object_id, obj_type)
    await objectdb.search_add_obj()

    # fake rates
    if FAKE_RATES and objectdb.new_obj:
        await objectdb.create_fake_rates()

    # getting rate
    rates_numb, rate, user_left_rate = await objectdb.get_rate(user_id)

    if rate[0] is not None:
        rate = round(float(rate[0]), 2)
    else:
        rate = 0
    keyboard = rate_keyboard(objectdb.objectid, mention)
    print(user_id, "  looking for rate", chat_id, " - chat_id")
    if user_left_rate is not None:
        await bot.edit_message_text(text[userdb.lang]["rate"].format("{}".format(username), rate,
                                                                     user_left_rate[0], rates_numb[0]), sended_message.chat.id,
                                    sended_message.message_id, reply_markup=keyboard, parse_mode="html")
    else:
        await bot.edit_message_text(text[userdb.lang]["rate_not_full"].format("{}".format(username), rate, rates_numb[0]),
                                    sended_message.chat.id,
                                    sended_message.message_id, reply_markup=keyboard, parse_mode="html")


async def forward_group(message: types.Message):
    print("forward_group")
    chat_id = message.chat.id
    user_id = message.from_user.id

    userdb = UserDb(user_id)
    await userdb.search_add_user()
    sended_message = await bot.send_message(chat_id, text[userdb.lang]["wait"])

    chat = message.forward_from_chat
    object_id = chat.id
    mention = chat.username
    if mention is None:
        mention = chat.title
        username = mention
    else:
        username = "@{}".format(mention)
    if chat.type == "group":
        obj_type = "group"
    elif chat.type == "supergroup":
        obj_type = "supergroup"
    else:
        obj_type = "channel"

    objectdb = ObjectDb(object_id, obj_type)
    await objectdb.search_add_obj()

    # fake rates
    if FAKE_RATES and objectdb.new_obj:
        await objectdb.create_fake_rates()

    # getting rate
    rates_numb, rate, user_left_rate = await objectdb.get_rate(user_id)

    if rate[0] is not None:
        rate = round(float(rate[0]), 2)
    else:
        rate = 0
    keyboard = rate_keyboard(objectdb.objectid, username)
    print(user_id, "  looking for rate", chat_id, " - chat_id")
    if user_left_rate is not None:
        await bot.edit_message_text(text[userdb.lang]["rate"].format("{}".format(username), rate,
                                                                     user_left_rate[0], rates_numb[0]), sended_message.chat.id,
                                    sended_message.message_id, reply_markup=keyboard, parse_mode="html")
    else:
        await bot.edit_message_text(text[userdb.lang]["rate_not_full"].format("{}".format(username), rate, rates_numb[0]),
                                    sended_message.chat.id,
                                    sended_message.message_id, reply_markup=keyboard, parse_mode="html")


def register_forward_handlers(dp: Dispatcher):
    dp.register_message_handler(forward_user, lambda message: message.forward_from is not None,
                                content_types=["text", "audio", "document", "photo", "sticker", "video", "video_note",
                                               "voice", "location", "contact"])
    dp.register_message_handler(forward_group, lambda message: message.forward_from_chat is not None,
                                content_types=["text", "audio", "document", "photo", "sticker", "video", "video_note",
                                               "voice", "location", "contact"])
