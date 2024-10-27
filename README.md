# Телеграмм бот для проверки чеков
### Описание:

Телеграмм бот на Python для проверки чеков магазина. Бот проверяет возраст пользователя через telegram_bot_calendar, спрашивает имя пользователя, запрашивает номер телефона и запрашивает фото чека и записывает данные в файл exel
___

### Правила установки
1. Скачать файлы из репозитория
2. Создать файл config.py и там создать 3 переменных:
    1. api_key = "YOUR_API_TELEGRAMM_BOT"
    2. directory = "ПУТЬ ГДЕ БУДЕТ ФОТО QR-КОД"
    3. chat_support = "НОМЕР ТЕЛЕФОНА ДЛЯ ЧАТ-ПОДДЕРЖКИ"
3. Скачать зависимости:
    1. Node.js
    2. Python:
        1. pip install pyTelegramBotAPI
        2. pip install python-telegram-bot-calendar
        3. pip install urllib3
        4. pip install pyzbar
        5. pip install pandas
        6. pip install subprocess32
    3. Js
        1. npm install --save jimp
        2. npm install jsqr --save
