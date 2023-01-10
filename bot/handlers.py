import logging

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import bot.buttons as buttons
import controller.Controller as ctrl

controller = {}


class user_session(StatesGroup):
    load_game = State()
    choice_action = State()
    change_location = State()
    talk_to = State()
    start_battle = State()
    is_continue_battle = State()


async def start(message: types.Message):
    logging.info('user id ', message.chat.id)
    if not controller.get(message.chat.id):
        controller[message.chat.id] = ctrl.Controller('game.db')
    '''Проверка существования юзера'''
    main_menu = types.InlineKeyboardMarkup(row_width=2)
    if controller[message.chat.id].get_protagonist_info(message.chat.id) != None:
        main_menu.add(buttons.new_game, buttons.load_game)
    else:
        main_menu.add(buttons.new_game)
    await message.answer('Главное меню', reply_markup=main_menu)
    await user_session.load_game.set()


async def start_new_game(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Старт новой игры')
    await user_session.choice_action.set()
    controller[callback.message.chat.id].start_game(callback.message.chat.id, True)
    await print_info_about_user(callback.message)
    await show_possible_actions(callback.message)


async def load_game(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Загрузка игры...')
    controller[callback.message.chat.id].start_game(callback.message.chat.id, False)
    await callback.message.answer('Игра загружена')
    await print_info_about_user(callback.message)
    await show_possible_actions(callback.message)
    await user_session.choice_action.set()


async def print_info_about_user(message: types.Message):
    await message.answer('Вы:')
    await message.answer("Имя: " + controller[message.chat.id].protagonist.name + '\n' \
                         + "Уровень: " + str(controller[message.chat.id].protagonist.level) + '\n' \
                         + "Здоровье: " + str(controller[message.chat.id].protagonist.hp))


async def print_info_about_location(message: types.Message):
    msg = controller[message.chat.id].protagonist.whereami()
    for i in msg:
        await message.answer(i)


async def print_info_about_ai_in_location(message: types.Message):
    npc = controller[message.chat.id].get_npc_in_location(controller[message.chat.id].protagonist.locations.id)
    enemy = controller[message.chat.id].get_enemy_in_location(controller[message.chat.id].protagonist.locations.id)
    npc_message = 'НПС:'
    for i in npc:
        npc_message += '\n' + i.name
    await message.answer(npc_message)
    enemy_message = "Враги:"
    for i in enemy:
        enemy_message += '\n' + i.name
    await message.answer(enemy_message)


async def show_possible_actions(message: types.Message):
    actions = types.InlineKeyboardMarkup(row_width=2)
    actions.insert(buttons.go)
    try:
        if len(controller[message.chat.id].get_npc_in_location(controller[message.chat.id].protagonist.locations.id)):
            actions.insert(buttons.talk_to)
    except Exception as e:
        logging.error(e + '\n in show possible actions when get npc')
    try:
        if len(controller[message.chat.id].get_enemy_in_location(controller[message.chat.id].protagonist.locations.id)):
            actions.insert(buttons.start_battle)
    except Exception as e:
        logging.error(e + '\n in show possible actions when get enemys')
    actions.add(buttons.go_to_main_menu)
    actions.add(*buttons.info_buttons)
    await message.answer('Доступные действия', reply_markup=actions)


async def get_action(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == 'button_go':
        await user_session.change_location.set()
        await show_available_directions(callback.message)
    elif callback.data == 'button_talk_to':
        await user_session.talk_to.set()
        await choose_npc(callback)
    elif callback.data == 'button_start_battle' or callback.data == 'button_continue':
        await user_session.start_battle.set()
        await choose_enemy(callback)
    elif callback.data == 'button_about_me':
        await print_info_about_user(callback.message)
        await show_possible_actions(callback.message)
    elif callback.data == 'button_wereami':
        await print_info_about_location(callback.message)
        await show_possible_actions(callback.message)
    elif callback.data == 'button_whothere':
        await print_info_about_ai_in_location(callback.message)
        await show_possible_actions(callback.message)
    elif callback.data == 'button_go_to_main_menu':
        await state.finish()
        await start(callback.message)
    else:
        await callback.message.answer("something wrong")


async def get_direction(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    is_correct = True
    if 'button' in callback.data:
        is_correct = False
        if callback.data == 'button_about_me':
            await print_info_about_user(callback.message)
        elif callback.data == 'button_wereami':
            await print_info_about_location(callback.message)
        elif callback.data == 'button_whothere':
            await print_info_about_ai_in_location(callback.message)
        elif callback.data == 'button_go_to_choose_action':
            is_correct = True
    else:
        locations = controller[callback.message.chat.id].get_locations_to_go()
        if locations != None:
            try:
                for i in locations:
                    print(callback.data)
                    if i.id == int(callback.data):
                        controller[callback.message.chat.id].go(i)
                        loc = controller[callback.message.chat.id].get_current_location()
                        await callback.message.answer("Перешли в локацию " + loc.name)
                        await callback.message.answer(loc.description)
                        break
            except Exception as e:
                print(e)
                await callback.message.answer('Нет, похоже остаемся здесь(・人・)')
    if is_correct:
        await user_session.choice_action.set()
        await show_possible_actions(callback.message)
    else:
        await show_available_directions(callback.message)


async def show_available_directions(message: types.Message):
    """Получение доступных направлений"""
    directions = types.InlineKeyboardMarkup(row_width=2)
    locations = controller[message.chat.id].get_locations_to_go()
    if locations != None:
        for i in locations:
            directions.insert(types.InlineKeyboardButton(text=i.name, callback_data=i.id))
    directions.insert(buttons.go_to_choose_action)
    for i in buttons.info_buttons:
        directions.insert(i)
    await message.answer('Пойти...', reply_markup=directions)


async def choose_npc(callback: types.CallbackQuery):
    btns = types.InlineKeyboardMarkup(row_width=2)
    for i in controller[callback.message.chat.id].get_npc_in_location(
            controller[callback.message.chat.id].protagonist.locations.id):
        btns.insert(types.InlineKeyboardButton(text=i.name, callback_data=str(i.id)))
    for i in buttons.info_buttons:
        btns.insert(i)
    btns.insert(buttons.go_to_choose_action)
    await callback.message.answer('Поговорить с...', reply_markup=btns)


async def talk_to_npc(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if 'button' in callback.data:
        is_cancle = False
        if callback.data == 'button_about_me':
            await print_info_about_user(callback.message)
        elif callback.data == 'button_wereami':
            await print_info_about_location(callback.message)
        elif callback.data == 'button_whothere':
            await print_info_about_ai_in_location(callback.message)
        elif callback.data == 'button_go_to_choose_action':
            is_cancle = True
        if is_cancle:
            await user_session.choice_action.set()
            await show_possible_actions(callback.message)
        else:
            await choose_npc(callback)
    else:
        npc = controller[callback.message.chat.id].get_npc(callback.data)
        npc_phrases = controller[callback.message.chat.id].interact(npc.id)
        is_end_game = npc_phrases[0]
        await callback.message.answer(npc.name + ' says: "' + npc_phrases[1] + '"')
        if is_end_game:
            controller[callback.message.chat.id].end_game()
            await state.finish()
            await start(callback.message)
        else:
            await user_session.choice_action.set()
            await show_possible_actions(callback.message)


async def choose_enemy(callback: types.CallbackQuery):
    btns = types.InlineKeyboardMarkup(row_width=2)
    for i in controller[callback.message.chat.id].get_enemy_in_location(
            controller[callback.message.chat.id].protagonist.locations.id):
        btns.insert(types.InlineKeyboardButton(text=i.name + ' lvl:' + str(i.level), callback_data=str(i.id)))
    for i in buttons.info_buttons:
        btns.insert(i)
    btns.insert(buttons.go_to_choose_action)
    await callback.message.answer('Сражаться с...', reply_markup=btns)


async def attack_enemy(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if 'button' in callback.data:
        is_cancle = False
        if callback.data == 'button_about_me':
            await print_info_about_user(callback.message)
        elif callback.data == 'button_wereami':
            await print_info_about_location(callback.message)
        elif callback.data == 'button_whothere':
            await print_info_about_ai_in_location(callback.message)
        elif callback.data == 'button_go_to_choose_action':
            is_cancle = True
        if is_cancle:
            await user_session.choice_action.set()
            await show_possible_actions(callback.message)
        else:
            await choose_npc(callback)
    else:
        try:
            kill_enemy, phrases = controller[callback.message.chat.id].attack_enemy(int(callback.data))
            if phrases != None:
                await callback.message.answer('Q(`⌒´Q)')
                for i in phrases:
                    await callback.message.answer(i)
                if kill_enemy:
                    await user_session.choice_action.set()
                    await show_possible_actions(callback.message)
                else:
                    await user_session.is_continue_battle.set()
                    await callback.message.answer('Продолжить бой?',
                                                  reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                                                      buttons.continue_battle, buttons.end_battle))
        except Exception as e:
            print(e)
            controller[callback.message.chat.id].end_game()
            await callback.message.answer('Тебя отпинали юнлинги. Не стыдно?')
            await state.finish()
            await start(callback.message)


async def is_battle_continue(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == 'button_continue':
        await user_session.start_battle.set()
        await choose_enemy(callback)
    elif callback.data == 'button_end_battle':
        await callback.message.answer('w(°ｏ°)w')
        await user_session.choice_action.set()
        await show_possible_actions(callback.message)
    elif callback.data == 'button_about_me':
        await print_info_about_user(callback.message)
        await callback.message.answer('Продолжить бой?',
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(buttons.continue_battle,
                                                                                               buttons.end_battle))
    elif callback.data == 'button_wereami':
        await print_info_about_location(callback.message)
        await callback.message.answer('Продолжить бой?',
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(buttons.continue_battle,
                                                                                               buttons.end_battle))
    elif callback.data == 'button_whothere':
        await print_info_about_ai_in_location(callback.message)
        await callback.message.answer('Продолжить бой?',
                                      reply_markup=types.InlineKeyboardMarkup(row_width=1).add(buttons.continue_battle,
                                                                                               buttons.end_battle))
    else:
        await callback.message.answer('something wrong')
        await user_session.choice_action.set()
        await show_possible_actions(callback.message)
