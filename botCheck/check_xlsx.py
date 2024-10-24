import pandas as pd

def find_xlsx(num_cheque):
    # Загрузка файла Excel
    file_path = r'C:\Users\Никита\Desktop\EnotBot\Participants.xlsx' 
    df = pd.read_excel(file_path)

    # Извлечение номеров чеков в список
    check_numbers = df['Номер чека'].tolist()
    for i in check_numbers:
        if i == int(num_cheque):
            return True
        