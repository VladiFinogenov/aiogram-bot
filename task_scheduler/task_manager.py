from parsers.kantata_tia import main_tia
from aiogram.types import ReplyKeyboardRemove
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram import types
from states.finite_state_machine import UserTask, UserMenu, InputDateStates, InputTimeStates
from aiogram.fsm.context import FSMContext
from datetime import datetime, date
from keyboards.buttons import main_menu_btn, select_button, task_btn


async def task_parser(
        message: types.Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):
    if message.text == 'ДА':
        data = await state.get_data()

        year, month, day, hour, minute = data['date']

        apscheduler.add_job(
            func=main_tia,
            trigger='date',
            run_date=datetime(year, month, day, hour, minute),
            name='task_parser'
        )

        await state.set_state(UserMenu.task_menu)

        await message.answer(text='задача создана', reply_markup=task_btn())
    elif message.text == 'НЕТ':
        await state.set_state(UserMenu.task_menu)
        await message.answer(text='Вы отменили ввод', reply_markup=task_btn())
    else:
        await message.answer(text='Некорректный ввод')


async def text(message, bot: Bot, chat_id: int):
    print(message)
    await bot.send_message(chat_id=chat_id, text=f'⏰ Напоминание\n{message}')


async def task_text(
        message: types.Message,
        bot: Bot,
        state: FSMContext,
        apscheduler: AsyncIOScheduler):

    data = await state.get_data()

    year, month, day, hour, minute = data['date']

    apscheduler.add_job(
        func=text,
        trigger='date',
        run_date=datetime(year, month, day, hour, minute),
        name='task_text',
        args=[message.text],
        kwargs={'bot': bot, 'chat_id': message.from_user.id}
    )

    await state.set_state(UserMenu.task_menu)

    await message.answer(text='напоминание создано', reply_markup=task_btn())


async def delete_a_task(
        message: types.Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):
    jobs = apscheduler.get_jobs()

    if message.text.isdigit():
        number = int(message.text)
        if 1 <= number <= len(jobs):
            removed_job = jobs.pop(number - 1)
            removed_job.remove()
            await state.set_state(UserMenu.task_menu)
            await message.answer(
                text=f"Задача '{removed_job.name}' удалена.",
                reply_markup=task_btn()
            )
        else:
            await message.answer(
                text='Некорректный номер задачи. Пожалуйста, введите номер из списка.'
            )
    else:
        await message.answer(text='Некорректный формат ввода. Попробуйте еще')


async def set_the_date(message: types.Message, state: FSMContext):
    date_str = message.text
    try:
        year, month, day = map(int, date_str.split(' '))
        current_date = datetime.now()

        if (
                year <= current_date.year and
                1 <= month <= 12 and
                1 <= day <= current_date.day
        ):

            # Переход к состоянию ожидания ввода времени
            await state.set_state(InputTimeStates.waiting_for_time)

            # Сохранение введенной даты в контексте состояния
            await state.update_data(date=[year, month, day])

            await message.answer(
                text="Введите время в формате HH MM (часы минуты),\n например: '14 30'.",
                reply_markup=ReplyKeyboardRemove()
            )

        else:
            await message.reply("Недопустимая дата. Попробуйте снова.")

    except ValueError:
        await message.reply("Некорректный формат даты. Попробуйте снова.")


async def set_the_time(message: types.Message, state: FSMContext):
    try:
        # Ввод времени в формате HH MM
        hour, minute = map(int, message.text.split())
        if 0 <= hour < 24 and 0 <= minute < 60:

            data = await state.get_data()
            year, month, day = data['date']
            current_task = data['task']

            selected_datetime = datetime(year, month, day, hour, minute)

            # Проверка, что выбранное время не раньше текущего момента
            current_datetime = datetime.now()

            if selected_datetime >= current_datetime:
                await state.update_data(date=[year, month, day, hour, minute])

                # Проверяем какая задача записана в машину состояний для ее выполнения
                if data['task'] == UserTask.task_enter_parser:  # Если записана задача task_parser
                    await message.answer(
                        text=f"Вы выбрали дату и время: {selected_datetime.strftime('%Y:%m:%d %H:%M')}"
                    )
                    await message.answer(
                        text='Нажмите "Да" чтобы создать задачу, "Нет" чтобы отменить',
                        reply_markup=select_button()
                    )
                    await state.set_state(current_task)
                else:
                    await message.answer(
                        f"Вы выбрали дату и время: {selected_datetime.strftime('%Y:%m:%d %H:%M')}"
                    )
                    await message.answer(
                        text='введите напоминание',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    await state.set_state(current_task)
            else:
                await message.reply("Выбранное время уже прошло. Попробуйте снова.")

        else:
            await message.reply("Некорректное время. Попробуйте снова.")
    except ValueError:
        await message.reply("Некорректный формат времени. Попробуйте снова.")


async def task_actions(message: types.Message, state: FSMContext, apscheduler: AsyncIOScheduler):
    if message.text == 'создать напоминание':

        # сохраняем название задачи в контексте состояния
        await state.update_data(task=UserTask.task_enter_text)

        await state.set_state(InputDateStates.waiting_for_date)
        await message.answer(
            text=f"Введите дату в формате 'день, месяц, год', "
                 f"например, {date.today().strftime('%Y %m %d')}.",
            reply_markup=ReplyKeyboardRemove()
        )

    elif message.text == 'текущие задачи':
        jobs = apscheduler.get_jobs()
        if jobs:
            await message.answer(text='Список задач')
            for num, job in enumerate(jobs, start=1):
                await message.answer(text=f'{num} {job.name} {job.next_run_time}')
        else:
            await message.answer(text='У вас нет текущих задач')

    elif message.text == 'удалить задачу':

        if apscheduler.get_jobs():

            await message.answer(
                text='Введите номер задачи для удаления',
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(UserTask.task_delete)
            jobs = apscheduler.get_jobs()
            for num, job in enumerate(jobs, start=1):
                await message.answer(text=f'{num} {job.name} {job.next_run_time}')
        else:
            await message.answer(text='У вас нет текущих задач')

    elif message.text == 'установить время для парсинга':

        await state.update_data(task=UserTask.task_enter_parser)
        await state.set_state(InputDateStates.waiting_for_date)
        await message.answer(
            text=f"Введите дату в формате 'день, месяц, год', "
                 f"например, {date.today().strftime('%Y %m %d')}.",
            reply_markup=ReplyKeyboardRemove()
        )

    elif message.text == '↩ Возврат в меню':
        await state.set_state(UserMenu.main_menu)
        await message.answer(text='Вы находитесь в главном меню', reply_markup=main_menu_btn())


async def task_scheduler(message: types.Message, state: FSMContext):
    await message.answer(text='Выберите задачу', reply_markup=task_btn())
    await state.set_state(UserMenu.task_menu)

