from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from setting_profile import users
from BotForms import Food


router = Router()


def get_water_bar(goal, current):
    fig = go.Figure(data=[
        go.Bar(name='Цель', x=['Вода, мл.'], y=[goal], marker_color='lightblue'),
        go.Bar(name='Сделано', x=['Вода, мл.'], y=[current], marker_color='blue')
    ])
    fig.update_layout(title_text='Прогресс по достижению нормы воды', barmode='overlay')
    fig.write_image("images/water_progress.png")


def get_calorie_bar(goal, current):
    fig = go.Figure(data=[
        go.Bar(name='Цель', x=['Калории, ккал.'], y=[goal], marker_color='lightblue'),
        go.Bar(name='Сделано', x=['Калории, ккал.'], y=[current], marker_color='blue')
    ])
    fig.update_layout(title_text='Прогресс по достижению нормы калорий', barmode='overlay')
    fig.write_image("images/calorie_progress.png")


def get_water_calorie_bar(water_goal, water_current, calorie_goal, calorie_current):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Прогресс по задачам", "Оставшиеся задачи"))

    fig.add_trace(go.Bar(name='Норма воды', x=['Вода, мл.'], y=[water_goal], marker_color='lightblue'), row=1, col=1)
    fig.add_trace(go.Bar(name='Выпито воды', x=['Вода, мл.'], y=[water_current], marker_color='blue'), row=1, col=1)
    fig.add_trace(go.Bar(name='Норма калорий', x=['Калории, ккал.'], y=[calorie_goal], marker_color='lightred'), row=1, col=2)
    fig.add_trace(go.Bar(name='Получено калорий', x=['Калории, ккал.'], y=[calorie_current], marker_color='red'), row=1, col=2)

    fig.update_layout(title_text="Прогресс",barmode='overlay')
    fig.write_image("images/water_calorie_progress.png")


def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:
            return products[0]['nutriments']['energy-kcal_100g']
        return None
    print(f"Ошибка: {response.status_code}")
    return None


def workout(activity, duration, weight):
    workout_met = {
        'прогулка': 3.0,
        'футбол': 10.3,
        'баскетбол'
        'бег': 11.2,
        'велосипед': 6.0,
        'плавание': 10.0,
        'йога': 3.3,
        'спортзал': 6.0
    }
    met = workout_met[activity]
    return round((met * weight * duration * 3.5) / 200)


@router.message(Command("log_water"))
async def log_water(message: Message, command: CommandObject):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return
    try:
        users[user_id]['logged_water'] += float(command.args)
        report = ("Ваш прогресс:\n"
              f"Выпито: {users[user_id]['logged_water']} мл. из {users[user_id]['water_goal']} мл.\n"
              f"Осталось: {max(0, users[user_id]['water_goal']-users[user_id]['logged_water'])} мл."  
        )
        get_water_bar(users[user_id]['water_goal'], users[user_id]['logged_water'])
        await message.answer_photo(FSInputFile("images/water_progress.png"), caption=report)
    except ValueError:
        await message.answer("Используйте формат: /log_water <количество в мл.>")


@router.message(Command("log_food"))
async def log_food(message: Message, command: CommandObject, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return
    try:
        product = command.args
        await state.set_state(Food.name)
        await state.update_data(name=product)
        energy = get_food_info(product)
        await state.set_state(Food.energy)
        await state.update_data(energy=energy)
        await message.reply(f"{product} - {energy} ккал. на 100 г. Сколько грамм вы съели?")
        await state.set_state(Food.product_weight)
    except ValueError:
        await message.answer("Используйте формат: /log_food <название продукта>")


@router.message(Food.product_weight)
async def proccess_product_weight(message: Message, state: FSMContext):
    await state.update_data(product_weight=float(message.text))
    data = await state.get_data()
    await state.clear()
    user_id = message.from_user.id
    users[user_id]['logged_calories'] += float(data['energy']*data['product_weight']/100)
    caption = ("Ваш прогресс:\n"
               f"{data['name']}: {data['energy']*data['product_weight']/100} ккал.\n"
               f"За сегодня: {users[user_id]['logged_calories']} ккал. из {users[user_id]['calories_goal']} ккал.\n"
               f"Осталось: {max(0, users[user_id]['calories_goal']-users[user_id]['logged_calories'])} ккал."  
              )
    get_calorie_bar(users[user_id]['calories_goal'], users[user_id]['logged_calories'])
    await message.answer_photo(FSInputFile("images/calorie_progress.png"), caption=caption)


@router.message(Command('log_workout'))
async def log_workout(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return
    try:
        _, activity, duration = message.text.split()
        calories_burned = workout(activity, duration, users[user_id]['weight'])
        water = (duration // 30) * 200
        users[user_id]['logged_water'] += water
        users[user_id]['burned_calories'] += calories_burned
        await message.answer(f"Тренировка добавлена: {activity}, {duration} мин.\n"
                             f"Сожжено калорий: {calories_burned} ккал\n"
                             f"Дополнительно выпито воды: {water} мл")
    except ValueError:
        await message.answer("Используйте формат: /log_workout <тип тренировки> <время (мин)>")


@router.message(Command('check_progress'))
async def check_progress(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль с помощью /set_profile.")
        return
    calorie_balance = users[user_id]['logged_calories']-users[user_id]['burned_calories']
    caption = (f"Прогресс:\n"
               f"Вода:\n"
               f"Выпито:{users[user_id]['logged_water']} мл. из {users[user_id]['water_goal']} мл.\n"
               f"Осталось:{max(0, users[user_id]['water_goal']-users[user_id]['logged_water'])} мл.\n\n"
               f"Калории:\n"
               f"Потреблено:{users[user_id]['logged_calories']} ккал из {users[user_id]['calories_goal']} ккал\n"
               f"Сожжено:{users[user_id]['burned_calories']} ккал\n"
               f"Баланс:{calorie_balance} ккал\n")

    get_water_calorie_bar(users[user_id]['water_goal'], users[user_id]['logged_water'], users[user_id]['calories_goal'], calorie_balance)
    await message.answer_photo(FSInputFile("images/water_calorie_progress.png"), caption=caption)

