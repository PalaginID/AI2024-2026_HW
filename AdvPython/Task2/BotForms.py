from aiogram.fsm.state import State, StatesGroup


class UserProfile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    temperature = State()
    water_goal = State()
    calories_goal = State()


class Food(StatesGroup):
    name = State()
    energy = State()
    product_weight = State()