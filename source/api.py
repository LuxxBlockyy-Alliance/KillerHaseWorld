import threading
from source import run


def start():
    thread = threading.Thread(target=run.start_server)
    thread.start()