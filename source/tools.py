import sqlite3

import aiofiles
import aiosqlite
from configparser import ConfigParser
import datetime
import discord
import aiohttp
import re
import asyncio
from collections import defaultdict
import requests
import random
from git import Repo, Actor
from discord import Webhook


async def async_copy_large_file(source_file_path, target_file_path,
                                chunk_size=1024 * 1024):  # default chunk size is 1MB
    async with aiofiles.open(source_file_path, mode='rb') as source:
        with open(target_file_path, mode='w') as target:
            target.write("")
            target.flush()
            target.close()
        async with aiofiles.open(target_file_path, mode='wb') as target:
            async for chunk in _read_in_chunks(source, chunk_size):
                await target.write(chunk)


async def _read_in_chunks(file_object, chunk_size):
    while True:
        data = await file_object.read(chunk_size)
        if not data:
            break
        yield data


async def backup_database(dp_path: str = './source/world.db'):
    db_path = dp_path + datetime.datetime.now().strftime('%Y%m%d%H%M%S').__str__()
    with open(f"{db_path + datetime.datetime.now().strftime('%Y%m%d%H%M%S').__str__()}.db", "w") as f:
        pass
    await async_copy_large_file(dp_path, db_path)
    repo_path = "."
    repo = Repo(repo_path)
    actor = Actor("Luxx", "lkgames256@gmail.com")
    repo.index.add([f"{db_path}"])
    repo.index.commit(f"Database backup from {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}", author=actor, committer=actor)

    # Push to GitHub
    origin = repo.remote(name='origin')
    origin.push()


async def send_global_broadcast(message: str):
    webhook_session = aiohttp.ClientSession()
    for url in await get_column("../world.db", "world_chats", "webhook_url"):
        try:
            webhook = Webhook.from_url(str(url), session=webhook_session)
            e = discord.Embed(
                title="🚀 BROADCAST 🚀",
                description=f"{message}",
                timestamp=datetime.datetime.now(),
                color=discord.Colour.red()
            )
            e.set_footer(text=" ✅ Dies ist eine offizielle Nachricht ✅")
            await webhook.send(embed=e, avatar_url="https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png")
        except discord.NotFound as e:
            print(
                "Es ist ein Fehler aufgetreten. Möglicherweise gibt es einen Webhook in der Datenbank, der nicht vorhanden ist.")
            pass


async def send_data(message):
    url = "http://195.62.46.112:3331/api"
    headers = {'Content-Type': 'application/json'}
    data = {'message': f'{message.lower()}'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.json()}')
        return response.status_code


async def delete_webhook_channel_id(channel_id: int):
    row: list = await view_dat_row(await get_DB_path(), "world_chats", "channel_id", channel_id)
    row: tuple = row[0]
    async with aiohttp.ClientSession() as session:
        async with session.delete(
                f"{row[2]}",
                headers={"Content-Type": "application/json"},
        ) as response:
            if response.status == 204:
                print("Webhook deleted!")
            else:
                async with session.get(
                        f"{row[2]}",
                        headers={"Content-Type": "application/json"},
                ) as response_check:
                    if response_check == 404:
                        print("This webhook doesn't exist!")
                    else:
                        print(f"Failed to delete webhook.")


async def delete_webhook_id(server_id: int):
    row: list = await view_dat_row(await get_DB_path(), "world_chats", "id", server_id)
    row: tuple = row[0]
    async with aiohttp.ClientSession() as session:
        async with session.delete(
                f"{row[2]}",
                headers={"Content-Type": "application/json"},
        ) as response:
            if response.status == 204:
                print(f"Webhook deleted successfully.")
            else:
                print(f"Failed to delete webhook.")


async def delete_webhooks():
    for url in await get_column(await get_DB_path(), "world_chats", "webhook_url"):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                        f"{url[0]}",
                        headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 204:
                        print(f"Webhook deleted successfully.")
                    else:
                        print(f"Failed to delete webhook.")
        except Exception as e:
            print("Well some error, may there be a webhook in db that doesn't exist")
            pass


async def create_embed(server_name: str, author_icon: str, author_url: str, title: str, description: str, icon: str,
                       footer: dict = None,
                       fields: list = None, thumbnail_url: str = None):  # create_embed("Stupid Title", "Stupider
    # description", "Nope", filed1_title="")
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x5643fd,
        timestamp=datetime.datetime.now()
    )
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    # embed.set_author(str(server_name.split("https")), "", str(author_icon))
    embed.set_author(name=server_name, icon_url=author_icon, url=author_url)
    if footer:
        footer_icon = footer.get("icon_url")
        footer_text = footer.get("text")
        embed.set_footer(text=footer_text, icon_url=footer_icon)
    icon, crap = icon.split("https")
    if icon:
        embed.set_image(url=str(icon))
    if fields:
        for field in fields:
            name = field.get('name')
            value = field.get('value')
            inline = field.get('inline', False)
            embed.add_field(name=name, value=value, inline=inline)
    if type(embed) is not discord.Embed:
        print("NOT AN EMBED")
    return embed


async def get_DB_path():
    config = ConfigParser()
    config.read("./source/configuration.cfg")
    if not config.has_section("DB") or not config.has_option("DB", "db_path"):
        if not config.has_section("DB"):
            config.add_section("DB")
        config['DB'] = {
            'db_path': './source/world.db'
        }
        with open('configuration.cfg', 'w') as config_file:
            config.write(config_file)
    db_path = config["DB"]["db_path"]
    return db_path


async def get_DC_token():
    config = ConfigParser()
    config.read("./source/configuration.cfg")
    if not config.has_section("BOT") or not config.has_option("BOT", "token"):
        config.add_section("BOT")
        config['BOT'] = {
            'token': '[REDACTED]'
        }
        with open('configuration.cfg', 'w') as config_file:
            config.write(config_file)
    token = config.get("BOT", "token")
    if token == "[REDACTED]":
        print("EDIT THE CONFIG FILE!!! TOKEN MISSING")
    return token


async def get_current_id(database_name, table_name):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    try:
        await cursor.execute(f"SELECT COUNT(*) FROM {table_name};")  # f"SELECT COUNT(*) FROM {table_name};"
    except Exception as e:
        print(e.with_traceback(e))
    try:
        next_id = await cursor.fetchall()
    except Exception as e:
        print(e.with_traceback(e))
        next_id = None
    try:
        await conn.close()
        if next_id is None:
            print("[FAIL] tools.py")
        else:
            return next_id
    except ValueError as e:
        print(e.with_traceback(e))
    await conn.close()


async def get_next_id(database_name, table_name):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    try:
        await cursor.execute(f"SELECT COUNT(*) FROM {table_name};")  # f"SELECT COUNT(*) FROM {table_name};"
    except Exception as e:
        print(e.with_traceback(e))
    try:
        next_id: list = await cursor.fetchall()
    except Exception as e:
        print(e.with_traceback(e))
        next_id = None
    try:
        await conn.close()
        if next_id is None:
            print("[FAIL] tools.py")
        else:
            try:
                next_number = next_id[0]
                next_number = next_number[0]
                return next_number + 1
            except Exception as e:
                print(e.with_traceback(e))
    except ValueError as e:
        print(e.with_traceback(e))
    await conn.close()


async def create_database(database_name):
    conn = await aiosqlite.connect(database_name)
    await conn.close()


async def create_table(database_name, table_name, *columns):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    column_def = ', '.join(f'{column} TEXT' for column in columns)
    await cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({column_def})')
    await conn.commit()
    await cursor.close()
    await conn.close()


async def insert_data(database_name, table_name, ident, channel_id, webhook_url: str, guild_id: int,
                      server_invite: discord.Asset):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    if not server_invite:
        server_invite = "https://world.killerhase75.com"
    else:
        server_invite = server_invite.url

    await cursor.execute(
        f"INSERT INTO {table_name} (id, channel_id, webhook_url, guild_id, guild_invite) VALUES (?, ?, ?, ?, ?)",
        (ident, channel_id, webhook_url, guild_id, server_invite))
    await conn.commit()
    await cursor.close()
    await conn.close()


async def view_dat_row(database_name, table_name, column, ident):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    await cursor.execute(f'SELECT * FROM {table_name} WHERE {column} = {str(ident)}')
    rows = await cursor.fetchall()
    await cursor.close()
    await conn.close()
    if not rows:
        return None
    else:
        return rows


async def view_data(database_name, table_name, column, value):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    await cursor.execute(f'SELECT * FROM {table_name} WHERE {column} = ?', (value,))
    rows = await cursor.fetchall()
    await cursor.close()
    await conn.close()
    if not rows:
        return None
    else:
        return rows


async def view_data_one(database_name, table_name, column, value, what):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    await cursor.execute(f'SELECT {what} FROM {table_name} WHERE {column} = ?', (value,))
    rows = await cursor.fetchall()
    await cursor.close()
    await conn.close()
    if not rows:
        return None
    else:
        return rows


async def update_data(database_name: str, table_name: str, condition_id: int, new_id: int, channel_id: int,
                      webhook_url: str):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    await cursor.execute(f'UPDATE {table_name} SET id=?, channel_id=?, webhook_url=? WHERE id=?',
                         (new_id, channel_id, webhook_url, condition_id))
    await conn.commit()
    await cursor.close()
    await conn.close()


async def get_column(database_name: str, table_name: str, column: str):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    try:
        await cursor.execute(f'SELECT {column} FROM {table_name}')
    except aiosqlite.OperationalError:
        print("Sqlite get column Failed")
    data = await cursor.fetchall()
    await conn.commit()
    await cursor.close()
    await conn.close()
    if not data:
        return None
    else:
        return data


async def delete_data(database_name, table_name, ident):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    await cursor.execute(f'DELETE FROM {table_name} WHERE channel_id={ident}')
    await conn.commit()
    await cursor.close()
    await conn.close()


async def delete_server_data(database_name, table_name, guild_id):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()
    await cursor.execute(f'DELETE FROM {table_name} WHERE guild_id={guild_id}')
    await conn.commit()
    await cursor.close()
    await conn.close()


async def execute_script(database_name, script):
    conn = await aiosqlite.connect(database_name)
    cursor = await conn.cursor()  # Ey DU? Spring mal zu mir, guck mal, was ich falsch mache, danke ;D
    await cursor.executescript(script)
    await conn.commit()
    await cursor.close()
    await conn.close()


async def check_url(input_str):
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    pattern2 = re.compile(r'^www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if pattern.match(input_str) or pattern2.match(input_str):
        return True
    else:
        return False


async def troll_url():
    link = [
        "https://killerhase75.com",
        "https://www.paypal.me/blocky287",
        "https://paypal.me/Gigagamerreal",
        "https://www.youtube.com/watch?v=xvFZjo5PgG0",
    ]
    selected_link = random.choice(link)
    return selected_link
