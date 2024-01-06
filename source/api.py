import asyncio
import threading
from api_files import run


def start():
    thread = threading.Thread(target=run.start_server)
    thread.start()
    thread.join()