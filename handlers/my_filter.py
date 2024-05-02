from abc import ABC
from aiogram import types
from aiogram.filters import Filter


class GreetingFilter(Filter, ABC):
    key = 'is_greeting'

    def __init__(self, is_greeting: str) -> None:
        self.is_greeting = is_greeting

    async def __call__(self, message: types.Message) -> bool:
        text = message.text.lower()
        if self.is_greeting and ('hello' in text or 'привет' in text or 'добрый день' in text):
            return True
