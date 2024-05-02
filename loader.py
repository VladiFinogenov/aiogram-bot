from loguru import logger
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_data import config
from handlers.mes_handlers import (
    send_start,
    send_back,
    info,
    bot_help,
    get_history,
    bot_welcome,
    photo_handler,
    cmd_search,
    price_min,
    price_max,
    prices_from_and_to,
    cancel,
    input_validation,
    on_min_price,
    on_max_price,
    cmd_rates,
    send_echo
)
from task_scheduler.task_manager import (
    task_scheduler,
    task_text,
    task_actions,
    delete_a_task,
    set_the_date,
    set_the_time,
    task_parser
)
from utils.set_bot_commands import set_default_commands
from aiogram.filters import Command
from aiogram import F
from states.finite_state_machine import (
    UserMenu,
    UserTask,
    PriceInputSteps,
    InputDateStates,
    InputTimeStates,
    InputPassword
)
from handlers.my_filter import GreetingFilter
from database.model import create_models
from utils.middleware import SchedulerMiddleware
from admin.admin import admin_menu, admin_actions, verification_password


async def start_bot(bot: Bot):

    await set_default_commands(bot)
    await bot.send_message(chat_id=config.ADMIN_ID, text='бот запущен')
    logger.info('start bot')


async def stop_bot(bot: Bot):
    await bot.send_message(chat_id=config.ADMIN_ID, text='бот остановлен')
    logger.info('stop bot')


async def start():

    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    create_models()

    # Устанавливаем временную зону для планировщика задач
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.start()

    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    #  Регистрируем хэндлеры и указываем на какие команды или фильтры реагировать, так же указываем состояния

    dp.message.register(send_start, Command(commands=['start', 'run']))
    dp.message.register(info, Command(commands=['info']), UserMenu())
    dp.message.register(bot_help, Command(commands=['help']), UserMenu())
    dp.message.register(get_history, Command(commands=['history']), UserMenu())
    dp.message.register(photo_handler, F.photo, UserMenu())
    dp.message.register(bot_welcome, GreetingFilter(F.text), UserMenu())
    dp.message.register(cmd_search, F.text == '🛒 Поиск товара', UserMenu.main_menu)
    dp.message.register(price_min, F.text == '📉 low', UserMenu.parser_menu)
    dp.message.register(price_max, F.text == '📈 high', UserMenu.parser_menu)
    dp.message.register(send_back, F.text == '↩ Возврат в меню', UserMenu.parser_menu)
    dp.message.register(prices_from_and_to, F.text == '📊 custom', UserMenu.parser_menu)
    dp.message.register(cancel, F.text == 'Отмена ❎')
    dp.message.register(input_validation, F.func(lambda mes: not mes.text.isdigit()), PriceInputSteps())
    dp.message.register(on_min_price, F.func(lambda mes: mes.text.isdigit()), PriceInputSteps.input_min_price)
    dp.message.register(on_max_price, F.func(lambda mes: mes.text.isdigit()), PriceInputSteps.input_max_price)
    dp.message.register(cmd_rates, F.text == '💰 курс валют', UserMenu.main_menu)
    dp.message.register(task_scheduler, F.text == 'менеджер задач', UserMenu.main_menu)
    dp.message.register(task_actions, UserMenu.task_menu)
    dp.message.register(task_text, UserTask.task_enter_text)
    dp.message.register(delete_a_task, UserTask.task_delete)
    dp.message.register(set_the_date, InputDateStates.waiting_for_date)
    dp.message.register(set_the_time, InputTimeStates.waiting_for_time)
    dp.message.register(task_parser, UserTask.task_enter_parser)
    dp.message.register(admin_menu, F.text == 'админ панель', UserMenu.main_menu)
    dp.message.register(admin_actions, UserMenu.admin_menu)
    dp.message.register(verification_password, InputPassword.login)
    dp.message.register(send_echo, F.text)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
