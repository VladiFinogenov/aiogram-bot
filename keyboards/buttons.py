from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_btn():
    """ Функция создает кнопки в главном меню """

    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text='🛒 Поиск товара')
    keyboard_builder.button(text='💰 курс валют')
    keyboard_builder.button(text='админ панель')
    keyboard_builder.button(text='менеджер задач')

    keyboard_builder.adjust(2, 2)

    return keyboard_builder.as_markup(resize_keyboard=True)


def task_btn():
    """ Функция создает кнопки в меню менеджер задач """

    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text='создать напоминание')
    keyboard_builder.button(text='текущие задачи')
    keyboard_builder.button(text='установить время для парсинга')
    keyboard_builder.button(text='удалить задачу')
    keyboard_builder.button(text='↩ Возврат в меню')

    keyboard_builder.adjust(2, 1, 2)

    return keyboard_builder.as_markup(resize_keyboard=True)


def price_btn_reply():
    """ Функция создает кнопки в меню парсер """

    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text='📉 low')
    keyboard_builder.button(text='📈 high')
    keyboard_builder.button(text='📊 custom')
    keyboard_builder.button(text='↩ Возврат в меню')

    keyboard_builder.adjust(3, 1)

    return keyboard_builder.as_markup(resize_keyboard=True)


def admin_btn():
    """ Функция создает кнопки в меню администратор """

    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text='Данные прокси')
    keyboard_builder.button(text='Журнал сообщений')
    keyboard_builder.button(text='очистить журнал')
    keyboard_builder.button(text='↩ В главное меню')

    keyboard_builder.adjust(3, 1)

    return keyboard_builder.as_markup(resize_keyboard=True)


def select_button():
    """ Функция создает кнопки выбора действия ДА/НЕТ """

    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text='ДА')
    keyboard_builder.button(text='НЕТ')

    keyboard_builder.adjust(1, 1)

    return keyboard_builder.as_markup(resize_keyboard=True)


""" Кнопка отмены """

cancel = KeyboardButton(text='Отмена ❎')
cancel_btn = ReplyKeyboardMarkup(keyboard=[[cancel]], resize_keyboard=True)








