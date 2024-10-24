from PIL import Image
from pyzbar.pyzbar import decode
import requests
import json
import subprocess

def call_js_qr_scanner(photo_path):
    # Вызываем JavaScript файл с помощью Node.js
    result = subprocess.run(['node', 'js/scan_qr.cjs', photo_path], capture_output=True, text=True)
    # Получаем результат
    if result.returncode == 0:
        return result.stdout
    


# Функция для конвертации изображения в формат JPEG
def convert_image_to_jpeg(input_path, output_path):
    # Открываем изображение с помощью Pillow
    image = Image.open(input_path)
    
    # Преобразуем в RGB (если изображение в другом цветовом формате)
    image = image.convert('RGB')
    
    # Сохраняем изображение в формате JPEG
    image.save(output_path, 'PNG')    

# Функция для отправки на сайт QR и запись ответа в файл response.json.
def get_response_FNS(QR):
    token = "29409.zYN90hTxFHzqJrDny"
    url = "https://proverkacheka.com/api/v1/check/get"

    # Пример параметров формата запроса с qrraw
    data = {
        "token": token,
        "qrraw": QR,  # Замените на ваш QR-код
    }

    # Выполняем POST-запрос
    response = requests.post(url, data=data)
    if response.status_code == 200:
        try:
            new_data = response.json()  # Преобразуем ответ в JSON
            
            # Читаем существующий файл response.json (если он есть)
            try:
                with open('response.json', 'r', encoding='utf-8') as json_file:
                    existing_data = json.load(json_file)
            except FileNotFoundError:
                existing_data = []  # Если файл не найден, создаем пустой список
            
            # Если структура файла — список, добавляем новый элемент
            if isinstance(existing_data, list):
                existing_data.append(new_data)
            else:
                print("Формат файла не поддерживается. Ожидался список.")
                existing_data = [existing_data, new_data]  # Преобразуем в список, если это не список
            
            # Записываем обновленные данные в файл
            with open('response.json', 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
            
        
        except ValueError:
            print("Не удалось декодировать JSON.")
    else:
        print(f"Запрос не успешен: {response.status_code}, тело ответа: {response.text}")
