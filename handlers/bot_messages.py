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

async def list_projects(telegram_id: str, message: Message) -> list:
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

        # получение задач
        cursor.execute(
            """SELECT owner_id, create_date, deadline_date, description, title, status_id FROM task WHERE executor_id = %s;""", (user_id,)
        )
        tasks = cursor.fetchall()

        # получение информации о каждой задаче

        for task in tasks:
            (task_owner_id, task_create_date, task_deadline_date, task_description, task_title, task_status_id) = task
            day = task_deadline_date.date().day
            month = task_deadline_date.date().month
            hour = task_deadline_date.time().hour
            minute = task_deadline_date.time().minute
            day_left = (datetime.datetime.now() - task_deadline_date).days

            #получение информации о статусе задачи

            cursor.execute(
            """SELECT name, space_id FROM status WHERE id = %s;""", (task_status_id,)
            )
            (status_name, space_id) = cursor.fetchone()

            #получение информации о space, в котором лежит задача

            cursor.execute(
            """SELECT owner_id, description, name, project_id FROM space WHERE id = %s;""", (space_id,)
            )
            (space_owner_id, space_description, space_name, project_id) = cursor.fetchone()

            # получение информации о проекте, в котором находится space

            cursor.execute(
            """SELECT owner_id, description, image, name FROM project WHERE id = %s;""", (project_id,)
            )
            (project_owner_id, project_description, project_image, project_name) = cursor.fetchone()
            
            #USER DATABASE Получение имен владельцев
            with users_connection.cursor() as users_cursor:
                users_cursor.execute(
                """SELECT full_name FROM users WHERE id = %s;""", (task_owner_id,)
                )
                task_owner_fullname = users_cursor.fetchone()
                users_cursor.execute(
                """SELECT full_name FROM users WHERE id = %s;""", (space_owner_id,)
                )
                space_owner_fullname = users_cursor.fetchone()
                users_cursor.execute(
                """SELECT full_name FROM users WHERE id = %s;""", (project_owner_id,)
                )
                project_owner_fullname = users_cursor.fetchone()

                data = (
                    user_fullname,
                    ((task_create_date, day, month, hour, minute, day_left), task_title, task_owner_fullname, task_description),
                    (status_name),
                    (space_name, space_owner_fullname, space_description),
                    (project_name, project_image, project_owner_fullname, project_description)
                    
                    )
                if day_left == 0:
                    deadline_data = "⚠️СЕГОДНЯ⚠️"
                else:
                    deadline_data = f"⚠️Осталось дней: {day_left}⚠️"
            await message.answer(f"🛠️<b>{task_title}</b>:\n\n📅Дэдлайн: {day}.{month} до {hour}:{minute}  {deadline_data}\n\n💬{task_description}\n\n🗣️Руководитель: <b>{task_owner_fullname[0]}</b>")

    
    projects_connection.close()
    users_connection.close()
    print("[INFO] PostgreSQL connection closed")
    return data






@router.message()
async def main_menu(message: Message, state: FSMContext):
    msg = message.text.lower()
    print(msg)
    if msg == "мои задачи":
        data = await list_projects(str(message.from_user.id), message)
    elif msg == "сменить пропуск":
        await state.set_state(Start.login)
        await message.answer("Отправьте новый <b>Пропуск</b>")
    