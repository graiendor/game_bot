from aiogram import types

new_game = types.InlineKeyboardButton(text='Новая игра', callback_data='button_new_game')
load_game = types.InlineKeyboardButton(text='Загрузить игру', callback_data='button_load_game')

go = types.InlineKeyboardButton(text='Пойти...', callback_data='button_go')

talk_to = types.InlineKeyboardButton(text='Поговорить с...', callback_data='button_talk_to')

start_battle = types.InlineKeyboardButton(text='Начать сражение...', callback_data='button_start_battle')
continue_battle = types.InlineKeyboardButton(text='Продолжить сражаться...', callback_data='button_continue')
end_battle = types.InlineKeyboardButton(text='Сбежать', callback_data='button_end_battle')

go_to_choose_action = types.InlineKeyboardButton(text='Назад', callback_data='button_go_to_choose_action')
go_to_main_menu = types.InlineKeyboardButton(text="В главное меню", callback_data='button_go_to_main_menu')

info_buttons = []
info_buttons.append(types.InlineKeyboardButton(text='Кто я', callback_data='button_about_me'))
info_buttons.append(types.InlineKeyboardButton(text='Где я', callback_data='button_wereami'))
info_buttons.append(types.InlineKeyboardButton(text='Кто здесь', callback_data='button_whothere'))
