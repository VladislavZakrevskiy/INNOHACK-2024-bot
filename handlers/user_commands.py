from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from utils.states import Start
import psycopg2
from config_reader import config

HOST = config.host.get_secret_value()
USER = config.user.get_secret_value()
PASSWORD = config.password.get_secret_value()
USER_DB_NAME =config.user_db_name.get_secret_value()
PROJECTS_DB_NAME = config.projects_db_name.get_secret_value()
PORT = config.port.get_secret_value()

router = Router()

@router.message(Command("start"))   
async def start(message: Message, state: FSMContext):
    try:
        # connect to exist database
        connection = psycopg2.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=USER_DB_NAME,
            port=PORT
        )

        # the cursor for performing database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT version"
            )
            print(f"Server version: {cursor.fetchone()}")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")
    await state.set_state(Start.login)
    await message.answer(f"👋 Привет, <b>{message.from_user.username}</b>, этот бот поможет тебе организовать твою работу над проектами. Пришли свой логин, чтобы привязать аккаунт.")

@router.message(Start.login)
async def login(message: Message, state: FSMContext):
    #TODO проверка пользователя, обращение к базе данных
    user_name = message.text
    await message.answer(f"Успешная авторизация")