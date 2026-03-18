from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Главное меню после /start
def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Найти музыку", callback_data="btn_music")],
        [InlineKeyboardButton(text="🎬 Найти фильм", callback_data="btn_movie")]
    ])
    return keyboard


# Кнопка "Назад"
def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="btn_back")]
    ])
    return keyboard