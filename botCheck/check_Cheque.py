import json
import os
import botCheck.db as db

from urllib.parse import parse_qs
from botCheck import check_xlsx
from datetime import datetime

def find_Cheque(qr):
    file_path = 'response.json'

    #Находим номер чека
    params = parse_qs(qr)
    num_cheque = params.get('i', [None])[0]
    xlsx = check_xlsx.find_xlsx(num_cheque)

    if xlsx == True:
        return "Дубль"
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:            
                data = json.load(json_file)
                i = find_index_with_fd(data, num_cheque)

                error_cheque = data[i]["data"] 
                inn_org = data[i]["data"]["json"]["userInn"]
                time_buy = data[i]["data"]["json"]["dateTime"]
                totalSum = data[i]["data"]["json"]["totalSum"]
                date_obj = datetime.strptime(time_buy[:-9], "%Y-%m-%d")
                
                if error_cheque == "Превышено количество обращений по чеку.":
                    return "Первышено обращение"
                
                elif inn_org == "Your_INN" or "Your_INN":
                    if date_obj.year < 2024 and date_obj.month < 11 and date_obj.month < 11:
                        return "Просрочен"
                    else:
                        if totalSum < 200000:
                            return "Меньше 2000"
                        else:
                            return "Всё хорошо"

                else:
                    return "Куплен не в Магазине"
                
        except FileNotFoundError:
            print(f"Файл {file_path} не найден.")
        except json.JSONDecodeError:
            print("Ошибка при декодировании JSON.")
        except Exception as error:
            print(f"Произошла ошибка: {error} - find_Cheque")

def record_participant(user, qr):
    # Находим номер чека
    params = parse_qs(qr)
    num_cheque = params.get('i', [None])[0]  # По умолчанию None, если ключ не найден

    file_path = 'response.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            i = find_index_with_fd(data, num_cheque)
            
            if i is None or i >= len(data):
                print(f"Индекс {i} вне диапазона для данных: {data}")
                return
            
            # Извлечение данных
            time_buy_json = data[i]["data"]["json"]["dateTime"]
            time_buy = time_buy_json.split('T')[0]
            total_sum = data[i]["data"]["json"]["totalSum"] // 100
            store = data[i]["data"]["json"]["retailPlace"]

            # Проверка на None перед вызовом записи
            if all([user.linkT, user.fullname, user.phone, num_cheque, time_buy, store, total_sum]) is not None:
                db.set_participant(user.linkT, user.fullname, user.phone, num_cheque, time_buy, store, total_sum)
            else:
                print("Одно или несколько значений равны None.")

    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except json.JSONDecodeError:
        print("Ошибка при декодировании JSON.")
    except Exception as error:
        print(f"Произошла ошибка: {error} record_participant")
    # finally:
    #     # Удаляем файл после его использования
    #     if os.path.exists(file_path):
    #         os.remove(file_path)    

def find_fd_in_json(json_file, number):
    # Открываем и загружаем данные из JSON-файла
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем, является ли data списком или объектом
        if isinstance(data, list):
            for item in data:
                if item.get('fd') == number:
                    print(f"Найдено значение {number} в fd")
                    return
        elif isinstance(data, dict):
            if data.get('fd') == number:
                print(f"Найдено значение {number} в fd")
                return
        print(f"Значение {number} в fd не найдено.")
    
    except FileNotFoundError:
        print(f"Файл {json_file} не найден.")
    except json.JSONDecodeError:
        print("Ошибка при декодировании JSON.")
    except Exception as error:
        print(f"Произошла ошибка: {error} find_fd_in_json")

def find_dubl(json_path, num):
    try:

        with open('response.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            fd_values = [item.get("request", {}).get("manual", {}).get("fd") for item in data]
            for i in fd_values:
                if i == num:
                    return "Дубль"


    except FileNotFoundError:
        print(f"Файл {json_path} не найден.")
    except json.JSONDecodeError:
        print("Ошибка при декодировании JSON.")
    except Exception as error:
        print(f"Произошла ошибка: {error} find_dubl")


# Функция для поиска индекса элемента с нужным значением "fd"
def find_index_with_fd(data, fd_value):
    for index, element in enumerate(data):
        if 'request' in element and 'manual' in element['request']:
            if element['request']['manual'].get('fd') == fd_value:
                return index
    return None

