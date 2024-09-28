import psycopg2
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from utils.states import Start
from config_reader import config
import datetime

HOST = config.host.get_secret_value()
USER = config.user.get_secret_value()
PASSWORD = config.password.get_secret_value()
USER_DB_NAME =config.user_db_name.get_secret_value()
PROJECTS_DB_NAME = config.projects_db_name.get_secret_value()
PORT = config.port.get_secret_value()

router = Router()

async def list_projects(telegram_id, message):
    users_connection = psycopg2.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=USER_DB_NAME,
    port=PORT
    )

    with users_connection.cursor() as cursor:
        cursor.execute(
            """SELECT id, full_name FROM users WHERE telegram_id = %s;""", (telegram_id,)
        )
        (user_id, user_fullname) = cursor.fetchone()

    projects_connection = psycopg2.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=PROJECTS_DB_NAME,
    port=PORT
    )

    with projects_connection.cursor() as cursor:
        cursor.execute(
            """SELECT owner_id, create_date, deadline_date, description, title, status_id FROM task WHERE executor_id = %s;""", (user_id,)
        )
        tasks = cursor.fetchall()
        for task in tasks:
            (task_owner_id, task_create_date, task_deadline_date, task_description, task_title, task_status_id) = task
            with users_connection.cursor() as users_cursor:
                users_cursor.execute(
                """SELECT full_name FROM users WHERE id = %s;""", (task_owner_id,)
                )
                task_owner_fullname = users_cursor.fetchone()
                print(task_deadline_date.time())
            await message.answer(f"🛠️<b>{task_title}</b>:\n\n📅До {task_deadline_date.date()}\n\n💬{task_description}\n🗣️Руководитель: <b>{task_owner_fullname[0]}</b>")

    
    projects_connection.close()
    users_connection.close()
    print("[INFO] PostgreSQL connection closed")


@router.message()
async def main_menu(message: Message, state: FSMContext):
    msg = message.text.lower()
    print(msg)
    if msg == "мои задачи":
        await list_projects(str(message.from_user.id), message)
    elif msg == "сменить пропуск":
        await state.set_state(Start.login)
        await message.answer("Отправьте новый <b>Пропуск</b>")
    