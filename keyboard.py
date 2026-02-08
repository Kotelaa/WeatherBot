from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def main_kb():
    """Main menu keyboard"""
    kb = [
        [KeyboardButton(text='Команды')],
        [KeyboardButton(text='Описание бота')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard