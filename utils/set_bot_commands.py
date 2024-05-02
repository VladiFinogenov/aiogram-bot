from aiogram import types
from aiogram import Bot
from aiogram.types import BotCommandScopeDefault


async def set_default_commands(bot: Bot):
    commands = [
        types.BotCommand(
            command='/start',
            description='запустить бота'
        ),
        types.BotCommand(
            command='/help',
            description='Справка по командам'
        ),
        types.BotCommand(
            command='/history',
            description='история запросов'
        ),
        types.BotCommand(
            command='/info',
            description='Получить информацию о режиме работы'
        )

    ]

    await bot.set_my_commands(commands=commands)
