from organizer import get_category
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent, FileModifiedEvent
from pathlib import Path
from folder_config import load_config
from global_config import GlobalConfig
import shutil
from watchdog.observers import Observer
import time
from load_file import FileInfo

class Handler(FileSystemEventHandler):
    def __init__(self, path:Path, global_config:GlobalConfig) -> None:
        self.folder_path = path
        self.folder_config = load_config(path/'.forg.yml')
        self.global_config = global_config
    
    def handle(self, path):
        path = Path(path)
        if path.is_dir():
            return
        if path.name.startswith('.'):
            return
        file = FileInfo(path)
        category = get_category(self.folder_config, file)
        if category is not None:
            print(f"Moving {path} to {self.folder_path/category}")
            shutil.move(path, self.folder_path/category)
        else:
            print("No category found, please move the file manually")

    def on_created(self, event):
        if type(event) == FileCreatedEvent and Path(event.src_path).parent == self.folder_path:
            self.handle(event.src_path)
    
    def on_moved(self, event):
        if type(event) == FileMovedEvent and Path(event.dest_path).parent == self.folder_path:
            self.handle(event.dest_path)
    
    def on_modified(self, event):
        if type(event) == FileModifiedEvent:
            if Path(event.src_path) == self.folder_path/'.forg.yml':
                print("reload config")
                self.folder_config = load_config(self.folder_path/'.forg.yml')



def run():
    flag = True
    global_config = GlobalConfig()
    global_config.set_environs()
    while flag:
        flag = False
        observers = []
        observer = Observer()
        for path in global_config.watch_dirs:
            observer.schedule(Handler(path, global_config), path)
            observers.append(observer)
        observer.start()

        def stop_observers():
            for o in observers:
                o.unschedule_all()
                o.stop()

        try:
            while True:
                time.sleep(1)
                if global_config.update_watch_dirs():
                    # restart as the watch dirs have changed
                    flag = True
                    stop_observers()
                    break
        except KeyboardInterrupt:
            stop_observers()

        for o in observers:
            o.join()


if __name__ == "__main__":
    run()