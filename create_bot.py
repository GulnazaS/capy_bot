import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
import json
from db_script import update_quiz_index, get_quiz_index, get_all_players_stats
from quiz_question import *

#Логирование
logging.basicConfig(level=logging.INFO)

#Токен от BotFather
API_TOKEN = 'API_TOKEN'

#Объект бота
bot = Bot(token=API_TOKEN)
#Диспетчер
dp = Dispatcher()

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_answers = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    correct_answers += 1
    await update_quiz_index(callback.from_user.id, current_question_index, correct_answers)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. КапиКвиз завершен! Вы набрали {correct_answers} баллов")

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_answers = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, correct_answers)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. КапиКвиз завершен! Вы набрали {correct_answers} баллов")
 #Хэндлер на команду /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в КапиКвиз!", reply_markup=builder.as_markup(resize_keyboard=True))

async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    correct_answers = 0
    await update_quiz_index(user_id, current_question_index, correct_answers)
    await get_question(message, user_id)

# Функция для отправки статистики всех игроков в телеграм
async def send_all_players_stats(message: types.Message):
    all_players_stats = await get_all_players_stats()

    if all_players_stats:
        response_message = "All Players Stats:\n"
        for player_stats in all_players_stats:
            user_id, question_index, correct_answers = player_stats
            response_message += f"User ID: {user_id}, Question Index: {question_index}, Correct Answers: {correct_answers}\n"
    else:
        response_message = "No player stats found."

    await message.answer(response_message)

# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем КапиКвиз!")
    await new_quiz(message)

# Хэндлер на команду запроса статистики игрока
@dp.message(F.text=="Статистика")
@dp.message(Command("stats"))
async def on_all_stats_command(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Посмотреть статистику по всем игрокам"))
    await send_all_players_stats(message)
