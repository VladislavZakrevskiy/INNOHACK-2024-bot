from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мои задачи"),
        ],
        [
            KeyboardButton(text="Сменить пропуск"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Береги рабочую мину",
    
)

rmk = ReplyKeyboardRemove()