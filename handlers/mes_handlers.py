import asyncio
from time import sleep
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto
from database.model import Users, Events, Product
from keyboards.buttons import main_menu_btn, price_btn_reply, cancel_btn
from parsers.rate import currency_rates
from states.finite_state_machine import UserMenu, PriceInputSteps


# commands=['start', 'run']
async def send_start(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    user = Users.get_or_none(Users.user_id == user_id)
    await state.set_state(UserMenu.main_menu)
    if user is None:
        Users.create(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
        )
        await message.answer(text='Добро пожаловать! \nя бот который может искать товары и получать о них данные',
                             reply_markup=main_menu_btn())
    else:
        await message.answer(text='рад снова вас видеть', reply_markup=main_menu_btn())
    Events.info_user_action(f'Выполнен вход в чат пользователем {first_name}')


# commands=['info'], state=UserMenu()
async def info(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    info_messages = {
        'main_menu': "Вы находитесь в главном меню.\n\n"
                     "Здесь вы можете:\n"
                     "Вызвать меню слева с быстрыми командами:\n"
                     "Команда /start - Начать общение с ботом(Перезапускает бота)\n"
                     "Команда /help - Получить справку по командам\n"
                     "Команда /info - Получить справку по работе с ботом\n"
                     "Запросить курс Доллара USD и Евро EUR:\n"
                     "кнопка Запросить курс"
                     "Найти необходимый товар:"
                     "Кнопка поиск товара",

        'parser_menu': 'Вы находитесь в меню "Поиск товара"\n'
                       'В этом меню доступно:\n'
                       'Кнопка "low" - самая низкая стоимость\n'
                       'Кнопка "high" - самая высокая стоимость\n'
                       'Кнопка "custom" - фильтр по цене от и до'

    }
    if current_state == UserMenu.main_menu:
        await message.answer(text=f"{info_messages['main_menu']}")
    else:
        await message.answer(text=f"{info_messages['parser_menu']}")


# commands=['help'], state=UserMenu()
async def bot_help(message: types.Message):
    await message.answer(text=" Привет! Я бот 🤖\n"
                              "Вот список доступных команд:\n"
                              "/start - Начать общение с ботом\n"
                              "/help - Получить справку по командам\n"
                              "/info - Получить информацию о боте\n"
                              "/history - Показать последние десять запросов"
                         )


# commands=['history'], state=UserMenu()
async def get_history(message: types.Message):
    res = Events.get_request_history()
    for i in res:
        await message.answer(text=f"\n{i}\n")
        await asyncio.sleep(0.1)


# GreetingFilter(F.text), state=UserMenu())
async def bot_welcome(message: types.Message):
    await message.reply(f'Привет {message.from_user.first_name}')


async def photo_handler(message: types.Message):
    """ Хэндлер для обработки сообщений с фотографиями от пользователя """
    await message.answer('Крутая фотка')


# F.text == '🛒 Поиск товара', state=UserMenu.main_menu
async def cmd_search(message: types.Message, state: FSMContext):
    Events.info_user_action('Нажата кнопка "Поиск товара"')
    await message.answer(text='Вы находитесь в меню Поиск товара '
                              'для вызова справки по меню отправьте команду /info', reply_markup=price_btn_reply())
    await state.set_state(UserMenu.parser_menu)


# F.text == '📉 low', state=UserMenu.parser_menu
async def price_min(message: types.Message, state: FSMContext):
    min_price = Product.get_min_price()
    Events.info_request('Выполнен запрос минимальной цены товара')
    await message.answer(text='Товар с минимальной стоимостью')
    await message.answer_photo(
        photo=min_price.image,
        caption=f'Наименование:\n{min_price.name}\n\nЦена: {min_price.price}'
    )
    await state.set_state(UserMenu.parser_menu)


# F.text == '📈 high', state=UserMenu.parser_menu
async def price_max(message: types.Message, state: FSMContext):
    max_price = Product.get_product_with_max_price()
    Events.info_request('Выполнен запрос товара с максимальной стоимостью')
    await message.answer(text='Товар с максимальной стоимостью')
    await message.answer_photo(photo=max_price.image,
                               caption=f'Наименование:\n{max_price.name}\n\nЦена: {max_price.price}')
    await state.set_state(UserMenu.parser_menu)


# F.text == '↩ Возврат в меню', state=UserMenu.parser_menu
async def send_back(message: types.Message, state: FSMContext):
    await message.answer(text='Вы находитесь в основном меню', reply_markup=main_menu_btn())
    await state.set_state(UserMenu.main_menu)  # Устанавливаем новое состояние


# F.text == '📊 custom', state=UserMenu.parser_menu
async def prices_from_and_to(message: types.Message, state: FSMContext):
    await message.answer(text='Введите диапазон цен:')
    await message.answer(text='Введите нижний диапазон:', reply_markup=cancel_btn)
    await state.set_state(PriceInputSteps.input_min_price)


# F.text == 'Отмена ❎', state=(PriceInputSteps.input_price, PriceInputSteps.input_max_price))
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(text="Отмена действий", reply_markup=price_btn_reply())
    await state.set_state(UserMenu.parser_menu)


# (lambda mes: not mes.text.isdigit(), state=(PriceInputSteps.input_price, PriceInputSteps.input_max_price))
async def input_validation(message: types.Message):
    await message.reply("Пожалуйста, введите только число.")


#  (lambda mes: mes.text.isdigit(), state=PriceInputSteps.input_price)
async def on_min_price(message: types.Message, state: FSMContext):

    # Сохраняем данные в машину состояний
    user_input = await state.update_data({'user_input': message.text})

    await message.answer(f'Вы ввели число "{message.text}"')
    await message.answer('Введите верхний диапазон:', reply_markup=cancel_btn)
    await state.set_state(PriceInputSteps.input_max_price)


# (lambda mes: mes.text.isdigit(), state=PriceInputSteps.input_max_price)
async def on_max_price(message: types.Message, state: FSMContext, bot: Bot):

    # достаем данные из состояний (ввод нижнего диапазона)
    user_data = await state.get_data()

    user_max_number = int(message.text)

    if user_max_number <= int(user_data['user_input']):
        await message.answer(f'Число должно быть больше нижнего диапазона "{user_data["user_input"]}"')
    else:
        Events.info_request(f'Выполнен запрос товаров в диапазоне от {user_data["user_input"]} до {user_max_number} ')
        product_list = Product.get_product_from_and_to(user_data['user_input'], user_max_number)

        await message.answer(text=f'Вы ввели число "{message.text}"')

        if product_list:
            await message.answer(text=f'Отправляю товары')
            await message.answer(text=f'Нажмите на любое фото чтобы посмотреть название и цену')
            for i_list in product_list:
                product_media = [InputMediaPhoto(type='photo',
                                                 media=product.image,
                                                 caption=f'Наименование:\n{product.name}\n\nЦена: {product.price}')
                                 for product in i_list]

                await bot.send_media_group(message.from_user.id, media=product_media)
            await message.answer(text="Конец списка", reply_markup=price_btn_reply())
        else:
            await message.answer(text=f'Товаров в диапазоне от {user_data["user_input"]} до {user_max_number} нет', reply_markup=price_btn_reply())
        await state.set_state(UserMenu.parser_menu)


async def cmd_rates(message: types.Message):
    sleep(1)
    data = currency_rates
    request_rates = 'Выполнен запрос валют'
    Events.info_request(request_rates)
    await message.answer(data)


# Обрабатываем любое сообщение которое не подходит под заданные условия других хэндлеров.
async def send_echo(message: types.Message):
    await message.answer(text='Я не разобрал твой запрос. Для получения справки по командам вызови команду "/help"')
