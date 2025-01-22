import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers import basic, setting_profile

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(basic.router, setting_profile.router)


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())