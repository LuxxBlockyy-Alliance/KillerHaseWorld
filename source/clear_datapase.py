import aiosqlite
import asyncio
import os
import random
import shutil
import sqlite3
import time

class Countdown:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def count_start(self):
        self.start_time = time.time()

    def count_stop(self):
        self.end_time = time.time()

    def counted_time(self):
        return self.end_time - self.start_time


async def clean_up_database(database_name: str, table_name: str, partition: int, num_splits: int):
    temp_database_name = 'temp_' + database_name
    shutil.copy(database_name, temp_database_name)

    try:
        async with aiosqlite.connect(temp_database_name) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT id FROM {table_name}')
                data = await cursor.fetchall()
                rows_to_delete = []
                for index, row in enumerate(data):
                    if row[0] == '' and index % num_splits == partition:
                        rows_to_delete.append(row[0])

                if rows_to_delete:
                    query = f'DELETE FROM {table_name} WHERE id=?'
                    await cursor.executemany(query, rows_to_delete)
                    await conn.commit()

                    query = f'UPDATE {table_name} SET id=? WHERE id=?'
                    for index, id in enumerate(rows_to_delete):
                        new_id = id - index - 1
                        await cursor.execute(query, (new_id, id))

                    await conn.commit()

            await cursor.close()
        await conn.close()
        os.remove(database_name)
        os.rename(temp_database_name, database_name)
    finally:
        if os.path.exists(temp_database_name):
            os.remove(temp_database_name)
            print(f"Counted time: {countdown.counted_time()} seconds")


async def parallel_clean_up_database(database_name: str, table_name: str, num_splits: int):
    tasks = []
    for i in range(num_splits):
        task = asyncio.ensure_future(clean_up_database(database_name, table_name, i, num_splits))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def main():
    await parallel_clean_up_database('example_database.db', 'rows', 4)


def create_example_database(filename):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS rows
                     (id INTEGER PRIMARY KEY, channel_id INTEGER, webhook_url TEXT)''')
    cursor.execute('DELETE FROM rows')

    rows = []
    for i in range(1000):
        rows.append((i, random.randint(1, 100), f"https://example.com/{i}"))

    cursor.executemany('INSERT INTO rows VALUES (?, ?, ?)', rows)
    conn.commit()
    conn.close()


def delete_random_rows(filename, number_of_rows_to_delete):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM rows ORDER BY RANDOM() LIMIT ?', (number_of_rows_to_delete,))
    rows_to_delete = cursor.fetchall()
    cursor.executemany('DELETE FROM rows WHERE id = ?', rows_to_delete)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_example_database("example_database.db")
    delete_random_rows("example_database.db", 20)
    countdown = Countdown()
    countdown.count_start()
    asyncio.run(main())