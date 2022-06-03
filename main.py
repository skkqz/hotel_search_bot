import os
import logic_bot

from loader import bot
from db.database_queries import user_history
from db.database import Users
from user_cls import User
from loguru import logger
from datetime import timedelta, date
from telegram_bot_calendar import DetailedTelegramCalendar


Users.create_a_database()


logger.add(os.path.abspath(os.path.join('logging', 'logging.log')), encoding='utf-8', rotation='10MB')


@bot.message_handler(commands=['start', 'help'])
def start_bot(message) -> None:
    bot.send_message(message.chat.id, text='\n✦Выполните одну из команд:'
                                           '\n✦ /lowprice — вывод самых дешёвых отелей в городе,'
                                           '\n✦ /highprice — вывод самых дорогих отелей в городе,'
                                           '\n✦ /bestdeal — вывод отелей, наиболее подходящих по цене и расположению '
                                           'от центра.'
                                           '\n✦ /history — вывод истории поиска отелей'
                                           '\n✦ /help — помощь по командам бота')

    logger.success(f'Пользователь id: {message.chat.id} - ввёл команду {message.text}')


@bot.message_handler(commands=['history'])
def history(message) -> None:
    history_user = user_history(message.chat.id)
    bot.send_message(message.chat.id, text=history_user)

    logger.success(f'Пользователь id: {message.chat.id} - ввёл команду {message.text}')


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def low_high_price(message) -> None:
    """
    Запуск события /lowprice, /highprice,/bestdeal. Запрашивает у пользователя город
    """

    user = User.get_user(message.chat.id)
    user.id_user = message.chat.id
    user.command = message.text
    name_city = bot.send_message(message.chat.id, text='Введите название города')
    bot.register_next_step_handler(name_city, logic_bot.id_city)

    logger.success(f'Пользователь id: {message.chat.id} - использовал команду {message.text}')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def call_date_in(call) -> None:
    """ Функция отвечает за выбор даты заезда в отель """

    min_date_in = date.today()
    max_date_in = min_date_in + timedelta(days=365)
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=min_date_in,
                                                 max_date=max_date_in).process(call.data)
    if not result and key:
        LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.edit_message_text(f'Дата заезда: {LSTEP[step]}', call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Дата заезда: {result}', call.message.chat.id, call.message.message_id)

        user = User.get_user(call.message.chat.id)
        user.date_in = result
        logger.success(f'Пользователь id: {call.message.chat.id} - дата заезда: {result}')

        # Вывод inline клавиатуры календаря даты выезда из отеля
        min_date_out = user.date_in
        max_date_out = min_date_out + timedelta(days=30)
        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=min_date_out,
                                                  max_date=max_date_out).build()
        LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.send_message(call.message.chat.id, f'Дата выезда: {LSTEP[step]}', reply_markup=calendar)

    elif call.data == 'cbcal_1_n':
        bot.answer_callback_query(callback_query_id=call.id, text='Выберете дату заезда в отель')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def call_date_out(call) -> None:
    """ Функция отвечает за выбор даты выезда из отель """

    user = User.get_user(call.message.chat.id)
    min_date_out = user.date_in + timedelta(days=1)
    max_date_out = min_date_out + timedelta(days=30)
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=min_date_out,
                                                 max_date=max_date_out).process(call.data)
    if not result and key:
        LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
        bot.edit_message_text(f"Дата выезда: {LSTEP[step]}", call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Дата выезда: {result}', call.message.chat.id, call.message.message_id)

        user = User.get_user(call.message.chat.id)
        user.date_out = result
        logger.success(f'Пользователь id: {call.message.chat.id} - дата выезда: {result}')

        if user.command == '/bestdeal':
            logger.success(f'Пользователь id: {call.message.chat.id} - ввод диапазон цен')

            range_price = bot.send_message(call.message.chat.id,
                                           text='Введите диапазон цен за сутки через пробел (пример ввода: 1000 5000)')
            bot.register_next_step_handler(range_price, logic_bot.check_price_range)
        else:
            logic_bot.result_lowprice(call.message)

    elif call.data == 'cbcal_2_n':
        bot.answer_callback_query(callback_query_id=call.id, text='Выберете дату выезда из отель')


@bot.callback_query_handler(func=lambda call: call.data.startswith('cnt_hotels'))
def call_count_hotels(call) -> None:
    """ Функция обрабатывает inline кнопки количества отелей """

    user = User.get_user(call.message.chat.id)
    user.count_hotels = call.data[-1]
    bot.send_message(call.message.chat.id, text='Выбрано количество отелей: {num}'.format(num=call.data[-1]))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    logger.success(f'Пользователь id: {call.message.chat.id} количество отелей {call.data[-1]}')
    logic_bot.photo_hotels(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
def call_photo_yes_no(call) -> None:
    """ Функция обрабатывает запрос вывода фотографий отеля """

    user = User.get_user(call.message.chat.id)
    if call.data.endswith('yes'):
        user.photo = 'Да'
        logic_bot.count_photo_hotels(call.message)

        logger.success(f'Пользователь id: {call.message.chat.id} - с загрузкой фотографий отеля')
    else:
        user.photo = 'Нет'
        logic_bot.date_in(call.message)
        logger.success(f'Пользователь id: {call.message.chat.id} - без загрузки фотографий отелей')
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cnt_photo'))
def call_count_photo(call) -> None:
    """ Функция обрабатывает запрос количества фотографий отеля"""

    user = User.get_user(call.message.chat.id)
    user.count_photo = int(call.data[-1])
    bot.send_message(call.message.chat.id, text=f'Загрузить {call.data[-1]} фотографий')
    logger.success(f'Пользователь id: {call.message.chat.id} - количество фотографий {call.data[-1]}')
    logic_bot.date_in(call.message)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)


if __name__ == '__main__':
    logger.success('Бот включен')
    bot.polling(none_stop=True, interval=0)
