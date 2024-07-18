from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    image = State()
    image_caption = State()
    image_caption_button = State()
    button_url = State()
    video_caption = State()
    video_caption_button = State()
    video_button_text = State()
    video_button_url = State()

@router.message(F.text == 'Создать рассылку')
async def mailing(message: Message):
    await message.answer('Что отправим?', reply_markup=kb.mailing)

@router.callback_query(F.data == 'text')
async def text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.message)
    await callback.message.answer('Пожалуйста, отправьте сообщение, которое вы хотите разослать.')
    await callback.answer()

@router.callback_query(F.data == 'text_btn')
async def text_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.message)
    await callback.message.answer('Пожалуйста, отправьте сообщение, которое вы хотитe разослать.')
    await callback.answer()
    await state.update_data(with_button=True)

@router.callback_query(F.data == 'text_img')
async def text_img(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.image_caption)
    await callback.message.answer('Пожалуйста, отправьте изображение с подписью.')
    await callback.answer()

@router.callback_query(F.data == 'text_img_btn')
async def text_img_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.image_caption_button)
    await callback.message.answer('Пожалуйста, отправьте изображение с подписью.')
    await callback.answer()

@router.callback_query(F.data == 'text_video')
async def text_video(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.video_caption)
    await callback.message.answer('Пожалуйста, отправьте видео с подписью.')
    await callback.answer()

@router.callback_query(F.data == 'text_video_btn')
async def text_video_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.video_caption_button)
    await callback.message.answer('Пожалуйста, отправьте видео с подписью.')
    await callback.answer()

@router.message(Mailing.image_caption_button, F.photo)
async def handle_image_caption_button(message: Message, state: FSMContext):
    image = message.photo[-1].file_id
    caption = message.caption or ''
    await state.update_data(image=image, caption=caption)
    await state.set_state(Mailing.button_text)
    await message.answer('Пожалуйста, отправьте текст для кнопки.')
    
@router.message(Mailing.video_caption, F.video | F.animation)
async def handle_video_caption(message: Message, state: FSMContext):
    if message.video:
        media = message.video.file_id
    else:
        media = message.animation.file_id
    caption = message.caption
    channels = ['@testchanelodin', '@testchaneldva']

    mailing_id = add_mailing(content=caption, video_id=media)

    for channel in channels:
        try:
            await message.bot.send_video(chat_id=channel, video=media, caption=caption)
            await message.answer(f'Видео отправлено в {channel}')
            add_mailing_channel(mailing_id, channel)
        except Exception as e:
            await message.answer(f'Не удалось отправить видео в {channel}: {str(e)}')

    await state.clear()
    await message.answer('Процесс отправки завершен.')

@router.message(Mailing.video_caption_button, F.video | F.animation)
async def handle_video_caption_button(message: Message, state: FSMContext):
    if message.video:
        media = message.video.file_id
    else:
        media = message.animation.file_id
    caption = message.caption or ''
    await state.update_data(video=media, caption=caption)
    await state.set_state(Mailing.video_button_text)
    await message.answer('Пожалуйста, отправьте текст для кнопки.')

@router.message(Mailing.message)
async def handle_mailing_message(message: Message, state: FSMContext):
    data = await state.get_data()
    with_button = data.get('with_button', False)

    if with_button:
        await state.set_state(Mailing.button_text)
        await state.update_data(mailing_message=message.text)
        await message.answer('Пожалуйста, отправьте текст для кнопки.')
    else:
        mailing_message = message.text
        channels = ['@testchanelodin', '@testchaneldva'] 

        mailing_id = add_mailing(mailing_message)

        for channel in channels:
            try:
                await message.bot.send_message(chat_id=channel, text=mailing_message)
                await message.answer(f'Сообщение отправлено в {channel}')
                add_mailing_channel(mailing_id, channel)
            except Exception as e:
                await message.answer(f'Не удалось отправить сообщение в {channel}: {str(e)}')

        await state.clear()
        await message.answer('Процесс отправки завершен.')

@router.message(Mailing.button_text)
async def handle_button_text(message: Message, state: FSMContext):
    data = await state.get_data()
    button_text = message.text
    await state.update_data(button_text=button_text)
    await state.set_state(Mailing.button_url)
    await message.answer('Пожалуйста, отправьте URL для кнопки.')

@router.message(Mailing.video_button_text)
async def handle_video_button_text(message: Message, state: FSMContext):
    button_text = message.text
    await state.update_data(button_text=button_text)
    await state.set_state(Mailing.video_button_url)
    await message.answer('Пожалуйста, отправьте URL для кнопки.')

@router.message(Mailing.button_url)
async def handle_button_url(message: Message, state: FSMContext):
    data = await state.get_data()
    button_url = message.text
    button_text = data['button_text']

    if 'mailing_message' in data:
        mailing_message = data['mailing_message']
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])
        channels = ['@testchanelodin', '@testchaneldva']

        mailing_id = add_mailing(content=mailing_message, button_text=button_text, button_url=button_url)

        for channel in channels:
            try:
                await message.bot.send_message(chat_id=channel, text=mailing_message, reply_markup=markup)
                await message.answer(f'Сообщение с кнопкой отправлено в {channel}')
                add_mailing_channel(mailing_id, channel)
            except Exception as e:
                await message.answer(f'Не удалось отправить сообщение в {channel}: {str(e)}')
    else:
        image = data['image']
        caption = data['caption']
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])
        channels = ['@testchanelodin', '@testchaneldva']

        mailing_id = add_mailing(content=caption, image_id=image, button_text=button_text, button_url=button_url)

        for channel in channels:
            try:
                await message.bot.send_photo(chat_id=channel, photo=image, caption=caption, reply_markup=markup)
                await message.answer(f'Изображение с кнопкой отправлено в {channel}')
                add_mailing_channel(mailing_id, channel)
            except Exception as e:
                await message.answer(f'Не удалось отправить изображение в {channel}: {str(e)}')

    await state.clear()
    await message.answer('Процесс отправки завершен.')

@router.message(Mailing.video_button_url)
async def handle_video_button_url(message: Message, state: FSMContext):
    data = await state.get_data()
    button_url = message.text
    button_text = data['button_text']
    video = data['video']
    caption = data['caption']
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])
    channels = ['@testchanelodin', '@testchaneldva']

    mailing_id = add_mailing(content=caption, video_id=video, button_text=button_text, button_url=button_url)

    for channel in channels:
        try:
            await message.bot.send_video(chat_id=channel, video=video, caption=caption, reply_markup=markup)
            await message.answer(f'Видео с кнопкой отправлено в {channel}')
            add_mailing_channel(mailing_id, channel)
        except Exception as e:
            await message.answer(f'Не удалось отправить видео в {channel}: {str(e)}')

    await state.clear()
    await message.answer('Процесс отправки завершен.')
    
@router.message(Mailing.image_caption, F.photo)
async def handle_image(message: Message, state: FSMContext):
    data = await state.get_data()
    image = message.photo[-1].file_id
    caption = message.caption
    channels = ['@testchanelodin', '@testchaneldva']

    mailing_id = add_mailing(content=caption, image_id=image)

    for channel in channels:
        try:
            await message.bot.send_photo(chat_id=channel, photo=image, caption=caption)
            await message.answer(f'Изображение отправлено в {channel}')
            add_mailing_channel(mailing_id, channel)
        except Exception as e:
            await message.answer(f'Не удалось отправить изображение в {channel}: {str(e)}')

    await state.clear()
    await message.answer('Процесс отправки завершен.')

@router.message(Mailing.image_caption_button, F.photo)
async def handle_image_caption_button(message: Message, state: FSMContext):
    image = message.photo[-1].file_id
    caption = message.caption or ''
    await state.update_data(image=image, caption=caption)
    await state.set_state(Mailing.button_text)
    await message.answer('Пожалуйста, отправьте текст для кнопки.')

@router.message(Mailing.button_text)
async def handle_button_text(message: Message, state: FSMContext):
    button_text = message.text
    await state.update_data(button_text=button_text)
    await state.set_state(Mailing.button_url)
    await message.answer('Пожалуйста, отправьте URL для кнопки.')
