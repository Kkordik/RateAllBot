import pyrogram
from multicolorcaptcha import CaptchaGenerator
import time
import os
import random
from pyrogram import Client

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import DATABASE_FILE, BOT_TOKEN, FAKE_RATES, api_hash, api_id, CAPCTHA_SIZE_NUM, CAPCTHA_DIFF_LVL
from texts import text
from database.Classes import *
from keyboards import rate_keyboard

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Rate(StatesGroup):
    rate = State()
    objectid = State()
    first_name = State()
    mention = State()
    captcha_answ = State()
    photo_path = State()
    message_id_edit = State()
    did_captcha = State()


def captcha_gen():

    generator = CaptchaGenerator(2)
    if random.choice([True, False]):
        multcol = random.choice([True, False])
        marg = random.choice([True, False])
        chrs_mode = random.choice(["nums", "hex", "ascii"])
        captcha = generator.gen_captcha_image(difficult_level=CAPCTHA_DIFF_LVL,
                                              multicolor=multcol,
                                              margin=marg,
                                              chars_mode=chrs_mode)
        image = captcha.image
        answer = captcha.characters
        but_numb = random.randint(4, 8)
        answ_but_numb = random.randint(1, but_numb)

        keyboard = types.InlineKeyboardMarkup(row_width=4)
        for i in range(but_numb):
            if i == answ_but_numb-1:
                keyboard.add(types.InlineKeyboardButton(text="{}".format(answer),
                                                        callback_data="answ_{}".format(answer)))
            else:
                keyb_answer = answer
                while keyb_answer == answer:
                    keyb_captcha = generator.gen_captcha_image(difficult_level=CAPCTHA_DIFF_LVL,
                                                               multicolor=multcol,
                                                               margin=marg,
                                                               chars_mode=chrs_mode)
                    keyb_answer = keyb_captcha.characters
                keyboard.add(types.InlineKeyboardButton(text="{}".format(keyb_answer),
                                                        callback_data="answ_{}".format(keyb_answer)))
    else:
        multcol = random.choice([True, False])
        marg = random.choice([True, False])
        allow_mult = random.choice([True, False])
        captcha = generator.gen_math_captcha_image(difficult_level=CAPCTHA_DIFF_LVL,
                                                   multicolor=multcol,
                                                   margin=marg,
                                                   allow_multiplication=allow_mult)
        image = captcha.image
        answer = captcha.equation_result
        but_numb = random.randint(4, 8)
        answ_but_numb = random.randint(1, but_numb)

        keyboard = types.InlineKeyboardMarkup(row_width=4)
        for i in range(but_numb):
            if i == answ_but_numb-1:
                "answ_{}".format(answer)
                keyboard.add(types.InlineKeyboardButton(text="{}".format(answer),
                                                        callback_data="answ_{}".format(answer)))
            else:
                keyb_answer = answer
                while keyb_answer == answer:
                    keyb_captcha = generator.gen_math_captcha_image(difficult_level=CAPCTHA_DIFF_LVL,
                                                                    multicolor=multcol,
                                                                    margin=marg,
                                                                    allow_multiplication=allow_mult)
                    keyb_answer = keyb_captcha.equation_result
                keyboard.add(types.InlineKeyboardButton(text="{}".format(keyb_answer),
                                                        callback_data="answ_{}".format(keyb_answer)))
    keyboard.add(types.InlineKeyboardButton("Отмена/Скасувати/Cancel", callback_data="answ_cancel"))

    timenow = int(time.time())
    photo_path = '{}.png'.format(timenow)
    image.save(photo_path, "png")
    photo = open(photo_path, "rb")

    return photo, answer, keyboard, photo_path


async def left_rate(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    userdb = UserDb(user_id)
    await userdb.search_add_user()
    rate = call.data.split("_")[1]
    object_id = call.data.split("_")[2]
    first_name = call.data.split("_")[3]
    mention = call.data.split("_")[4]

    photo, answer, keyboard, photo_path = captcha_gen()

    await bot.send_photo(chat_id, photo, reply_markup=keyboard, caption=text[userdb.lang]["make_captcha"],
                         parse_mode="html")
    os.remove(photo_path)

    state = dp.get_current().current_state(chat=chat_id, user=user_id)
    await state.set_state("Rate")
    await state.update_data(objectid=object_id, first_name=first_name, mention=mention, captcha_answ=answer, rate=rate,
                            message_id_edit=call.message.message_id)
    await Rate.did_captcha.set()
    await call.answer()


async def check_captch_answ(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    if call.data.split("_")[1] == "cancel":
        await state.finish()
        await call.answer(show_alert=True, text="Отменено/Скасовано/Canceled")
        await bot.delete_message(chat_id, call.message.message_id)
        return
    userdb = UserDb(user_id)
    await userdb.search_add_user()

    data = await state.get_data()
    object_id = data["objectid"]
    first_name = data["first_name"]
    mention = data["mention"]
    captcha_answ = data["captcha_answ"]
    rate = data["rate"]
    message_id_edit = data["message_id_edit"]

    if first_name == "None":
        first_name = None

    if mention == "None":
        mention = None
        displayed_name = first_name
    else:
        displayed_name = "@{}".format(mention)

    if str(captcha_answ) == call.data.split("_")[1]:
        await call.answer(show_alert=True, text=text[userdb.lang]["captch_done"])
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        objectdb = ObjectDb(object_id)
        await objectdb.delete_rate(user_id)
        await objectdb.insert_rate(user_id, rate)

        rates_numb, rate, user_left_rate = await objectdb.get_rate(user_id)

        rate = round(float(rate[0]), 2)

        keyboard = rate_keyboard(objectdb.objectid, first_name, mention, userdb)

        try:
            await bot.edit_message_text(text[userdb.lang]["rate"].format(displayed_name, rate,
                                                                         user_left_rate[0], rates_numb[0]),
                                        chat_id, message_id_edit, reply_markup=keyboard, parse_mode="html")
        except Exception as e:
            print(e)
        await state.finish()
    else:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        photo, answer, keyboard, photo_path = captcha_gen()

        await state.update_data(captcha_answ=answer)
        await bot.send_photo(chat_id, photo, reply_markup=keyboard, caption=text[userdb.lang]["make_captcha_again"],
                             parse_mode="html")
        os.remove(photo_path)



def register_left_rate_handler(dp: Dispatcher):
    dp.register_callback_query_handler(left_rate, lambda call: call.data.split("_")[0] == "rate")
    dp.register_callback_query_handler(check_captch_answ, lambda call: call.data.split("_")[0] == "answ",
                                       state=Rate.did_captcha)

