import time
from logger import logger
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from dotenv import load_dotenv
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread

load_dotenv('.env', override=True) 
log = logger()
servers = os.getenv('SERVER_TARGET').split(',')

log.info(f'Available servers'  + str(servers))

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
                response = requests.post(f'{server}/api/upload', data=form_data, files=files)
                response.raise_for_status()
            except Exception as e:
                log.error(f'Failed to upload to server {server}: {e} {filePath}')

class MyEventHandler(PatternMatchingEventHandler):
    def __init__(self, *, patterns = None, ignore_patterns = None, ignore_directories = False, case_sensitive = False):
        super().__init__(ignore_patterns=["*/.*", "*/*mpdf*/*"], ignore_directories=True)
        self.executor = ThreadPoolExecutor(max_workers=100)

    def on_created(self, event: FileSystemEvent) -> None:
        try:
            log.info(f'EVENT:CREATE {event.src_path}')
            self.executor.submit(upload, event.src_path)
        except Exception as ex:
            log.error(f'EXCEPTION: {ex}')

event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, "/App/aii_school_prod/storage/app", recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()