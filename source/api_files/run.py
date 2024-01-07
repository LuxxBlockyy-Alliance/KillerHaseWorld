from datetime import datetime

import aiohttp
import discord
from discord import Webhook
from flask import Flask, jsonify, request, render_template
import json
from rich.console import Console

from source import tools

console = Console()
app = Flask(__name__, template_folder='website')


async def send_global_broadcast(message: str):
    webhook_session = aiohttp.ClientSession()
    from source.tools import get_column
    for url in await get_column("../world.db", "world_chats", "webhook_url"):
        try:
            webhook = Webhook.from_url(str(url), session=webhook_session)
            e = discord.Embed(
                title="🚀 BROADCAST 🚀",
                description=f"{message}",
                timestamp=datetime.now(),
                color=discord.Colour.red()
            )
            e.set_footer(text=" ✅ Dies ist eine offizielle Nachricht ✅")
            await webhook.send(embed=e, avatar_url="https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png")
        except discord.NotFound as e:
            print(
                "Es ist ein Fehler aufgetreten. Möglicherweise gibt es einen Webhook in der Datenbank, der nicht vorhanden ist.")
            pass


@app.route('/')
async def index():
    return render_template('index.html')


@app.route('/access/backend/api/send_broadcast', methods=['GET', 'POST'])
async def handle_input():
    if request.method == 'GET':
        return render_template('api_get.html'), 200
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        message = data['message']
        await tools.send_global_broadcast(message)

        return jsonify({'result': "result"}), 400


def start_server(host: str = "172.17.0.3", port: int = 8001, debug: bool = True):
    app.run(debug=debug, port=port, host=host)


start_server()
