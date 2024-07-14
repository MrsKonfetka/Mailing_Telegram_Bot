from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать рассылку')]],
                            resize_keyboard=True,
                            input_field_placeholder='Select menu item...')

get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Sent telephone number', 
                                                           request_contact=True)]],
                                resize_keyboard = True)

mailing = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Текст', callback_data='text')],
        [InlineKeyboardButton(text='Текст с кнопкой', callback_data='text_btn')],
        [InlineKeyboardButton(text='Изображение с текстом', callback_data='text_img')],
        [InlineKeyboardButton(text='Изображение с текстом и кнопкой', callback_data='text_img_btn')]])