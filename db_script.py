from create_bot import *
# Запуск процесса поллинга новых апдейтов
async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY,
                                                                    question_index INTEGER,
                                                                    correct_answers INTEGER)''')
        # Сохраняем изменения
        await db.commit()