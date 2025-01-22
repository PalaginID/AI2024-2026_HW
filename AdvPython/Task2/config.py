import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
FOOD_TOKEN = os.getenv('FOOD_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')