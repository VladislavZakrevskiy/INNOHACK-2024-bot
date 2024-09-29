from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.utils.callback import ProjectDetails
from core.handlers.bot_messages import db
from config_reader import config

SITE_URL = config.site_url.get_secret_value()

def get_more_inline_keyboard(num_task):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(text="Подробнее", callback_data=ProjectDetails(action="more", num_task=num_task).pack())
        )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

def get_details_inline_keyboard(num_task):
    if db.data != []:
        link = f"http://{SITE_URL}/task/{db.data[num_task][1][-1]}"
        print(link)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(
        InlineKeyboardButton(text="Статус задачи", callback_data=ProjectDetails(action="status", num_task=num_task).pack()),
        )
    keyboard_builder.add(InlineKeyboardButton(text="Пространство задачи", callback_data=ProjectDetails(action="space", num_task=num_task).pack()))
    keyboard_builder.add(InlineKeyboardButton(text="Проект задачи", callback_data=ProjectDetails(action="project", num_task=num_task).pack()))
    # keyboard_builder.add(InlineKeyboardButton(text="Ссылка на задачу", url=link))
    keyboard_builder.add(InlineKeyboardButton(text="Скрыть", callback_data=ProjectDetails(action="hide", num_task=num_task).pack()))
    keyboard_builder.adjust(1, 1, 1, 1)
    return keyboard_builder.as_markup()