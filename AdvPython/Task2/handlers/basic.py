from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (f"Добро пожаловать, {message.from_user.username}! \n"
                    "Предлагаю начать с заполнения профиля!\n"
                    "Для этого воспользуйся командой /set_profile\n"
                    "О других моих функцих можно узнать с помощью /help"
                    )
    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = ("Вы можете воспользоваться следующими командами:\n"
                 "/set_profile - задать или поменять параметры Вашего профиля\n"
                 "/log_water <количество в мл.> - записать количество выпитой воды\n"
                 "/log_food <название еды> - подсчитать и записать количество съеденной еды\n"
                 "/log_workout <вид тренировки> <время в мин.> - подсчитать и записать сожженные калории\n"
                 "Доступны следующие виды: прогулка, футбол, баскетбол, бег, плавание, йога, спортзал и велосипед\n"
                 "/check_progress - посмотреть прогресс выполнения дневных норм воды и калорий\n")
    await message.answer(help_text)