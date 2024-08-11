from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать рассылку')]],
                            resize_keyboard=True,
                            input_field_placeholder='Select menu item...')

get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Sent telephone number', 
                                                           request_contact=True)]],
                                resize_keyboard=True)

add_button_prompt = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes')],
    [InlineKeyboardButton(text='Нет', callback_data='no')]
])
