import json
import os
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from database.model import Product, Events
from loguru import logger


def get_user_agent():
    """
    Функция генерирует рандомный User Agent
    для имитации реального пользователя.
    """

    ua = UserAgent()
    user_agent = ua.random
    return user_agent


proxies = {'http': 'http://45.132.20.68:8000'}


def save_data_url():
    """
    Функция делает get запрос на указанный сайт,
    затем парсит html код, в скрипте находит класс с данными в формате json,
    сохраняя данные в корень проекта в формате json.
    """

    global proxies
    st_accept = "text/html"
    headers = {
        "Accept": st_accept,
        'User-Agent': get_user_agent()
    }

    try:
        response = requests.get('https://www.cantata.ru/tea/chay?page=12', headers=headers)
        # Проверяем статус-код ответа
        if response.status_code == 200:
            # Обработка успешного ответа
            logger.info('Запрос на сайт выполнен успешно')
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

        data = response.content
        soup = BeautifulSoup(data, "lxml")  # 'lxml' вид парсера
        json_data = soup.find('script', id='__NEXT_DATA__').text

        if json_data:

            # Преобразование JSON-строки в Python-объект
            json_obj = json.loads(json_data)

            # Указываем имя файла
            file_name = 'kantana_tia.json'

            # Путь к папке относительно текущей директории
            relative_folder_path = 'parsers'

            # Полный путь к файлу, учитывая относительный путь
            file_path = os.path.join(relative_folder_path, file_name)
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_obj, json_file, ensure_ascii=False, indent=4)


def add_or_update_product(data: dict) -> None:
    """
    Функция сначала проверяет существование товара с заданным именем.
    Если такой товар существует, она проверяет цену и url.
    Если цена или url совпадает, ничего не делается. Иначе она обновляет информацию о товаре.
    Если товара с таким именем нет, создается новый экземпляр товара и добавляется в базу данных.
    """

    existing_product = Product.select().where(Product.name == data['name']).first()

    if existing_product is not None:
        if existing_product.price != data['price']:
            existing_product.price = data['price']
            existing_product.save()
            # print(f"Информация о товаре {name} обновлена.") занести в лог файл
        if existing_product.image != data['image']:
            existing_product.image = data['image']
            existing_product.save()
            # print(f"Информация о товаре {image} обновлена.") занести в лог файл
    else:
        new_product = Product(name=data['name'], price=data['price'], image=data['image'])
        new_product.save()
        # print(f"Товар {name} успешно добавлен в базу данных.") занести в лог файл


def find_key_in_nested_dict(data, target_key):
    if not isinstance(data, dict):
        return None

    # Ищем ключ в текущем словаре
    if target_key in data:
        return data[target_key]['items']

    # Рекурсивно ищем ключ во всех вложенных словарях
    for key, value in data.items():
        if isinstance(value, dict):
            result = find_key_in_nested_dict(value, target_key)
            if result is not None:
                return result

    return None


def upload_data_url():
    """
    Функция считывает файл в формате json, проверяет содержимое ключа "products"
    с помощью функции find_key_in_nested_dict()
    дальше идем циклом по каждому товару("elem") и отправляем в функцию add_or_update_product()
    для дальнейшей сортировки необходимых данных и сохранения в базу данных.
    """

    with open('parsers/kantana_tia.json', 'r', encoding='utf8') as json_file:
        data = json.loads(json_file.read())

        key = "products"

        container = find_key_in_nested_dict(data, key)
        if container:
            for elem in container:
                product = {'name': elem['title'], 'price': elem['price'], 'image': elem['image']}
                add_or_update_product(product)
        else:
            Events.info_request(f'ключ {key} не найден')


async def main_tia():
    try:
        save_data_url()
        upload_data_url()
    except Exception as exp:
        print(exp)
