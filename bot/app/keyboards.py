from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

start = [InlineKeyboardButton(text='На главнyя', callback_data='start')]

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ На главную', callback_data='start')]
])


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мой профиль', callback_data='my_profile')],
    [InlineKeyboardButton(text='Создать Жалобу', callback_data='create_report'), InlineKeyboardButton(text='Получить совет', callback_data='get_tip')],
    [InlineKeyboardButton(text='SOS', callback_data='sos')],
    start,
    [InlineKeyboardButton(text='ℹ️ О проекте', callback_data='about_project')]
])

skip = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='skip')]
])

verify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Верифецировать аккаунт', callback_data='verify')],
    start
])

sos = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать сигнал сос',request_location=True)]
], resize_keyboard=True)