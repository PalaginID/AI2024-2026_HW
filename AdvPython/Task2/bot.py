import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers.basic import router as start_router
from handlers.setting_profile import router as profile_router
from handlers.loggers import router as loggers_router
from middlewares import LoggingMiddleware

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start_router)
dp.include_router(profile_router)
dp.include_router(loggers_router)
dp.message.middleware(LoggingMiddleware())


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())