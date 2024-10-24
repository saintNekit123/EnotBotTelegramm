from telebot import types

def create_phone_keyboard() -> types.ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой для отправки номера телефона."""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(button_phone)
    return keyboard

def create_send_exit_keyboard() -> types.ReplyKeyboardMarkup:
    """Создать клавиатуру с кнопками отправки Прислать чек и Выход"""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    send_cheque = types.KeyboardButton(text="Прислать чек")
    exit = types.KeyboardButton(text="Выход")
    keyboard.add(send_cheque, exit)
    return keyboard