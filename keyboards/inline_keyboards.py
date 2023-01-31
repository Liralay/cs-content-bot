from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_btn_1 = InlineKeyboardButton('Я не буду дежурить завтра', callback_data='needOk')
inline_kb1 = InlineKeyboardMarkup(row_width=1)
inline_kb1.add(inline_btn_1)

confirmation_btn_1 = InlineKeyboardButton('Да. (Пока на расслабоне, на чиле)', callback_data="iAmSure")
confirmation_btn_2 = InlineKeyboardButton('Нет, верни обратно', callback_data="Ooops")
inline_kb_confirmation = InlineKeyboardMarkup(row_width=1)
inline_kb_confirmation.add(confirmation_btn_1).add(confirmation_btn_2)

reset_queue_y = InlineKeyboardButton("Да", callback_data="resetPlease")
reset_queue_n = InlineKeyboardButton("Нет", callback_data="doNotReset")
inline_kb_reset_queue = InlineKeyboardMarkup(row_width=1)
inline_kb_reset_queue.add(reset_queue_y).add(reset_queue_n)


