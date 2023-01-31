from asyncio import get_event_loop
from aiogram import Bot, Dispatcher, executor
from config import token
from aiogram.contrib.fsm_storage.memory import MemoryStorage



loop = get_event_loop()
bot = Bot(token, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())


if __name__ == "__main__":
    from handlers import dp, send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)