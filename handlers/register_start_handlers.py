from aiogram import Dispatcher
from handlers.start_cmd import register_start_cmd_handlers
from handlers.username import register_username_handlers
from handlers.left_rate import register_left_rate_handler
from handlers.forward import register_forward_handlers


def register_start_handlers(dp: Dispatcher):
    register_start_cmd_handlers(dp)
    register_username_handlers(dp)
    register_left_rate_handler(dp)
    register_forward_handlers(dp)

