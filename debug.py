import logging
from aiogram.dispatcher import FSMContext
from states import properties
from aiogram import types
from main import dp
from mailing import sending_message
from db import Database
import config

debugToggle = True
db = Database('staff.db')

@dp.message_handler(commands=("qwe"), state = "*")
async def qwe(message: types.Message):
    logging.info("qwe function started working")
    global debugToggle
    if debugToggle == True:
        try:
            await message.answer_sticker('CAACAgIAAxkBAAET289j2Jyap9y51V6QtfU6OdwiIp3BGwACZwADkp8eETTKV0Pwm88HLQQ')
        except Exception as e:
            await message.answer(e)


@dp.message_handler(commands="send_now", state = "*")
async def send_now(message: types.Message):
    global debugToggle
    if message.from_user.id == config.adminID:
        try:
            if debugToggle == True:
                await sending_message()
        except Exception as e:
            await message.answer(e)
    else:
        await message.answer_sticker('CAACAgIAAxkBAAET289j2Jyap9y51V6QtfU6OdwiIp3BGwACZwADkp8eETTKV0Pwm88HLQQ')


@dp.message_handler(commands=("debug"), state = properties.admin)
async def start_mailing(message: types.Message):
    global debugToggle
    if message.chat.type == "private":
        if message.from_user.id == config.adminID:
            if debugToggle == True:
                debugToggle = False
                await message.answer(f"Режим debug выключен")
            else:
                debugToggle = True
                await message.answer(f"Включен режим debug. Доступные команды /qwe /send_now /debug")
        else: 
            await message.answer_sticker('CAACAgIAAxkBAAET289j2Jyap9y51V6QtfU6OdwiIp3BGwACZwADkp8eETTKV0Pwm88HLQQ')


@dp.message_handler(commands=("set_active"), state = properties.admin)
async def set_active(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id == config.adminID:
            if message.text != "/set_active":
                id = message.text[12:]
                db.set_active(id, 1)
                await message.answer(f"Рассылка пользователю с {id} возобновлена ")
            else:
                await message.answer("Пустой запрос. Код ошибки 3")
        else:
            await message.answer_sticker('CAACAgIAAxkBAAET289j2Jyap9y51V6QtfU6OdwiIp3BGwACZwADkp8eETTKV0Pwm88HLQQ')
    else:
        await message.reply("Я не общаюсь в общих беседах, пожалуйста, шепните это мне в личку:)")


@dp.message_handler(commands=("number"), state = "*")
async def db_number(message: types.Message):   
        if message.chat.type == "private" and message.from_user.id == config.adminID:
            await message.answer(db.number_of_users())
        else:
            await message.answer_sticker('CAACAgIAAxkBAAET289j2Jyap9y51V6QtfU6OdwiIp3BGwACZwADkp8eETTKV0Pwm88HLQQ')


@dp.message_handler(commands=("is_root"), state="*")
async def is_root(message: types.Message):
    id = message.text[9:]
    if message.text == "/is_root":
        await message.answer(f"Ваш статус root: {db.is_admin(message.from_user.id)}")
    else:
        await message.answer(f"Статус root {id}: {db.is_admin(id)}")

            
@dp.message_handler(commands=["root_back"], state = properties.admin)
async def grant_admin(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id == config.adminID:
            id = message.text[11:]
            await message.answer("Done")
            await message.answer(db.revoke_admin(id, 1))

