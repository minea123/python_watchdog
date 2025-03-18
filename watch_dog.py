import time
from logger import logger
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from dotenv import load_dotenv
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
import redis

load_dotenv('.env', override=True) 
log = logger()
servers = os.getenv('SERVER_TARGET').split(',')

r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'),  db=os.getenv('REDIS_DB'), decode_responses=True)

CURRENT_SERVER = os.getenv('SERVER_CURRENT')

log.info(f'Available servers'  + str(servers))
log.info(f'Current seerver ' + CURRENT_SERVER)

def upload(filePath: str):
    thread_name = current_thread().name
    log.info(f'Uploading file using thread {thread_name} {filePath}')
    
    form_data = {
        'destination': filePath
    }

    with open(filePath, 'rb') as f:
        files = {'file': f}

        for server in servers:
            try:
                ip = server.replace('http://', '').split(':')[0]
                
                if r.exists(f'{ip}:{filePath}'):
                    log.info(f'NOTICE: file already exists on server {ip}')
                    continue
                response = requests.post(f'{server}/api/upload', data=form_data, files=files)
                response.raise_for_status()
            except Exception as e:
                log.error(f'EXCEPTION: Failed to upload to server {server}: {e} {filePath}')

class MyEventHandler(PatternMatchingEventHandler):
    def __init__(self, *, patterns = None, ignore_patterns = None, ignore_directories = False, case_sensitive = False):
        super().__init__(ignore_patterns=["*/.*", "*/*mpdf*/*"], ignore_directories=True)
        self.executor = ThreadPoolExecutor(max_workers=100)

    def on_created(self, event: FileSystemEvent) -> None:
        try:
            file_size = os.path.getsize(event.src_path)

            if file_size <= 0:
                log.warning('File size is zero byte')

            r.set(f'{CURRENT_SERVER}:{event.src_path}', '')

            log.info(f'EVENT:CREATE {event.src_path}')
            log.info(F'FILE_SIZE {os.path.getsize(event.src_path)}')
            self.executor.submit(upload, event.src_path)
        except Exception as ex:
            log.error(f'EXCEPTION: {ex}')

event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, os.getenv('WATCH_PATH'), recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()