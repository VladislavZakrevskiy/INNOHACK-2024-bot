from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from utils.states import Start

router = Router()

@router.message(Command("start"))   
async def start(message: Message, state: FSMContext):
    #TODO проверка пользователя, обращение к базе данных, если его нет, попросить авторизоваться
    await state.set_state(Start.login)
    await message.answer(f"👋 Привет, <b>{message.from_user.username}</b>, этот бот поможет тебе организовать твою работу над проектами. Пришли свой логин, чтобы привязать аккаунт.")

@router.message(Start.login)
async def login(message: Message, state: FSMContext):
    #TODO проверка пользователя, обращение к базе данных
    user_name = message.text
    await message.answer(f"Успешная авторизация")