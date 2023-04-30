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


async def search_chat_id(mention):
    object_id, obj_type, subs_numb, is_chat_mention = None, None, None, True
    try:
        chat = await bot.get_chat("@{}".format(mention))
        object_id = chat.id
        obj_type = chat.type
        app = Client("my_account", api_id, api_hash)
        await app.start()
        subs_numb = await app.get_chat_members_count("@{}".format(mention))
        await app.stop()
    except Exception:
        is_chat_mention = False

    return object_id, obj_type, subs_numb, is_chat_mention


async def search_not_chat(mention, chat_id, userdb):
    try:
        app = Client("my_account", api_id, api_hash)
        try:
            await app.start()
            user = await app.get_users("@{}".format(mention))
            object_id = user.id
            if user.is_bot:
                obj_type = "bot"
            else:
                obj_type = "user"
            await app.stop()
            return object_id, obj_type
        except Exception as e:
            await app.stop()
            print(e)
            await bot.send_message(chat_id, text[userdb.lang]["smth_wrong"])
    except Exception as e:
        print("serch_not_chat   ", e)


async def username(message: types.Message):
    print(message.text.split("t.me/"), "  username ", message.entities)
    chat_id = message.chat.id
    user_id = message.from_user.id
    m_text = message.text
    subs_numb = None

    userdb = UserDb(user_id)
    await userdb.search_add_user()
    sended_message = await bot.send_message(chat_id, text[userdb.lang]["wait"])

    # parsing mention from message
    if m_text not in m_text.split("@"):
        mention = m_text.split("@")[1].split()[0]
    elif m_text not in m_text.split("t.me/"):
        mention = m_text.split("t.me/")[1].split()[0]
    else:
        await bot.send_message(chat_id, text[userdb.lang]["smth_wrong"])
        return

    # searching chat_id of mentioned group/ channel
    object_id, obj_type, subs_numb, is_chat_mention = await search_chat_id(mention)

    # searching chat_id if mentioned is not group/ channel and is user/ bot
    if not is_chat_mention:
        object_id, obj_type = await search_not_chat(mention, chat_id, userdb)

    # object searchind/adding db
    objectdb = ObjectDb(object_id, obj_type)
    print(object_id)
    await objectdb.search_add_obj()

    # fake rates
    if FAKE_RATES and objectdb.new_obj:
        await objectdb.create_fake_rates(subs_numb)

    # getting rate
    rates_numb, rate, user_left_rate = await objectdb.get_rate(user_id)

    if rate[0] is not None:
        rate = round(float(rate[0]), 2)
    else:
        rate = 0

    keyboard = rate_keyboard(objectdb.objectid, mention)
    if user_left_rate is not None:
        await bot.edit_message_text(text[userdb.lang]["rate"].format("@{}".format(mention), rate,
                                                                     user_left_rate[0], rates_numb[0]), sended_message.chat.id,
                                    sended_message.message_id, reply_markup=keyboard, parse_mode="html")
    else:
        await bot.edit_message_text(text[userdb.lang]["rate_not_full"].format("@{}".format(mention), rate, rates_numb[0]),
                                    sended_message.chat.id,
                                    sended_message.message_id, reply_markup=keyboard, parse_mode="html")


def register_username_handlers(dp: Dispatcher):
    dp.register_message_handler(username, lambda message: "mention" in str(message.entities) or
                                                          message.text not in message.text.split("t.me/"))
