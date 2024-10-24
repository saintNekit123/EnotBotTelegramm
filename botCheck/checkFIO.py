import re

def is_full_name(text):
    # Разбиваем текст на слова
    words = text.split()
    
    # Проверяем, что каждое слово состоит только из кириллицы
    cyrillic_pattern = re.compile(r'^[А-Яа-яЁё]+$')

    # Если каждое слово соответствует регулярному выражению, возвращаем True
    for word in words:
        if not cyrillic_pattern.match(word) or len(word) <= 2:
            return False
    if len(words) in [1, 2, 3]:
        return True
    else:
        return False
