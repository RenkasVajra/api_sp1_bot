import os
import time

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(filemode='w', level=logging.DEBUG)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/{method}/'
BOT = telegram.Bot(token=TELEGRAM_TOKEN)

def parse_homework_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    else:
        verdict = 'Работа ещё на проверке, проверка длится не более 24 часов.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
       }
    
    params_get = {
        'from_date':current_timestamp,
    }
    try:
        homework_statuses = requests.get(
            url=URL.format(method='homework_statuses'), 
            params=params_get, 
            headers=headers
        )
        return homework_statuses.json()
    except RequestException:
        return (
            'Найдено исключение, '
            'которое произошло во время обработки вашего запроса.')



def send_message(message, bot_client):
    return bot_client.send_message(text=message,chat_id=CHAT_ID)


def main():
    current_timestamp = int(time.time()) 

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]),BOT
                )
            current_timestamp = new_homework.get(
                'current_date', 
                current_timestamp
            ) 
            time.sleep(300)  

        except Exception as e:
            logging.debug('This is a debug message')
            time.sleep(5)


if __name__ == '__main__':
    main()
