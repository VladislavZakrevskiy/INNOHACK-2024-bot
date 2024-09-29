from aiogram import Router, F
from aiogram.types import CallbackQuery
from core.utils.callback import ProjectDetails
from core.keyboards.inline import get_details_inline_keyboard, get_more_inline_keyboard
from core.handlers.bot_messages import db
from config_reader import config

router = Router()


@router.callback_query(ProjectDetails.filter(F.action == "more"))
async def details(call: CallbackQuery, callback_data: ProjectDetails):
    text = call.message.text
    await call.message.edit_text(text, reply_markup=get_details_inline_keyboard(callback_data.num_task))
    await call.answer()   
    
@router.callback_query(ProjectDetails.filter(F.action == "status"))
async def details(call: CallbackQuery, callback_data: ProjectDetails):
    text = call.message.text
    if db.data != [] and "⏱️Статус:" not in text:
        status = db.data[callback_data.num_task][2]
        await call.message.edit_text(f"{text}\n\n⏱️Статус: {status}", reply_markup=get_details_inline_keyboard(callback_data.num_task))
    await call.answer()

@router.callback_query(ProjectDetails.filter(F.action == "space"))
async def details(call: CallbackQuery, callback_data: ProjectDetails):
    text = call.message.text
    if db.data != [] and "📦Пространство:" not in text and "🗣️Руководитель пространства:" not in text:
        space = db.data[callback_data.num_task][3]
        await call.message.edit_text(f"{text}\n\n📦Пространство: {space[0]}\n🗣️Руководитель пространства: {space[1][0]}\n", reply_markup=get_details_inline_keyboard(callback_data.num_task))
    await call.answer()

@router.callback_query(ProjectDetails.filter(F.action == "project"))
async def details(call: CallbackQuery, callback_data: ProjectDetails):
    text = call.message.text
    if db.data != [] and "📓Проект:" not in text and "🗣️Руководитель проекта:" not in text:
        project = db.data[callback_data.num_task][4]

        await call.message.edit_text(f"{text}\n\n📓Проект: {project[0]}\n🗣️Руководитель проекта: {project[2][0]}\n", reply_markup=get_details_inline_keyboard(callback_data.num_task))
    await call.answer()

@router.callback_query(ProjectDetails.filter(F.action == "hide"))
async def details(call: CallbackQuery, callback_data: ProjectDetails):
    text = call.message.text

    await call.message.edit_text(text, reply_markup=get_more_inline_keyboard(callback_data.num_task))
    await call.answer()