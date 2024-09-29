from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛠️Мои задачи"),
            KeyboardButton(text="💬Уведомления"),
        ],
        [
            KeyboardButton(text="👤Сменить пропуск"),
            KeyboardButton(text="💳Мой пропуск"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Береги рабочую минуту!",
    
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛠️Мои задачи"),
        ],
        [
            KeyboardButton(text="👤Сменить пропуск"),
            KeyboardButton(text="💳Мой пропуск"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Береги рабочую минуту!",
    
)


rmk = ReplyKeyboardRemove()