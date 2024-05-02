from loguru import logger
from datetime import datetime
from peewee import (
    CharField,
    IntegerField,
    Model,
    SqliteDatabase,
    FloatField,
    DateTimeField,
)


db = SqliteDatabase('database.db')

# Шаблон формат для записи даты и времени
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    """
    Класс Пользователь.
    Создает таблицу в которой хранятся данные пользователя
    user_id = уникальный идентификатор пользователя
    username = никнейм в Telegram
    first_name = Имя при регистрации
    last_name = Фамилия пользователя
    """

    user_id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField(null=True)


# class Category(BaseModel):
#     category_id = IntegerField(primary_key=True)
#     name = CharField(unique=True)


class Product(BaseModel):
    """
    Класс Товары.
    Создает таблицу в которой хранятся данные о товарах
    product_id = уникальный идентификатор товара
    name = имя товара
    price = цена товара
    image = изображение товара
    """

    product_id = IntegerField(primary_key=True)
    name = CharField()
    price = FloatField()
    image = CharField()

    @staticmethod
    def get_min_price():
        """ Метод извлекает товар с минимальной ценой."""

        return Product.select().order_by(Product.price).first()

    @staticmethod
    def get_product_with_max_price():
        """ Метод извлекает товар с максимальной ценой."""
        return (Product.select()
                .order_by(Product.price.desc())
                .where(Product.price != 'Нет данных')
                .first())

    @staticmethod
    def get_product_from_and_to(from_price, to_price):
        """
        Метод извлекает товары в диапазоне от и до.
        На вход принимает 2 аргумента(числа) соответствующим диапазону от и до
        """

        product_group = (Product.select()
                         .order_by(Product.price)
                         .where((Product.price >= from_price) & (Product.price <= to_price)))

        # Группируем товары в список по 10 элементов
        return [product_group[i:i + 10] for i in range(0, len(product_group), 10)]


class Events(BaseModel):
    """
    Класс События.
    Создает таблицу в которой хранится информация о действиях пользователей
    date - дата события
    message_log - информационное сообщение
    log_level - уровень логирования(для удобства фильтровки сообщений)
    """

    date = DateTimeField(formats=DATE_FORMAT)
    message_log = CharField()
    log_level = CharField()

    @staticmethod
    def info_request(log):
        """ Метод сохраняет событие связанное с внешними get запросами."""

        record = Events(
            date=datetime.now().strftime(DATE_FORMAT),
            message_log=log,
            log_level='req_info',
        )
        record.save()

    @staticmethod
    def info_user_action(log):
        """
        Метод сохраняет событие связанные с действиями пользователя (например:
        пользователь зашел в чат;
        пользователь отправил фото;
        пользователь нажал кнопку и т.д).
        """

        record = Events(
            date=datetime.now().strftime(DATE_FORMAT),
            message_log=log,
            log_level='user_action',
        )
        record.save()

    @staticmethod
    def get_request_history():
        """ Метод извлекает из базы данных историю последних 10 запросов """

        request_history = Events.select().order_by(Events.id.desc()).where(Events.log_level == 'req_info').limit(10)
        history = []
        if request_history:
            for key, val in enumerate(request_history, start=1):
                history.append(f'{key}. {val.message_log} {val.date}')
        else:
            history.append('Записей в базе данных нет')
        return history


def database_log(message):
    """ Функция для логирования. Записывает логи в таблицу Events из базы данных """

    date_str = message.record["time"].strftime("%Y-%m-%d %H:%M:%S")
    Events.create(
        date=date_str,
        message_log=message.record["message"],
        log_level=message.record["level"].name,
    )


# Создаем запись логов.
logger.add(database_log, format="{time:%Y-%m-%d %H:%M:%S} | {level} | {message}", level='DEBUG')


def create_models():
    """ Функция создает таблицы в базе данных для всех подклассов класса `BaseModel`. """

    db.create_tables(BaseModel.__subclasses__())
