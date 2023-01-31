import logging
from aiogram import types
from db import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.dispatcher import FSMContext
from states import properties


from main import dp, bot
from config import adminID
from mailing import sending_message, next_addressee, reset_counter
import keyboards.inline_keyboards as nav
import debug

db = Database('staff.db')
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
logging.basicConfig(level=logging.INFO)

helloText = \
"Привет!\nДобро пожаловать в бот оповещения о дежурстве на срочных.\n\
Теперь ты можешь забыть о беседе со срочными тасками, а когда нужно будет о ней вспомнить, я обязательно к тебе \
прибегу"

adminHello = \
"/add_user – Добавить пользователя. \n\
Пример использования команды: /add_user 0000000 (Где цифры это TG ID сотрудника) \n\
\n\
/remove_user – Удалить пользователя. \n\
Пример использования команды: /remove_user 0000000 (Где цифры это TG ID сотрудника)\n\
\n\
/send_all – Отправиль сообщение всем пользователям бота\n\
Пример использования команды: /send_all TEXT (Всем пользователям придет сообщение с текстом TEXT)\n\
\n\
/start_mailing – Запусить напоминания всем пользователям бота \n\
\n\
/stop_mailing – Остановить ежедневную рассылку)"

#setting up scheduling messages. Job starting in function mailing_functions() and stops at stop_mailing()
scheduler.add_job(sending_message, "cron", day_of_week = "mon,tue,wed,thu,fri", hour = "17",\
     minute = "0", second = "0", id = "sending_message_function", replace_existing=True)


async def send_to_admin(dp):
    await bot.send_message(chat_id = adminID, text = "Bot launched\n/admin_help")

async def empty(message: types.Message):
        await message.answer("Пустой запрос. Код ошибки 3")

async def private_only(message: types.Message):
    await message.reply("Я не общаюсь в общих беседах, пожалуйста, шепните это мне в личку:)")


@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
        if db.is_admin(message.from_user.id) == True:
            await properties.admin.set()
        else:
            pass
        if db.user_exists(message.from_user.id) == False or db.is_active_uid(message.from_user.id) == False:
            await properties.out_staff.set()
            await outstaff_message(message, state)
        else:
            await bot.send_message(message.from_user.id, helloText)
    else:
        await private_only(message)


@dp.message_handler(commands=["root"])
async def grant_admin(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
        if message.from_user.id == adminID:
            id = message.text[6:]
            await message.answer(db.grant_admin(id))


@dp.message_handler(commands=["unroot"])
async def grant_admin(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
        if message.from_user.id == adminID:
            id = message.text[8:]
            await message.answer("Done")
            await message.answer(db.revoke_admin(id, 0))


@dp.message_handler(state=properties.out_staff)
async def outstaff_message(message: types.Message, state: FSMContext):
    await message.answer(f"У тебы не хватает прав для использования бота. Пожалуйста, обратись к своему тимлиду.\
Код ошибки 403 Forbidden, uid {message.from_user.id}")


@dp.message_handler(commands=["admin_help"], state=properties.admin)
async def admin_help(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
            await bot.send_message(message.from_user.id, adminHello)
    else:
        await private_only(message)


@dp.message_handler(commands=["send_all"], state=properties.admin)
async def send_all(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        message_text = message.text[9:]
        users = db.number_of_users()
        if message.text != "/send_all":
            for i in range (1, users+1):
                logging.info(db.is_active(i))
                if db.is_active(i)==True:
                    await bot.send_message(db.get_user_ud(i), message_text)
                else:
                    continue
            await bot.send_message(message.from_user.id, "Успешная рассылка")
            await bot.send_message(message.from_user.id, message.text)
        else:
            await empty(message)
    else:
        await private_only(message)



@dp.message_handler(commands=['add_user'], state=properties.admin)
async def add_user(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
        if message.text!="/add_user":
            id = message.text[9:]
            db.add_user(id)
            await message.answer(f"Пользователь с ID{id} добавлен")
        else:
            await empty(message)
    else:
        await private_only(message)
    
@dp.message_handler(commands=('remove_user'), state=properties.admin)
async def remove_user(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
        if message.text != "remove_user":
            id = message.text[13:]
            db.set_active(id, 0)
            await message.answer(f"Пользователь с ID {id} удален")
        else:
            await empty(message)
    else:
        await private_only(message)

@dp.message_handler(commands=("start_mailing"), state=properties.admin)
async def start_mailing(message: types.Message, state: FSMContext):
    logging.info("start_mailing func lautched")
    if message.chat.type == "private":
            try:    
                message_text = "Работа бота была запущена администратором"
                users = db.number_of_users()
                for i in range (1, users+1):
                    if db.is_active(i)==True:
                        await bot.send_message(db.get_user_ud(i), message_text)
                        logging.info(f"sent to {db.get_user_ud(i)}")
                    else:
                        continue
                scheduler.start()
            except Exception as e:
                await bot.send_message(message.from_user.id, e)
    else:
        await private_only(message)

@dp.message_handler(commands=("stop_mailing"), state=properties.admin)
async def start_mailing(message: types.Message, state: FSMContext):
    logging.info("stop_mailing func lautched")
    if message.from_user.id == adminID:
        scheduler.shutdown()
        message_text = "Работа бота была остановлена администратором"
        users = db.number_of_users()
        for i in range (1, users+1):
            if db.is_active(i)==True:
                await bot.send_message(db.get_user_ud(i), message_text)
                logging.info(f"sent to {db.get_user_ud(i)}")
            else:
                continue
    else:
        await private_only(message)


@dp.message_handler(commands=("start_over"), state=properties.admin)
async def start_over(message:types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, text="Вы уверены, что хотите начать очередь с начала?", reply_markup=nav.inline_kb_reset_queue)

"""
▼▼▼ button functions ▼▼▼
"""

@dp.callback_query_handler(text="needOk", state="*")
async def noWorkTomorow(message: types.Message):
    await bot.delete_message(message.from_user.id,message.message.message_id)  
    await bot.send_message(message.from_user.id, text="Вы уверены, что пропускаете очередь дежурить?\
         \nНапример, причиной для этого может быть отпуск или болезнь", reply_markup=nav.inline_kb_confirmation)


@dp.callback_query_handler(text="iAmSure", state="*")
async def got_confirmation(message: types.Message):
    await next_addressee()
    await bot.delete_message(message.from_user.id,message.message.message_id)  
    await bot.send_message(message.from_user.id, text="Готово! Уведомление о дежурстве выслано следующему по очереди сотруднику.\
        \nУдачного отдыха:)")

@dp.callback_query_handler(text="Ooops", state="*")
async def mistakes_were_made(message: types.Message):
    await bot.delete_message(message.from_user.id,message.message.message_id)    
    await bot.send_message(message.from_user.id, text="Отменено. Удачи завтра на срочных тасках!")

@dp.callback_query_handler(text="resetPlease", state=properties.admin)
async def resetPlease(message: types.Message):
    await bot.delete_message(message.from_user.id,message.message.message_id) 
    await reset_counter()
    await bot.send_message(message.from_user.id, text="Готово!")

@dp.callback_query_handler(text="doNotReset", state=properties.admin)
async def doNotReset(message: types.Message):
    await bot.delete_message(message.from_user.id,message.message.message_id)    
    await bot.send_message(message.from_user.id, text="Отменено")
