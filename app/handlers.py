from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import app.keyboards as kb
from app.database import add_user, add_mailing, add_mailing_channel

router = Router()

class Register(StatesGroup):
    name = State()
    age = State()
    number = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет, я бот для рассылок. Нажмите на кнопку снизу', reply_markup=kb.main)

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Бот только на стадии разработки. Извините, пока ничем не могу помочь :)')

@router.message(Command('register'))
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('Напишите свое имя')

@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer('Напишите свой возраст')

@router.message(Register.age)
async def register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.number)
    await message.answer('Отправьте свой номер телефона', reply_markup=kb.get_number)

@router.message(Register.number, F.contact)
async def register_number(message: Message, state: FSMContext):
    await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()
    add_user(data["name"], data["age"], data["number"])
    await message.answer(f'Ваше имя: {data["name"]}\nВаш возраст: {data["age"]}\nВаш номер телефона: {data["number"]}')
    await state.clear()

class Mailing(StatesGroup):
    message = State()
    button_text = State()
    button_url = State()

@router.message(F.text == 'Создать рассылку')
async def mailing(message: Message, state: FSMContext):
    await state.set_state(Mailing.message)
    await message.answer('Отправьте сообщение для рассылки.')

@router.message(Mailing.message, F.text)
async def handle_text_message(message: Message, state: FSMContext):
    await state.update_data(content=message.text, media_type='text')
    await ask_for_button(message, state)

@router.message(Mailing.message, F.photo)
async def handle_image_message(message: Message, state: FSMContext):
    image = message.photo[-1].file_id
    caption = message.caption or ''
    await state.update_data(content=caption, media=image, media_type='photo')
    await ask_for_button(message, state)

@router.message(Mailing.message, F.video | F.animation)
async def handle_video_message(message: Message, state: FSMContext):
    if message.video:
        media = message.video.file_id
    else:
        media = message.animation.file_id
    caption = message.caption or ''
    await state.update_data(content=caption, media=media, media_type='video')
    await ask_for_button(message, state)

async def ask_for_button(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer('Хотите добавить кнопку?', reply_markup=markup)
    await state.set_state(Mailing.button_text)

@router.message(Mailing.button_text, F.text == 'Да')
async def ask_button_text(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, отправьте текст для кнопки.', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True))
    await state.set_state(Mailing.button_url)

@router.message(Mailing.button_text, F.text == 'Нет')
async def finish_mailing(message: Message, state: FSMContext):
    await send_mailing(message, state)
    await state.clear()

@router.message(Mailing.button_url)
async def ask_button_url(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await message.answer('Пожалуйста, отправьте URL для кнопки.')

@router.message(Mailing.button_url)
async def finish_mailing_with_button(message: Message, state: FSMContext):
    await state.update_data(button_url=message.text)
    await send_mailing(message, state)
    await state.clear()

async def send_mailing(message: Message, state: FSMContext):
    data = await state.get_data()
    content = data['content']
    media_type = data.get('media_type')
    button_text = data.get('button_text')
    button_url = data.get('button_url')
    channels = ['@testchanelodin', '@testchaneldva'] 

    if button_text and button_url:
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])
    else:
        markup = None

    mailing_id = add_mailing(content=content, image_id=data.get('media'), video_id=data.get('media'), button_text=button_text, button_url=button_url)

    for channel in channels:
        try:
            if media_type == 'text':
                await message.bot.send_message(chat_id=channel, text=content, reply_markup=markup)
            elif media_type == 'photo':
                await message.bot.send_photo(chat_id=channel, photo=data['media'], caption=content, reply_markup=markup)
            elif media_type == 'video':
                await message.bot.send_video(chat_id=channel, video=data['media'], caption=content, reply_markup=markup)
            await message.answer(f'Сообщение отправлено в {channel}')
            add_mailing_channel(mailing_id, channel)
        except Exception as e:
            await message.answer(f'Не удалось отправить сообщение в {channel}: {str(e)}')

    await message.answer('Процесс отправки завершен.', reply_markup=kb.main)
