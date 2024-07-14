import asyncio

from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database import create_tables

from config import TOKEN

async def main():
    # create_tables()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    
    try:
        asyncio.run(main())
    except:
        print('Exit')