import time
from logger import logger
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from dotenv import load_dotenv
import os

load_dotenv('.env')

log = logger()

class MyEventHandler(PatternMatchingEventHandler):
    def __init__(self, *, patterns = None, ignore_patterns = None, ignore_directories = False, case_sensitive = False):
        super().__init__(ignore_patterns=["*/.*", "mpdf"], ignore_directories=True)
        self.file_handle = open(os.getenv('APPEND_LOG'), 'a')

    def on_created(self, event: FileSystemEvent) -> None:
        try:
            log.info(f'EVENT:CREATE {event.src_path}')
            self.file_handle.write(f'CREATE:{event.src_path}\n')
            self.file_handle.flush()
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