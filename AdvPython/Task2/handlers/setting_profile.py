from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from googletrans import Translator
import requests
from BotForms import UserProfile
from config import WEATHER_TOKEN


WEATHER_API = WEATHER_TOKEN
users = {}
tracking_features = {'logged_water': 0, 'logged_calories': 0, 'burned_calories': 0}

router = Router()


def calculate_calories(weight, height, age, activity):
    return 10*weight + 6.25*height - 5*age + 100*(activity//30)


def calculate_water(weight, activity, city):
    try:
        result = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}').json()
        temp = int(result['main']['temp']) - 273
        if temp > 25:
            return weight*30 + 500*(activity//30) + 750, temp
        else: 
            return weight*30 + 500*(activity//30), temp
    except Exception:
        return weight*30 + 500*(activity//30), None



@router.message(Command("set_profile"))
async def set_profile_start(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(UserProfile.weight)


@router.message(UserProfile.weight)
async def proccess_weight(message: Message, state: FSMContext):
    await state.update_data(weight=float(message.text))
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(UserProfile.height)


@router.message(UserProfile.height)
async def proccess_height(message: Message, state: FSMContext):
    await state.update_data(height=float(message.text))
    await message.reply("Введите ваш возраст:")
    await state.set_state(UserProfile.age)


@router.message(UserProfile.age)
async def proccess_age(message: Message, state: FSMContext):
    await state.update_data(age=float(message.text))
    await message.reply("Введите сколько минут в день вы уделяете спорту:")
    await state.set_state(UserProfile.activity)


@router.message(UserProfile.activity)
async def proccess_activity(message: Message, state: FSMContext):
    await state.update_data(activity=float(message.text))
    await message.reply("Введите город вашего проживания на английском и без тире:")
    await state.set_state(UserProfile.city)


@router.message(UserProfile.city)
async def proccess_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    water, temp = calculate_water(data['weight'], data['activity'], data['city'])
    calorie = calculate_calories(data['weight'], data['height'], data['age'], data['activity'])
    await state.update_data(temperature=temp)
    await state.update_data(water_goal=water)
    await state.update_data(calories_goal=calorie)
    await message.reply(f"Рассчитанная цель калорий: {calorie} ккал.\nЕсли хотите установить другое значение - введите число, иначе отправьте 'нет'")
    await state.set_state(UserProfile.calories_goal)


@router.message(UserProfile.calories_goal)
async def proccess_calorie_goal(message: Message, state: FSMContext):
    if message.text.lower() != 'нет':
        await state.update_data(calories_goal=float(message.text))
    data = await state.get_data()
    profile_info = (f"Ваш профиль:\n"
                    f"Вес: {data['weight']} кг\n"
                    f"Рост: {data['height']} см\n"
                    f"Возраст: {data['age']} лет\n"
                    f"Активность: {data['activity']} мин/день\n"
                    f"Город: {data['city']} (Температура: {data['temperature']})\n"
                    f"Норма воды: {data['water_goal']} мл.\n"
                    f"Цель калорий: {data['calories_goal']} ккал")
    
    user_id = message.from_user.id
    users[user_id] = dict(list(data.items())+list(tracking_features.items()))
    
    await message.reply(profile_info)
    await state.clear()
