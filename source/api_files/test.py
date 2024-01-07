import requests

response = requests.post('http://127.0.0.1:8001/access/backend/api/send_broadcast', json={'message':'Hello World!'})