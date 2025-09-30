# auto_reload.py
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(["python", self.script])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Arquivo modificado: {event.src_path}, reiniciando app...")
            self.start_app()

if __name__ == "__main__":
    script = "app.py"  # seu arquivo principal
    path = os.path.dirname(os.path.abspath(script))
    
    event_handler = RestartHandler(script)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
