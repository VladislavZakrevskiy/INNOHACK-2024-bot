from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мои задачи"),
            KeyboardButton(text="Ссылки"),
        ],
        [
            KeyboardButton(text="Калькулятор"),
            KeyboardButton(text="Спец кнопки"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="дэдлайны горят",
    
)

rmk = ReplyKeyboardRemove()