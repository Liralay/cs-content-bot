from db import Database
import logging
from main import bot
from db import Database
import keyboards.inline_keyboards as nav

db = Database('staff.db')
users = db.number_of_users()

logging.basicConfig(level=logging.INFO)

i = 1 
'''
ˆ i var is an indicator of current recipient ID. It is needs to be set outside the function to be used in multiple functions
  переенная i – ID текущего получателя. Устанавливается вне функций для того чтобы к ней можно было получить доступ из всей программы. 
  Для использования внутри функции используется ключевое слово global
'''

async def sending_message():
    global i
    global users
    logging.info(f"f.statred id = {i}")
    id = db.get_user_ud(i)
    if db.is_active(i) == 1:
        logging.info(f'sedning message to {i} ID')
        await bot.send_message(id, text="Завтра твоя очередь дежурить на срочных тасках!", reply_markup = nav.inline_kb1)
        if i == users:
            i = 1
        else:
            i+=1
        logging.info(f"sending message done working_id changed to {i}")
    else:
        if i == users:
            i = 1
        else:
            i+=1


async def reset_counter():
    global i
    i = 1
    logging.info(f" i is set to {i}")
        

async def next_addressee():
    # global i
    # if i == users:
    #     i = 1
    # else:
    #     i+=1
    await sending_message()
    logging.info(f'next_a function done working')

