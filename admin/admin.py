import json
import requests
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import FSInputFile
from database.model import Events
from config_data import config
from keyboards.buttons import main_menu_btn, admin_btn
from states.finite_state_machine import UserMenu, InputPassword
import os
from loguru import logger


def get_data_proxy():
    try:
        response = requests.get(f'https://proxy6.net/api/{config.PROXY_KEY}/getproxy/')
        # Проверяем статус-код ответа
        if response.status_code == 200:
            # Обработка успешного ответа
            Events.info_request('Запрос на сайт выполнен успешно')
    except requests.exceptions.RequestException as exp:
        # Запись ошибок, связанных с запросом
        Events.info_request(f'Ошибка запроса: {exp}')
    except Exception as exp:
        # Запись других ошибок
        Events.warning(f'Произошла ошибка: {exp}')

    else:
        data = json.loads(response.text)
        new_data = {'Баланс': data['balance'],
                    'Тип прокси': data['list']['24361983']['type'],
                    'Дата покупки прокси': data['list']['24361983']['date'],
                    'Дата окончания срока действия прокси': data['list']['24361983']['date_end'],
                    'Активный (1) или нет (0)': data['list']['24361983']['active']}

        return json.dumps(new_data, ensure_ascii=False, indent=4)


async def admin_actions(message: types.Message, state: FSMContext):
    if message.text == 'Данные прокси':
        data = get_data_proxy()

        await message.answer(text=f'{data}')

    elif message.text == 'Журнал сообщений':

        try:
            # Запрос к базе данных и формирование отчета
            reports = Events.select()
            report_text = "Отчет из базы данных:\n"
            for report in reports:
                report_text += (f"текст: {report.message_log} "
                                f"| Уровень: {report.log_level} | date {report.date}\n\n")

            # Создаем временный файл с отчетом
            with open("report.txt", "w", encoding="utf-8") as file:
                file.write(report_text)
                root_directory = os.getcwd()

            # Задаем путь к файлу относительно корня проекта
            file_path = os.path.join(root_directory, "report.txt")
            document = FSInputFile(path=file_path)
            await message.answer_document(document=document)

        except Exception as exp:
            logger.error(f"Ошибка при формировании и отправке отчета: {exp}")

    elif message.text == 'очистить журнал':
        Events.delete().execute()
        await message.answer(text='очистка журнала сообщений')
    elif message.text == '↩ В главное меню':
        await state.set_state(UserMenu.main_menu)
        await message.answer(text='Вы находитесь в главном меню', reply_markup=main_menu_btn())


async def verification_password(message: types.Message, state: FSMContext):
    if message.text == config.PASSWORD:
        await state.set_state(UserMenu.admin_menu)
        await message.answer(text='Вы авторизованны', reply_markup=admin_btn())
    else:
        await message.answer(text='Не верный пароль. Попробуйте снова')


async def admin_menu(message: types.Message, state: FSMContext):

    if message.from_user.id == int(config.ADMIN_ID):
        await message.answer(text='Вы авторизованы как администратор', reply_markup=admin_btn())
        await state.set_state(UserMenu.admin_menu)

    else:
        await message.answer(text='Вы не являетесь администратором.\n'
                                  'Введите пароль для доступа')
        await state.set_state(InputPassword.login)
