from datetime import datetime
from db.database import Users, users_db
from typing import Dict


def database_entry(user_dict: Dict) -> None:
    """ Запись полученных данных от пользователя в базу данных"""

    with users_db:
        if user_dict['command'] == '/bestdeal':
            Users(requests_date=datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                  user_id=user_dict['id_user'],
                  command=user_dict['command'],
                  city_name=user_dict['city_name'],
                  city_id=user_dict['city_id'],
                  count_hotels=user_dict['count_hotels'],
                  date_in=user_dict['date_in'],
                  date_out=user_dict['date_out'],
                  photo=user_dict['photo'],
                  count_photo=user_dict['count_photo'],
                  price_min=user_dict['price_min'],
                  price_max=user_dict['price_max'],
                  range_landmark_min=user_dict['range_landmark_min'],
                  range_landmark_max=user_dict['range_landmark_max']).save()
        else:
            Users(requests_date=datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                  user_id=user_dict['id_user'],
                  command=user_dict['command'],
                  city_name=user_dict['city_name'],
                  city_id=user_dict['city_id'],
                  count_hotels=user_dict['count_hotels'],
                  date_in=user_dict['date_in'],
                  date_out=user_dict['date_out'],
                  photo=user_dict['photo'],
                  count_photo=user_dict['count_photo']).save()


def user_history(user_id: int) -> str:
    """ Показывает пользователю последние 5 запросов"""

    with users_db:
        user = Users.select().where(Users.user_id == user_id).limit(5).order_by(Users.id.desc())

        template = '\n✦Дата выполнение запроса: {date_request}' \
                   '\n✦Команда: {command}'\
                   '\n✦Город: {city_name}' \
                   '\n✦Количество отелей: {count_hotels}' \
                   '\n✦Дата заезда в отель: {date_in}' \
                   '\n✦Дата выезда из отеля: {date_out}' \
                   '\n✦Фото: {photo}' \
                   '\n✦Количество фотографий: {count_photo}' \
                   '\n' + '=' * 35

        template_bestdeal = '\n✦Дата выполнение запроса: {date_request}' \
                            '\n✦Команда: {command}' \
                            '\n✦Город: {city_name}' \
                            '\n✦Количество отелей: {count_hotels}' \
                            '\n✦Дата заезда в отель: {date_in}' \
                            '\n✦Дата выезда из отеля: {date_out}' \
                            '\n✦Фото: {photo}' \
                            '\n✦Количество фотографий: {count_photo}' \
                            '\n✦Минимальная цена за ночь в отеле: {price_min}' \
                            '\n✦Минимальная цена за ночь в отеле: {price_max}' \
                            '\n✦Минимальное расстояние отеля от центра города: {range_landmark_min}' \
                            '\n✦Максимальное расстояние отеля от центра города: {range_landmark_max}' \
                            '\n' + '=' * 35

        str_result = ''
        for i in reversed(user):
            if i.command == '/bestdeal':
                result = template_bestdeal.format(
                    date_request=i.requests_date,
                    command=i.command,
                    city_name=i.city_name,
                    count_hotels=i.count_hotels,
                    date_in=i.date_in,
                    date_out=i.date_out,
                    photo=i.photo,
                    count_photo=i.count_photo,
                    price_min=i.price_min,
                    price_max=i.price_max,
                    range_landmark_min=i.range_landmark_min,
                    range_landmark_max=i.range_landmark_max
                )
            else:
                result = template.format(
                    date_request=i.requests_date,
                    command=i.command,
                    city_name=i.city_name,
                    count_hotels=i.count_hotels,
                    date_in=i.date_in,
                    date_out=i.date_out,
                    photo=i.photo,
                    count_photo=i.count_photo
                )
            str_result += result

        return str_result
