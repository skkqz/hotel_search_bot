import handlers
import re

from main import bot, logger
from db.database_queries import database_entry
from user_cls import User
from datetime import timedelta, date
from inline_buttons import cnt_hotels_button, photo_hotels_button, count_photo_hotels_button
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telebot.apihelper import ApiException


def id_city(message) -> None:
    """ Запрос у пользователя количество отелей для поиска """

    logger.success(f'Пользователь id: {message.chat.id} - ввёл город {message.text.lower()}')
    check_city = handlers.city_search(message.text.lower())
    if check_city:
        user = User.get_user(message.chat.id)
        user.city_name = check_city['name']
        user.city_id = check_city['destinationId']
        markup = cnt_hotels_button()
        bot.send_message(message.chat.id, text='Выберете количество отелей', reply_markup=markup)

        logger.success(f'Пользователь id: {message.chat.id} - выбор количество отелей')
    else:
        bot.send_message(message.chat.id, text='Такой город не найден. Попробуйте еще раз.')


def photo_hotels(message) -> None:
    """ Запрос у пользователя нужны ли фотографии отеля """

    markup = photo_hotels_button()
    bot.send_message(message.chat.id, text='Загрузить фото для каждого отеля?', reply_markup=markup)


def count_photo_hotels(message) -> None:
    """ Запрос у пользователя количество фотографий """

    markup = count_photo_hotels_button()
    bot.send_message(message.chat.id, text='Количество фотографий ?', reply_markup=markup)


def date_in(message) -> None:
    """ Вывод inline клавиатуры календаря даты заезда """

    min_date_in = date.today()
    max_date_in = min_date_in + timedelta(days=365)
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=min_date_in,
                                              max_date=max_date_in).build()
    LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
    bot.send_message(message.chat.id, f'Дата заезда: {LSTEP[step]}', reply_markup=calendar)


def result_lowprice(message) -> None:
    """ Вывод результата поиска отеля по команде lowprice, highprice"""

    bot.send_message(message.chat.id, text='Пожалуйста подождите, выполняется поиск отелей...')
    logger.success(f'Пользователь id: {message.chat.id} - выполняется загрузка отелей')

    user = User.get_user(message.chat.id)
    user_dict = user.get_dict()
    database_entry(user_dict)

    res_hotels = handlers.hotel_search(user_dict['city_id'], user_dict['count_hotels'],
                                       user_dict['date_in'], user_dict['date_out'], user_dict['command'])
    photo_true = user_dict['photo']
    count = 0

    for i_hotel in res_hotels:
        price_int = i_hotel['ratePlan']['price']['current'].split()
        price_int[0] = str(int(price_int[0].replace(',', '')) * (user_dict['date_out'] - user_dict['date_in']).days)
        template = '✦Название отеля: {name}' \
                   '\n✦Адрес: {address}' \
                   '\n✦Дата заезда: {date_in}' \
                   '\n✦Дата выезда: {date_out}' \
                   '\n✦Цена за период проживания от: {price}' \
                   '\n✦Расстояние от центра города: {distance}' \
                   '\n✦Сайт отеля: {url_hotels}'.format(
                    name=i_hotel['name'],
                    address=i_hotel['address'].get('streetAddress', 'Адрес можно узнать на сайте'),
                    date_in=user_dict['date_in'],
                    date_out=user_dict['date_out'],
                    distance=i_hotel['landmarks'][0]['distance'],
                    price=' '.join(price_int),
                    url_hotels='https://ru.hotels.com/ho{id}'.format(id=i_hotel['id'])
                )

        try:
            if photo_true == 'Да':
                photo = handlers.photo_search(i_hotel['id'], user_dict['count_photo'])
                if photo:
                    bot.send_media_group(message.chat.id, photo)
            count += 1
            bot.send_message(message.chat.id, text=template)
        except ApiException as ex:
            logger.success(f'Ошибка: {ex}')

    bot.send_message(message.chat.id, text=f'Найдено отелей {count} из {user_dict["count_hotels"]}')
    logger.success(f'Для пользователя {message.chat.id} найдено отелей {count} из {user_dict["count_hotels"]}')


def check_price_range(message) -> None:
    """Проверка и запись ввода пользователем данных, минимальной и максимальной цены"""

    user = User.get_user(message.chat.id)
    check_price = message.text.split()
    if len(check_price) == 2 and check_price[0].isdigit() and check_price[1].isdigit():
        if int(check_price[0]) < int(check_price[1]):
            price_min, price_max = int(check_price[0]), int(check_price[1])
        else:
            price_min, price_max = int(check_price[1]), int(check_price[0])
        user.price_min, user.price_max = price_min, price_max
        logger.success(f'Пользователь id: {message.chat.id} - цены: {price_min} - {price_max}')

        logger.success(f'Пользователь id: {message.chat.id} - ввод диапазон расстояния от центра города')
        range_price = bot.send_message(message.chat.id, text='Введите диапазон расстояния в км от центра города через '
                                                             'пробел (пример ввода: 1 5)')
        bot.register_next_step_handler(range_price, check_landmark_range)
    else:
        input_error = bot.send_message(message.chat.id, text='Ошибка ввода. Попробуйте еще раз')
        bot.register_next_step_handler(input_error, check_price_range)


def check_landmark_range(message) -> None:
    """Проверка и запись ввода пользователем данных о расстояние от центра города"""

    user = User.get_user(message.chat.id)
    check_range = message.text.split()
    if len(check_range) == 2 and check_range[0].isdigit() and check_range[1].isdigit():
        if int(check_range[0]) < int(check_range[1]):
            range_min, range_max = int(check_range[0]), int(check_range[1])
        else:
            range_min, range_max = int(check_range[1]), int(check_range[0])
        user.range_landmark_min, user.range_landmark_max = range_min, range_max
        logger.success(f'Пользователь id: {message.chat.id} - '
                       f'ввод диапазон расстояния от центра города: {range_min} - {range_max}')
        result_bestdeal(message)
    else:
        input_error = bot.send_message(message.chat.id, text='Ошибка ввода. Попробуйте еще раз')
        bot.register_next_step_handler(input_error, check_landmark_range)


def result_bestdeal(message) -> None:
    """Вывод результата поиска отелей по команде bestdeal"""

    bot.send_message(message.chat.id, text='Пожалуйста подождите, выполняется поиск отелей...')
    logger.success(f'Пользователь id: {message.chat.id} - выполняется загрузка отелей')

    user = User.get_user(message.chat.id)
    user_dict = user.get_dict()
    database_entry(user_dict)

    result_hotels = handlers.hotel_search(user_dict['city_id'], user_dict['count_hotels'], user_dict['date_in'],
                                          user_dict['date_out'], user_dict['command'], user_dict['price_min'],
                                          user_dict['price_max'])
    count = 0

    try:
        for i_hotel in result_hotels:
            if count == int(user_dict['count_hotels']):
                break
            price_int = i_hotel['ratePlan']['price']['current'].split()
            price_int[0] = str(int(price_int[0].replace(',', '')) * (user_dict['date_out'] - user_dict['date_in']).days)
            template = '✦Название отеля: {name}' \
                       '\n✦Адрес: {address}' \
                       '\n✦Дата заезда: {date_in}' \
                       '\n✦Дата выезда: {date_out}' \
                       '\n✦Цена за период проживания от: {price}' \
                       '\n✦Расстояние от центра города: {distance}' \
                       '\n✦Сайт отеля: {url_hotels}'.format(
                        name=i_hotel['name'],
                        address=i_hotel['address'].get('streetAddress', 'Адрес можно узнать на сайте'),
                        date_in=user_dict['date_in'],
                        date_out=user_dict['date_out'],
                        distance=i_hotel['landmarks'][0]['distance'],
                        price=' '.join(price_int),
                        url_hotels='https://ru.hotels.com/ho{id}'.format(id=i_hotel['id'])
            )

            distance_float = re.sub(r',', r'.', i_hotel['landmarks'][0]['distance'][:3])

            try:
                if user_dict['range_landmark_min'] < float(distance_float) < user_dict['range_landmark_max']:
                    if user_dict['photo'] == 'Да':
                        photo = handlers.photo_search(i_hotel['id'], user_dict['count_photo'])
                        if photo:
                            bot.send_media_group(message.chat.id, photo)
                    count += 1
                    bot.send_message(message.chat.id, text=template)
            except (Exception, ApiException) as ex:
                logger.success(f'Ошибка: {ex}')

        if count == 0:
            bot.send_message(message.chat.id, text=f'По вашему запросу отеле не найдены. Попробуйте другие значения, '
                                                   f'например цена проживания.')
        else:
            bot.send_message(message.chat.id, text=f'Найдено отелей {count} из {user_dict["count_hotels"]}')
    except TypeError as ty:
        logger.success(f'Ошибка: {ty}')
        bot.send_message(message.chat.id, text='Ой, какая-то ошибка. Попробуйте еще раз.')

    logger.success(f'Для пользователя {message.chat.id} найдено отелей {count} из {user_dict["count_hotels"]}')
