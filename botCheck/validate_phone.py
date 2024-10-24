import re

def validate_phone_number(phone):
    # Регулярное выражение для проверки, что номер начинается с 89 и состоит из 11 цифр
    pattern = r"^(?:\+79\d{9}|89\d{9})$"
    
    if re.match(pattern, phone):
        return True
    else:
        return False