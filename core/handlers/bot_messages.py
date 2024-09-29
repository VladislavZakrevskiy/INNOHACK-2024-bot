import psycopg2
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from core.utils.states import Start
from core.keyboards import reply, inline
from config_reader import config
from core.data.database import DataBase
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


HOST = config.host.get_secret_value()
USER = config.user.get_secret_value()
PASSWORD = config.password.get_secret_value()
USER_DB_NAME =config.user_db_name.get_secret_value()
PROJECTS_DB_NAME = config.projects_db_name.get_secret_value()
PORT = config.port.get_secret_value()
CURRENT_USER = None


router = Router()

db = DataBase(host=HOST, user=USER, password=PASSWORD, user_db=USER_DB_NAME, project_db=PROJECTS_DB_NAME, port=PORT)

async def check_deadline(bot: Bot):
    user_connection = await db.connect_user()
    project_connection = await db.connect_project()

    with user_connection.cursor() as cursor:
        cursor.execute("""SELECT telegram_id FROM users""")
        telegram_id = cursor.fetchall()
        for id in telegram_id:
            id = id[0]
            if id != None:
                await db.update_tasks_data(id, user_connection, project_connection)
                db.data = sorted(db.data, key=lambda x: x[1][0][-2], reverse=True)
                if db.data != None:  
                    for i in range(min(len(db.data), db.data_check_count)):
                        diff = db.data[i][1][0][-2] - datetime.now()
                        diff = diff.total_seconds()
                        hours = divmod(diff, 3600)[0]
                        print(hours)
                        if 0 <= hours <= db.data_time_to_end:
                            await bot.send_message(id, text="🔔Напоминаю о задаче товарищ!🔔")
                            await print_task(db.data[i], message=None, num_task=i, id=id, bot=bot)
    await db.disconnect(user_connection)
    await db.disconnect(project_connection)

async def get_user_info(message):
    connection = await db.connect_user()
    connection.autocommit = True
    id = str(message.from_user.id)
    # the cursor for performing database
    username, fullname = await db.get_user(id, connection)
    await db.disconnect(connection)
    return username, fullname


async def print_task(el: tuple, message: Message = None, num_task: int = 0, id: str = None, bot: Bot = None):
    task = el[1]
    day_left = task[0][-1]
    deadline_data = ''
    if day_left == "None":
        deadline_data = f"✅Нет дэдлайна✅"
    elif int(day_left) == 0:
        deadline_data = "⚠️СЕГОДНЯ⚠️"
    elif int(day_left) > 0:
        deadline_data = f"⚠️Осталось дней: {day_left}⚠️"
    
    if message != None and deadline_data != '':
        await message.answer(f"🛠️<b>{task[1]}</b>:\n\n📅Дэдлайн: {str(task[0][1]).zfill(2)}.{str(task[0][2]).zfill(2)} до {str(task[0][3]).zfill(2)}:{str(task[0][4]).zfill(2)}  {deadline_data}\n\n💬{task[3]}\n\n🗣️Руководитель: <b>{task[2][0]}</b>", reply_markup=inline.get_more_inline_keyboard(num_task=num_task))
    elif bot != None and deadline_data != '':
        await bot.send_message(id, text=f"🛠️<b>{task[1]}</b>:\n\n📅Дэдлайн: {str(task[0][1]).zfill(2)}.{str(task[0][2]).zfill(2)} до {str(task[0][3]).zfill(2)}:{str(task[0][4]).zfill(2)}  {deadline_data}\n\n💬{task[3]}\n\n🗣️Руководитель: <b>{task[2][0]}</b>", reply_markup=inline.get_more_inline_keyboard(num_task=num_task))


async def print_tasks(data: list, message: Message):
    db.data = sorted(db.data, key=lambda x: x[1][-2], reverse=True)
    user_fullname = data[0][0]
    await message.answer(f"{user_fullname}, вот твои текущие задачи⬇️", reply_markup=reply.main)
    for i, el in enumerate(data):
        await print_task(el, message, i)
        


@router.message(Command('start'))   
async def start(message: Message, state: FSMContext):
    username, fullname = await get_user_info(message)
    if fullname == None:
        await state.set_state(Start.login)
        await message.answer(f"👋 Привет товарищ! Твой телеграм не привязан к аккаунту Комитета. Пришли свой <b>Пропуск</b>")
    else:
        await state.clear()
        await message.answer(f"👋 Привет, <b>{fullname}</b>. Этот бот будет напоминать тебе о твоих задачах. Приступай к работе товарищ!", reply_markup=reply.main)


@router.message(Start.login)
async def login(message: Message, state: FSMContext):
    username = message.text
    connection = await db.connect_user()
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(
                """SELECT username, full_name FROM users WHERE username = %s;""", (username,)
            )
        user = cursor.fetchone()
    if user == None:
        await message.answer(f"Такого рабочего не существует")
    else:
        await db.update_user(username, str(message.from_user.id), connection)
        await state.clear()
        await message.answer(f"Пропуск успешно установлен.")
        await message.answer(f"👋 Привет, <b>{user[1]}</b>. Этот бот будет напоминать тебе о твоих задачах. Приступай к работе товарищ!", reply_markup=reply.main)
        


@router.message()
async def main_menu(message: Message, state: FSMContext):
    msg = message.text.lower()
    if msg == "🛠️мои задачи":
        user_connection = await db.connect_user()
        project_connection = await db.connect_project()

        await db.update_tasks_data(str(message.from_user.id), user_connection, project_connection)

        await db.disconnect(user_connection)
        await db.disconnect(project_connection)

        if db.data == []:
            await message.answer("У тебя нет задач", reply_markup=reply.main)
        else:
            await print_tasks(db.data, message)
    elif msg == "👤сменить пропуск":
        await state.set_state(Start.login)
        await message.answer("Отправьте новый <b>Пропуск</b>")
    elif msg == "💳мой пропуск":
        username, fullname = await get_user_info(message)
        await message.answer(f"<b>Имя -></b> {fullname}\n<b>Пропуск -></b> {username}", reply_markup=reply.main)
    
