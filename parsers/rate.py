import json
import requests
from fake_useragent import UserAgent
from loguru import logger


def get_user_agent():
    ua = UserAgent()
    user_agent = ua.random
    return user_agent


@logger.catch
def get_currency_rates():
    st_accept = "text/html"
    headers = {
        "Accept": st_accept,
        'User-Agent': get_user_agent()
    }
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js', headers=headers)
        data = json.loads(response.text)
    except requests.exceptions.HTTPError as http_err:
        logger.warning(f"HTTP ошибка: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logger.warning(f"Ошибка соединения: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logger.warning(f"Время ожидания истекло: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logger.warning(f"Ошибка запроса: {req_err}")
    except Exception as exp:
        logger.warning(f"Другая ошибка: {exp}")
    else:
        # Текущий тариф
        current_usd_rate = data['Valute']['USD']['Value']
        current_eur_rate = data['Valute']['EUR']['Value']

        # Тариф за предыдущий день
        previous_usd_rate = data['Valute']['USD']['Previous']
        previous_eur_rate = data['Valute']['EUR']['Previous']

        data_str = 'USD:{:>38}\n{:>45}\n{}\nEUR:{:>38}\n{:>46}'.format(
            f'current_rate:  {current_usd_rate}',
            f'previous_rate:  {previous_usd_rate}',
            f'{"="*30}',
            f'current_rate:  {current_eur_rate}',
            f'previous_rate:  {previous_eur_rate}')
        return data_str


currency_rates = get_currency_rates()
