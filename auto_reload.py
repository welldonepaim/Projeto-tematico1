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
    script_name = "app.py" 
    
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    script_path = os.path.join(base_dir, script_name)
    
    path_to_watch = base_dir 
    
    
    event_handler = RestartHandler(script_path) 
    
    observer = Observer()
    
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
