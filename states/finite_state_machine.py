from aiogram.filters.state import StatesGroup, State


class UserMenu(StatesGroup):
    """ Класс в котором прописаны состояния навигации пользователя по меню:
    main_menu - пользователь находится в главном меню;
    parser_menu - пользователь находится в меню поиска товаров;
    task_menu - пользователь находится в меню менеджер задач;
    admin_menu - пользователь находится в меню администратора. """

    main_menu = State()
    parser_menu = State()
    task_menu = State()
    admin_menu = State()


class UserTask(StatesGroup):
    # Состояние ввода от пользователя напоминания(текста)
    task_enter_text = State()
    # Состояние в котором назначается функция(task_parser) для ее выполнения
    task_enter_parser = State()
    task_delete_db = State()
    # Состояние в котором ожидается что пользователь введет номер задачи для ее удаления из списка
    task_delete = State()


class InputDateStates(StatesGroup):
    waiting_for_date = State()  # Состояние ожидания ввода даты


class InputPassword(StatesGroup):
    login = State()  # Состояние ожидания ввода пароля


class InputTimeStates(StatesGroup):
    waiting_for_time = State()  # Состояние ожидания ввода времени


class PriceInputSteps(StatesGroup):
    """
    Класс, в котором прописаны состояния ввода минимальной и максимальной цены товара.
    input_min_price - состояние в котором от пользователя ожидается ввод минимальной цены.
    input_max_price - состояние в котором от пользователя ожидается ввод максимальной цены.
    cancel - переход в исходное состояние до того когда пользователь начал вводить
    минимальную или максимальную цену.
    """

    input_min_price = State()
    input_max_price = State()
    cancel = State()
