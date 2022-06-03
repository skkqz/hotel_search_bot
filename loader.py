import os
import telebot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN_BOT')
KEY = os.getenv('KEY_API')
URL_ID_CITY = os.getenv('URL_ID_CITY')
URL_INFO_HOTELS = os.getenv('URL_INFO_HOTELS')
URL_PHOTO = os.getenv('URL_PHOTO')
bot = telebot.TeleBot(TOKEN)
HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': KEY
}
