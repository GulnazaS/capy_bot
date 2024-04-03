from create_bot import *
# Запуск процесса поллинга новых апдейтов
DB_NAME = 'quiz_bot.db'

# Функция для получения статистики всех игроков
async def get_all_players_stats():
    all_players_stats = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM quiz_state') as cursor:
            async for row in cursor:
                all_players_stats.append(row)
    return all_players_stats

async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index, correct_answers):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers) VALUES (?, ?, ?)', (user_id, index, correct_answers))
        # Сохраняем изменения
        await db.commit()

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY,
                                                                    question_index INTEGER,
                                                                    correct_answers INTEGER)''')
        # Сохраняем изменения
        await db.commit()