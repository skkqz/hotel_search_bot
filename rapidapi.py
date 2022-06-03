import requests

from loader import HEADERS, URL_ID_CITY, URL_INFO_HOTELS, URL_PHOTO
from main import logger
from typing import Any


def response_to_api(url, headers, params):
    """
    Шаблон для запросов к API

    :param url: url адрес страницы API
    :param headers: host и key доступ к  API
    :param params: Параметры поиска

    :return: ответ от сервера API
    """

    try:
        response = requests.request('GET', url=url, headers=headers, params=params, timeout=15)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            response.raise_for_status()
    except (Exception, TimeoutError) as err:
        logger.success(f'Произошла ошибка {err}')


def locations_city(name_city: str) -> Any:
    """
    Функция проверяет запрос API на наличия города
    :param name_city: Название города
    :return: Данные о городе
    """

    querystring = {"query": name_city, "locale": "ru_RU", "currency": "RUB"}

    response = response_to_api(url=URL_ID_CITY, headers=HEADERS, params=querystring)

    return response


def query_hotels(id_city: str, count_hotels: str, check_in: str, check_out: str, price_sort: str, price_min: int = None,
                 price_max: int = None, command: str = None) -> Any:
    """
    Функция проверяет запрос API отелей
    :param id_city: Расположение города
    :param command Команда выбранная пользователем
    :param count_hotels: Количество отелей на поиск
    :param check_in: Дата заезда в отель
    :param check_out: Дата выезда из отелЯ
    :param price_sort: Сортировка по цене
    :param price_min Минимальная цена отеля за сутки
    :param price_max Максимальная цена отеля за сутки

    :return: Данные о отелях в городе
    """

    querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": count_hotels, "checkIn": check_in,
                   "checkOut": check_out, "adults1": "1", "sortOrder": price_sort, "locale": "ru_RU", "currency": "RUB"}

    if command == '/bestdeal':
        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": '25', "checkIn": check_in,
                       "checkOut": check_out, "adults1": "1", "priceMin": price_min, "priceMax": price_max,
                       "sortOrder": price_sort, "locale": "ru_RU", "currency": "RUB"}

    response = response_to_api(url=URL_INFO_HOTELS, headers=HEADERS, params=querystring)

    return response


def photo_hostel(hotel_id: str) -> Any:
    """
    Функция проверяет запрос API фотографий отеля
    :param hotel_id: id отеля
    :return: Список фотографий отеля
    """

    querystring = {'id': str(hotel_id)}

    response = response_to_api(url=URL_PHOTO, headers=HEADERS, params=querystring)

    return response
