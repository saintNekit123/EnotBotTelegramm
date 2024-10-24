import telebot
import os
import time
import requests
import logging
import atexit


from config import api_key, directory, chat_support
from telebot import apihelper
from botCheck import checkFIO, check_18, validate_phone, decoding, check_Cheque, create_button
from datetime import date
from user import User
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

uid = os.environ
is_waiting_for_date = {}
bot = telebot.TeleBot(api_key)

direct = directory
CHAT_ID = None
PHOTO_PATH = os.path.join(direct, 'downloaded_photo.png')
CONVERTED_PHOTO_PATH = os.path.join(direct, 'converted_photo.png')
LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

"""Допл-функции"""

# Функция вывода тех-поддержки
@bot.message_handler(commands=["help"])
def help_command(message: types.Message):
    bot.send_message(message.chat.id, "t.me/KujiraKit +7 (987) 536-06-52 - Никита")

# Функция вывода номер телефона магазина 
@bot.message_handler(commands=["shop"])
def shop_command(message: types.Message):
    bot.send_message(message.chat.id, "8 (963) 379-09-99 - Магазины Enot Hookah Market")

# Функция проверки ввода команды
def check_command(message):
    
    if message.text.startswith('/'):
        # Обработка команды /help
        if message.text == '/help':
            help_command(message)
        # Обработка команды /shop
        elif message.text == '/shop':
            shop_command(message)
        else:
            return False
        return


"""Основной код"""
@bot.message_handler(commands=["start"])
def start_main(message: types.Message):

    user = User.get_user(message.from_user.id)
    user_id = message.from_user.id
    global CHAT_ID
    CHAT_ID = message.chat.id
    user_name = message.from_user
    user_link = f"https://t.me/{user_name.username}"
    user.linkT = user_link
    
    # Отправка приветственного сообщения
    bot.send_message(message.chat.id, "Привет! Хотите принять участие в Розыгрыше? \nВведите Вашу дату рождения в календаре.")
    time.sleep(2)
    
    # Устанавливаем флаг ожидания даты
    is_waiting_for_date[user_id] = True
    # Генерация и отправка календаря
    set_calendar(message)

def set_calendar(m):
    user_id = m.from_user.id

    # Генерируем и отправляем календарь пользователю
    calendar, step = DetailedTelegramCalendar(locale='ru', first_step="y",  min_date=date(1950, 1, 1), 
                                              max_date=date(2007, 12, 31), current_date=date(1960, 1, 1)).build()
    bot.send_message(m.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)

    # Устанавливаем флаг, что ожидаем выбор даты
    is_waiting_for_date[user_id] = True
    
 
@bot.callback_query_handler(func=lambda call: is_waiting_for_date.get(call.from_user.id))
def handle_calendar(call):
    user_id = call.message.from_user.id

    # Получаем выбор пользователя
    result, key, step = DetailedTelegramCalendar(locale='ru').process(call.data)

    if not result and key:
        # Если дата еще не выбрана (пользователь делает выбор), обновляем календарь
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        if check_18.check_BD(result) < 18:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            is_waiting_for_date.pop(user_id, None)  # Снимаем флаг ожидания даты
            bot.send_message(call.message.chat.id, "Вам еще нет 18 лет. К сожалению, Вы НЕ можете принять участие в Розыгрыше. Для перезапуска введите команду /start")
            time.sleep(1)
            return  # Завершение функции, чтобы не продолжать
        else:
            # Когда дата выбрана, отправляем сообщение с результатом
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "Отлично! Давайте знакомиться🥰 Как вас зовут? <i>Напишите Ваше Имя и Фамилию</i>:", parse_mode="HTML")
            
            # Регистрируем обработчик следующего шага (ввод имени), используем объект call.message для регистрации
            bot.register_next_step_handler(call.message, set_FIO_user)
            
            # Убираем флаг ожидания даты
            is_waiting_for_date.pop(user_id, None)
            
@bot.message_handler(func=lambda message: is_waiting_for_date.get(message.from_user.id, False), content_types=['text'])
def handle_text_input(message: types.Message):
    if message.text.startswith('/'):
        if message.text == '/start':
            bot.clear_step_handler_by_chat_id(message.chat.id)
            start_main(message)
            return
        elif check_command(message) == False:
            bot.send_message(message.chat.id, "Неизвестная команда! \nПожалуйста, выбирайте дату только через календарь.")
    bot.send_message(message.chat.id, "Пожалуйста, выбирайте дату только через календарь. Нажмите на календарь для выбора даты.")

@bot.message_handler(func=lambda message: is_waiting_for_date.get(message.from_user.id, False), content_types=['photo', 'video', 'audio', 'document', 
                                                                                                               'sticker', 'voice', 'video_note', 'location', 
                                                                                                               'contact', 'venue', 'poll', 'dice', 'new_chat_members', 
                                                                                                               'left_chat_member', 'new_chat_title', 'new_chat_photo', 
                                                                                                               'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 
                                                                                                               'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 
                                                                                                               'pinned_message'])
def handle_other_media(message: types.Message):
    bot.send_message(message.chat.id, "Пожалуйста, используйте календарь для выбора даты.")

@bot.message_handler(content_types="text")
def set_FIO_user(message: types.Message) -> None:
    """
    Функция проверяет и записывает в БД Имя пользователя.
    """

    user_message = message.text
    user = User.get_user(message.from_user.id)

    if message.content_type != "text":
        bot.send_message(message.chat.id, "Я не могу понять что вы написали😔, \nмне хотелось бы узнать как Вас зовут🙂")
        bot.register_next_step_handler(message, set_FIO_user)
    
    # Проверка на команду (если сообщение начинается с "/")
    elif user_message.startswith('/'):
        if message.text == '/start':
            bot.clear_step_handler_by_chat_id(message.chat.id)
            start_main(message)
            return
        elif check_command(message) == False:
            bot.send_message(message.chat.id, "Неизвестная команда! \nМне хотелось бы узнать как вас зовут:")
            bot.register_next_step_handler(message, set_FIO_user)
    
        user.id = message.from_user.id
        

    else:
        if not message.text.strip():
            bot.send_message(message.chat.id, "Напишите Ваше Имя и Фамилию🙂")
            bot.register_next_step_handler(message, set_FIO_user)
        else:
            if not checkFIO.is_full_name(message.text):  # Проверка на полное ввод данных
                bot.send_message(message.chat.id, "Возможно вы допустили ошибку😔 \nПопробуйте еще раз🙂") 
                bot.register_next_step_handler(message, set_FIO_user)
            else:
                user.fullname = user_message.title()
                bot.send_message(message.chat.id, "Осталось всего 2 шага🥳 \nПожалуйста, укажите Ваш номер телефона. Введите его в формате +79ХХХХХХХХХ или нажмите на кнопку «Отправить номер телефона».", reply_markup=create_button.create_phone_keyboard())           
                bot.register_next_step_handler(message, set_number_phone)

@bot.message_handler(content_types=['text', 'contact'])
def set_number_phone(message: types.Message) -> None:
    user = User.get_user(message.from_user.id)

    # Проверка на текстовое сообщение
    if message.content_type == 'text':
        if message.text.startswith('/'):
            if message.text == '/start':
                bot.clear_step_handler_by_chat_id(message.chat.id)
                start_main(message)
                return
            elif check_command(message) == False:
                create_button.create_phone_keyboard()
                bot.send_message(message.chat.id, "Неизвестная команда! \nПожалуйста, введите номер телефона или отправьте мне его.")
                bot.register_next_step_handler(message, get_photo_qr)
            else:
                create_button.create_phone_keyboard()
                bot.send_message(message.chat.id, "Теперь пришлите мне Ваш номер телефона:")
                bot.register_next_step_handler(message, get_photo_qr)
                return

        # Если команда правильная
            create_button.create_phone_keyboard()
            bot.send_message(message.chat.id, "Теперь введите номер телефона или отправьте мне его:")
            bot.register_next_step_handler(message, set_number_phone)
            return

        if message.text:  # Проверяем, что текст не пустой
            if validate_phone.validate_phone_number(message.text):
                user.phone = message.text
                bot.send_message(message.chat.id, "Телефон введен верно!")
                time.sleep(1)
                bot.send_message(message.chat.id, "Теперь отправьте фото с QR-кодом.")
                bot.register_next_step_handler(message, get_photo_qr)
            else:
                create_button.create_phone_keyboard()
                bot.send_message(message.chat.id, "Возможно вы допустили ошибку😔, \nПопробуйте еще раз🙂 \nНомер телефона должен начинаться с +79 и должен иметь 11 цифр.")
                bot.register_next_step_handler(message, set_number_phone)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, введите номер телефона.")
            bot.register_next_step_handler(message, set_number_phone)

    # Проверка на контакт
    elif message.content_type == "contact":
        if message.contact and hasattr(message.contact, 'phone_number'):  # Проверяем, что контакт есть и у него есть номер
            phone_number = message.contact.phone_number
            user.phone = phone_number
            bot.send_message(message.chat.id, "Телефон введен верно!", reply_markup=types.ReplyKeyboardRemove())
            time.sleep(1)
            bot.send_message(message.chat.id, "Урааа! Последний шаг😍 \nОтправьте фото чека! (QR-код должен быть виден полностью)")
            bot.register_next_step_handler(message, get_photo_qr)
        else:
            bot.send_message(message.chat.id, "Не удалось получить номер телефона. \nПожалуйста, попробуйте снова.")
            create_button.create_phone_keyboard()
            bot.register_next_step_handler(message, set_number_phone)

    # Если не текст и не контакт
    else:
        bot.send_message(message.chat.id, "Произошла ошибка! \nПожалуйста, введите номер телефона или отправьте мне его:")
        bot.register_next_step_handler(message, set_number_phone)


# Функция для получения и обработки фото с QR-кодом
@bot.message_handler(content_types=['text', 'photo'])
def get_photo_qr(message: types.Message):

    if message.content_type == "text":
        if message.text.startswith('/'):
            if message.text == '/start':
                bot.clear_step_handler_by_chat_id(message.chat.id)
                start_main(message)
                return
            elif check_command(message) == False:
                bot.send_message(message.chat.id, "Неизвестная команда! \nПожалуйста, пришлите мне QR:")
                bot.register_next_step_handler(message, get_photo_qr)
            else:
                bot.send_message(message.chat.id, "Теперь пришлите мне QR:")
                bot.register_next_step_handler(message, get_photo_qr)
                return
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте фото чека! \n(QR-код должен быть виден полностью)")
            bot.register_next_step_handler(message, get_photo_qr)
            return

    if message.content_type == 'photo':
        if len(message.photo) > 4:
            bot.send_message(message.chat.id, "Вы прислали несколько фото. \nПожалуйста, выберите одно и отправьте его мне🙂")
            bot.register_next_step_handler(message, get_photo_qr)
        else:
            # Убедитесь, что папка существует, создайте ее при необходимости
            os.makedirs(directory, exist_ok=True)
                
            # Скачиваем фото
            photo_file = message.photo[-1].file_id
            file_info = bot.get_file(photo_file)
            downloaded_file = bot.download_file(file_info.file_path)

            user = User.get_user(message.from_user.id)
                
            # Сохраняем исходное изображение
            with open(PHOTO_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Конвертируем фото в JPEG
            decoding.convert_image_to_jpeg(PHOTO_PATH, CONVERTED_PHOTO_PATH)
            qr_code = decoding.call_js_qr_scanner(CONVERTED_PHOTO_PATH)
            print(qr_code)
            if "error" in qr_code:
                keyboard = create_button.create_send_exit_keyboard()
                bot.send_message(message.chat.id, "Извините, но произошла какая-то ошибка... \nДавайте попробуем еще раз? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                bot.register_next_step_handler(message, bot_again)
            elif qr_code:  # Если QR найден ->
                decoding.get_response_FNS(qr_code)
                if "https" in qr_code:
                    keyboard = create_button.create_send_exit_keyboard()
                    bot.send_message(message.chat.id, "Не нужно присылать ссылки. Мне нужен чек нашего магазина. Хотите продолжить? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                    bot.register_next_step_handler(message, bot_again)
                elif check_Cheque.find_Cheque(qr_code) == "Дубль":
                    keyboard = create_button.create_send_exit_keyboard()
                    bot.send_message(message.chat.id, "Вы прислали ссылку. Наверно там что-то интересное😁Но мне нужен чек магазина Нашей сети. \nХотите продолжить? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                    bot.register_next_step_handler(message, bot_again)
                elif check_Cheque.find_Cheque(qr_code) == "Просрочен":
                    keyboard = create_button.create_send_exit_keyboard()
                    bot.send_message(message.chat.id, "К сожалению, дата в Вашем чеке не подходит для участия в Розыгрыше😔 \nХотите добавить ещё один чек? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                    bot.register_next_step_handler(message, bot_again)
                elif check_Cheque.find_Cheque(qr_code) == "Меньше 2000":
                    keyboard = create_button.create_send_exit_keyboard()
                    bot.send_message(message.chat.id, "К сожалению, сумма чека не подходит для участия в Розыгрыше😔 Хотите добавить ещё один чек? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                    bot.register_next_step_handler(message, bot_again)
                elif check_Cheque.find_Cheque(qr_code) == "Куплен не в Enot":
                    keyboard = create_button.create_send_exit_keyboard()
                    bot.send_message(message.chat.id, "Чек был выдан не в нашем магазине! 🧐 \nХотите добавить ещё один чек? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                    bot.register_next_step_handler(message, bot_again)
                else:
                    keyboard = create_button.create_send_exit_keyboard()
                    check_Cheque.record_participant(user, qr_code)
                    bot.send_message(message.chat.id, "Поздравляю!!!🥳Чек успешно зарегистрирован, Вы участвуете в Розыгрыше!!! \nХотите добавить ещё один чек? \n'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                    bot.register_next_step_handler(message, bot_again)

            else:
                bot.send_message(message.chat.id, "QR-код не найден на изображении😢 Попробуйте сфотографировать QR-код крупнее.😉")
                bot.register_next_step_handler(message, get_photo_qr)
            
            # Удаляем изображения после обработки
            os.remove(PHOTO_PATH)
            os.remove(CONVERTED_PHOTO_PATH)
    
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фото чека! \n(QR-код должен быть виден полностью)")
        bot.register_next_step_handler(message, get_photo_qr)

# Функция спрашивающая нужно ли загружать ещё один чек?
@bot.message_handler(content_types=['text'])
def bot_again(message):
    if message.content_type == 'text':
        if message.text.startswith('/'):
            if message.text == '/start':
                bot.clear_step_handler_by_chat_id(message.chat.id)
                start_main(message)
                return
            elif check_command(message) == False:
                keyboard = create_button.create_send_exit_keyboard()
                bot.send_message(message.chat.id, "Неизвестная команда! \nМы будет добавлять новый QR-код? 'Прислать чек' или 'Выйти':", reply_markup=keyboard)
                bot.register_next_step_handler(message, bot_again)
            else:
                keyboard = create_button.create_send_exit_keyboard()
                bot.send_message(message.chat.id, "Пожалуйста, отправьте фото чека! \n(QR-код должен быть виден полностью) \n'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                bot.register_next_step_handler(message, bot_again)
                return
        
        if isinstance(message.text, int):
            keyboard = create_button.create_send_exit_keyboard()
            bot.send_message(message.chat.id, "Я Вас не понимаю 😔 \nЕсли нужна помощь, введите /help \n'Прислать чек' или 'Выйти'", reply_markup=keyboard)
            bot.register_next_step_handler(message, bot_again)
        elif isinstance(message.text, str):
            if message.text == "Прислать чек":
                bot.send_message(message.chat.id, "Хорошо! Пришлите мне фото.", reply_markup=types.ReplyKeyboardRemove())
                get_photo_qr(message)
            elif message.text == "Выход":
                bot.send_message(message.chat.id, "Это было классно😘 До свидания!🙂", reply_markup=types.ReplyKeyboardRemove())
            else: 
                keyboard = create_button.create_send_exit_keyboard()
                bot.send_message(message.chat.id, "Все еще Вас не понимаю... Хотите добавить ещё один чек? \n'Прислать чек' или 'Выйти'", reply_markup=keyboard)
                bot.register_next_step_handler(message, bot_again)
        else:
            keyboard = create_button.create_send_exit_keyboard()
            bot.send_message(message.chat.id, "Я вообще ничего не понял.  Хотите добавить ещё один чек? \n'Прислать чек' или 'Выйти'", reply_markup=keyboard)
            bot.register_next_step_handler(message, bot_again)
    else:
        keyboard = create_button.create_send_exit_keyboard()
        bot.send_message(message.chat.id, "Вы прислали не ответ. И всё таки, Будем отправлять новый QR-код? 'Прислать чек' или 'Выйти'", reply_markup=keyboard)
        bot.register_next_step_handler(message, bot_again)

# Настройка логирования
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

@atexit.register
def goodbye():
    # отправляем сообщение о том, что бот выключен в чат с указанным идентификатором
    bot.send_message(chat_support, "Bot offline")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(timeout=120, long_polling_timeout=120)
        
        # Ошибки, связанные с API Telegram
        except apihelper.ApiTelegramException as e:
            logging.error(f"ApiTelegramException: {e}", exc_info=True)
            bot.send_message(CHAT_ID, f"Произошла ошибка API Telegram: {e}. \nБот перезагружается.")
            bot.send_message(chat_support, f"Произошла ошибка! Произошла ошибка API Telegram: {e}.")

            if e.error_code == 429:  # Ошибка "Too Many Requests"
                retry_after = int(e.result_json['parameters']['retry_after'])
                bot.send_message(chat_support, f"Произошла ошибка! Произошла ошибка API Telegram 429: {e}.")
                time.sleep(retry_after)

            elif e.error_code == 409:  # Конфликт с другим экземпляром бота
                bot.send_message(CHAT_ID, "Конфликт: бот уже запущен в другом месте. \nПерезапуск через 5 секунд.")
                bot.send_message(chat_support, f"Произошла ошибка! Конфликт: бот уже запущен в другом месте: {e}.")
                time.sleep(5)
            
            else:
                bot.send_message(CHAT_ID, f"Неизвестная ошибка API Telegram: {e}. \nПерезапуск через 5 секунд.")
                bot.send_message(chat_support, f"Произошла ошибка! Неизвестная ошибка API Telegram: {e}.")
                time.sleep(5)

        # Ошибка ожидания
        except requests.exceptions.ReadTimeout as e:
            logging.error(f"ReadTimeout: {e}", exc_info=True)
            bot.send_message(CHAT_ID, f"Ошибка: Превышено время ожидания. \nБот перезапустится через 5 секунд. ")
            time.sleep(5)

        # Другие ошибки
        except Exception as e:
            logging.error(f"Exception: {e}", exc_info=True)
            bot.send_message(CHAT_ID, f"Произошла ошибка: {e}. \nБот будет перезапущен через 5 секунд.")
            time.sleep(5)

        else:
            # Сообщение отправляется после успешного восстановления бота
            bot.send_message(CHAT_ID, "Бот был перезагружен после ошибки.")
