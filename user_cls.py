from datetime import datetime
from typing import Optional


class User:
    all_user = dict()

    def __init__(self, user_id):
        self.id_user: Optional[int] = None
        self.command: Optional[str] = None
        self.city_name: Optional[str] = None
        self.city_id: Optional[str] = None
        self.count_hotels: Optional[str] = None
        self.date_in: Optional[datetime] = None
        self.date_out: Optional[datetime] = None
        self.photo: Optional[str] = None
        self.count_photo: int = 0
        self.price_min: int = 0
        self.price_max: int = 0
        self.range_landmark_min: int = 0
        self.range_landmark_max: int = 0
        User.add_user(user_id, self)

    def get_dict(self):
        cls_dict = {
            'id_user': self.id_user,
            'command': self.command,
            'city_name': self.city_name,
            'city_id': self.city_id,
            'count_hotels': self.count_hotels,
            'date_in': self.date_in,
            'date_out': self.date_out,
            'photo': self.photo,
            'count_photo': self.count_photo,
            'price_min': self.price_min,
            'price_max': self.price_max,
            'range_landmark_min': self.range_landmark_min,
            'range_landmark_max': self.range_landmark_max
        }

        return cls_dict

    @staticmethod
    def get_user(user_id):
        if User.all_user.get(user_id) is None:
            new_user = User(user_id)
            return new_user
        return User.all_user.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.all_user[user_id] = user
