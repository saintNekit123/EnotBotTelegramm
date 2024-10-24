from datetime import datetime

def check_BD(BD):
    date_str = str(BD)
    date_parts = list(map(int, date_str.split('-')))
    # Преобразуем список в объект datetime
    birthdate = datetime(date_parts[0], date_parts[1], date_parts[2])
    
    # Текущая дата
    today = datetime.now()
    
    # Расчет возраста
    age = today.year - birthdate.year
    
    # Корректировка, если день рождения ещё не был в текущем году
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age