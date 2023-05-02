from aiogram import types
from texts import text
from database.Classes import UserDb


def start_keyboard(userdb):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    # keyboard.add(types.KeyboardButton(text[userdb.lang]["help"]), types.KeyboardButton(text[userdb.lang]["about_us"]))
    keyboard.add(types.KeyboardButton(text[userdb.lang]["edit_lang"]))
    return keyboard


def rate_keyboard(object_id, first_name, mention, userdb):
    keyboard = types.InlineKeyboardMarkup(row_width=5)

    if mention:
        keyboard.add(types.InlineKeyboardButton(
            text=text[userdb.lang]["share_rating"],
            url="https://t.me/share/url?url=http://t.me/rateallbot?start={}".format(mention))
        )

    keyboard.add(types.InlineKeyboardButton("1⭐️", callback_data="rate_1_{}_{}_{}".format(object_id, first_name, mention)),
                 types.InlineKeyboardButton("2⭐️", callback_data="rate_2_{}_{}_{}".format(object_id, first_name, mention)),
                 types.InlineKeyboardButton("3⭐️", callback_data="rate_3_{}_{}_{}".format(object_id, first_name, mention)),
                 types.InlineKeyboardButton("4⭐️", callback_data="rate_4_{}_{}_{}".format(object_id, first_name, mention)),
                 types.InlineKeyboardButton("5⭐️", callback_data="rate_5_{}_{}_{}".format(object_id, first_name, mention)))
    return keyboard
