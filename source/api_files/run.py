from flask import Flask, jsonify, request, render_template
import json
from rich.console import Console

from source import tools

console = Console()
app = Flask(__name__, template_folder='website')


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