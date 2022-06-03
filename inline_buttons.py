from telebot import types


def cnt_hotels_button():
    markup = types.InlineKeyboardMarkup()
    but1 = types.InlineKeyboardButton(text='1', callback_data='cnt_hotels_1')
    but2 = types.InlineKeyboardButton(text='2', callback_data='cnt_hotels_2')
    but3 = types.InlineKeyboardButton(text='3', callback_data='cnt_hotels_3')
    but4 = types.InlineKeyboardButton(text='4', callback_data='cnt_hotels_4')
    but5 = types.InlineKeyboardButton(text='5', callback_data='cnt_hotels_5')
    but6 = types.InlineKeyboardButton(text='6', callback_data='cnt_hotels_6')
    but7 = types.InlineKeyboardButton(text='7', callback_data='cnt_hotels_7')
    but8 = types.InlineKeyboardButton(text='8', callback_data='cnt_hotels_8')
    but9 = types.InlineKeyboardButton(text='9', callback_data='cnt_hotels_9')
    markup.add(but1, but2, but3, but4, but5, but6, but7, but8, but9)

    return markup


def photo_hotels_button():
    markup = types.InlineKeyboardMarkup()
    but1 = types.InlineKeyboardButton(text='Да', callback_data='photo_yes')
    but2 = types.InlineKeyboardButton(text='Нет', callback_data='photo_no')
    markup.add(but1, but2)

    return markup


def count_photo_hotels_button():
    markup = types.InlineKeyboardMarkup()
    but1 = types.InlineKeyboardButton(text='1', callback_data='cnt_photo_1')
    but2 = types.InlineKeyboardButton(text='2', callback_data='cnt_photo_2')
    but3 = types.InlineKeyboardButton(text='3', callback_data='cnt_photo_3')
    but4 = types.InlineKeyboardButton(text='4', callback_data='cnt_photo_4')
    but5 = types.InlineKeyboardButton(text='5', callback_data='cnt_photo_5')
    markup.add(but1, but2, but3, but4, but5)

    return markup

