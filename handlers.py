import json
import re
import os
from loguru import logger
from telebot import types
from typing import Any
from rapidapi import locations_city, query_hotels, photo_hostel

logger.add(os.path.abspath(os.path.join('logging', 'logging.log')), encoding='utf-8', rotation='5 MB')


def city_search(name_city: str) -> Any:
    """
    Функция проверяет запрос API города и забирает нужную информацию о городе в котором будет поиск отелей
    :param name_city: называние города
    :return: Строка с id города
    """
    try:
        info_city = locations_city(name_city)
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        re_info_city = re.search(pattern, info_city)
        if re_info_city:
            result = json.loads(f'{{{re_info_city[0]}}}')
            return result['entities'][0]
        else:
            return None
    except Exception as err:
        logger.success(f'Город {name_city} не найден! Ошибка {err}')


def hotel_search(id_city: str, count_hotels: str, check_in: str, check_out: str, command: str, price_min: int = None,
                 price_max: int = None) -> Any:
    """
    Функция запрашивает у API список отелей в городе
    :param id_city: id города
    :param count_hotels: Количество отелей на вывод
    :param check_in: Дата заезда в отель
    :param check_out: Дата выезда из отеля
    :param command: Дешевые или дорогие отели
    :param price_min Минимальная цена отеля за сутки
    :param price_max Максимальная цена отеля за сутки

    :return: Список отелей в городе по указанным параметрам
    """

    price = 'PRICE'
    if command == '/highprice':
        price = 'PRICE_HIGHEST_FIRST'
    try:
        info_hotel = query_hotels(id_city, count_hotels, check_in, check_out, price, price_min, price_max, command)

        pattern = r'(?<="results".).*?}}]'
        re_info_hotel = re.search(pattern, info_hotel)
        if re_info_hotel:
            result = json.loads(re_info_hotel[0])
            return result
    except Exception as err:
        logger.success(f'Запрашиваемый ключ не найден! Ошибка {err}')


def photo_search(id_hotel: str, count_hotel: int) -> Any:
    """
    Функция находит фото отеля
    :param id_hotel: id отеля
    :param count_hotel: число выводимых фотографий отеля
    :return: Список с ссылками на фото отелей
    """

    photo = list()
    try:
        info_photo = photo_hostel(id_hotel)
        pattern = r'(?<="hotelImages".).*?}}]'
        re_info_photo = re.search(pattern, info_photo)
        if re_info_photo:
            result = json.loads(re_info_photo[0])

            for i_count, i_photo in enumerate(result):
                if count_hotel == i_count:
                    break
                photo.append(types.InputMediaPhoto(i_photo['baseUrl'].format(size='z')))

            return photo
    except Exception as err:
        logger.success(f'Запрашиваемый ключ не найден! Ошибка {err}')
