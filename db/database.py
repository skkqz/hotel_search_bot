from peewee import *


users_db = SqliteDatabase('db/users_db.db')


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = users_db
        order_by = 'id'


class Users(BaseModel):
    requests_date = DateTimeField()
    user_id = IntegerField()
    command = TextField()
    city_name = TextField()
    city_id = TextField()
    count_hotels = TextField()
    date_in = DateField()
    date_out = DateField()
    photo = TextField()
    count_photo = IntegerField()
    price_min = IntegerField(default=0)
    price_max = IntegerField(default=0)
    range_landmark_min = IntegerField(default=0)
    range_landmark_max = IntegerField(default=0)

    class Meta:
        db_table = 'users'

    @staticmethod
    def create_a_database() -> None:
        """ Создаёт базу данных Users"""

        with users_db:
            users_db.create_tables([Users])
