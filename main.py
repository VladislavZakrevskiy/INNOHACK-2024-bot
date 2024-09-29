import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from config_reader import config
from core.handlers import bot_messages, callback
from core.utils.commands import set_commands
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
from core.handlers.bot_messages import db


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(1008265857, text="<strong>Бот запущен!</strong>")

async def stop_bot(bot: Bot):
    await bot.send_message(1008265857, text="<strong>Бот остановлен!</strong>")

async def start():
    # logging.basicConfig(level=logging.INFO,
    #                     format="%(asctime)s - [%(levelname)s] - %(name)s - "
    #                     "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)"
    #                     )
    bot = Bot(config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(bot_messages.check_deadline, trigger="cron", hour=db.data_check_hour, minute=db.data_check_minute, kwargs={"bot": bot})
    scheduler.start()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(
        bot_messages.router,
        callback.router
        
    )
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
         
if __name__ == "__main__":
    asyncio.run(start())
