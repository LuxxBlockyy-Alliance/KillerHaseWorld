from flask import Flask, jsonify, request, render_template
import json
from rich.console import Console

console = Console()
app = Flask(__name__, template_folder='website')

@app.route('/access/admin/panel')
async def index():
    return render_template('index.html')


@app.route('/access/backend/api', methods=['GET', 'POST'])
async def handle_input():
    if request.method == 'GET':
        return render_template('api_get.html'), 200
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        message = data['message']

        return jsonify({'result': "result"}), 400


def start_server(host: str = "127.0.0.1", port: int = 8001, debug: bool = True):
    app.run(debug=debug, port=port, host=host)


start_server()
