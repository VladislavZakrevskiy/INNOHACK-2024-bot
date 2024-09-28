from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from utils.states import Start
from keyboards import reply
import psycopg2
from config_reader import config

HOST = config.host.get_secret_value()
USER = config.user.get_secret_value()
PASSWORD = config.password.get_secret_value()
USER_DB_NAME =config.user_db_name.get_secret_value()
PROJECTS_DB_NAME = config.projects_db_name.get_secret_value()
PORT = config.port.get_secret_value()

router = Router()



@router.message(Command('start'))   
async def start(message: Message, state: FSMContext):
    connection = psycopg2.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=USER_DB_NAME,
    port=PORT
    )
    connection.autocommit = True
    id = str(message.from_user.id)
    # the cursor for performing database
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT full_name FROM users WHERE telegram_id = %s;""", (id,)
        )
        fullname = cursor.fetchone()
        connection.close()
        print("[INFO] PostgreSQL connection closed")
        if fullname == None:
            await state.set_state(Start.login)
            await message.answer(f"👋 Привет товарищ! Твой телеграм не привязан к аккаунту Комитета. Пришли свой <b>Пропуск</b>")
        else:
            await state.clear()
            await message.answer(f"👋 Привет, <b>{fullname[0]}</b>. Этот бот будет напоминать тебе о твоих задачах. Приступай к работе товарищ!", reply_markup=reply.main)



@router.message(Start.login)
async def login(message: Message, state: FSMContext):
    connection = psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=USER_DB_NAME,
        port=PORT
    )
    connection.autocommit = True
    username = message.text
    id = str(message.from_user.id)
    with connection.cursor() as cursor:
        cursor.execute(
                """SELECT username, full_name FROM users WHERE username = %s;""", (username,)
            )
        user = cursor.fetchone()
        if user == None:
            await message.answer(f"Такого рабочего не существует")
        else:
            cursor.execute(
                """SELECT username FROM users WHERE telegram_id = %s;""", (id,)
            )
            old_id = cursor.fetchone()
            if old_id == None:
                cursor.execute(
                    """UPDATE users SET telegram_id = %s WHERE username = %s""", (id, username,)
                )
            else:
                cursor.execute(
                    """UPDATE users SET telegram_id = %s WHERE telegram_id = %s""", (None, id,)
                )
                cursor.execute(
                    """UPDATE users SET telegram_id = %s WHERE username = %s""", (id, username,)
                )
            await state.clear()
            connection.close()
            print("[INFO] PostgreSQL connection closed")
            await message.answer(f"Пропуск успешно установлен.")
            await message.answer(f"👋 Привет, <b>{user[1]}</b>. Этот бот будет напоминать тебе о твоих задачах. Приступай к работе товарищ!", reply_markup=reply.main)

