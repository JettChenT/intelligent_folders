from organizer import get_category
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent, FileModifiedEvent
from pathlib import Path
from folder_config import load_config
from global_config import GlobalConfig
import shutil
from watchdog.observers import Observer
import time
from load_file import FileInfo
import uvicorn
from fastapi import FastAPI
from threading import Thread, Event
import logging
import os
import signal


class Handler(FileSystemEventHandler):
    def __init__(self, path: Path, global_config: GlobalConfig, logger: logging.Logger) -> None:
        self.folder_path = path
        self.folder_config = load_config(path/'.forg.yml')
        self.global_config = global_config
        self.logger = logger

    def handle(self, path):
        path = Path(path)
        self.logger.info(f"Handling {path}")
        if path.is_dir():
            return
        if path.name.startswith('.'):
            return
        file = FileInfo(path)
        category = get_category(self.folder_config, file)
        if category is not None:
            self.logger.info(f"Moving {path} to {self.folder_path/category}")
            shutil.move(path, self.folder_path/category)
        else:
            self.logger.info(
                "No category found, please move the file manually")

    def on_created(self, event):
        if type(event) == FileCreatedEvent and Path(event.src_path).parent == self.folder_path:
            self.handle(event.src_path)

    def on_moved(self, event):
        if type(event) == FileMovedEvent and Path(event.dest_path).parent == self.folder_path:
            self.handle(event.dest_path)

    def on_modified(self, event):
        if type(event) == FileModifiedEvent:
            if Path(event.src_path) == self.folder_path/'.forg.yml':
                self.logger.info("reload config")
                self.folder_config = load_config(self.folder_path/'.forg.yml')


global_config = GlobalConfig()
app = FastAPI()
dirs_modified = Event()

@app.get("/status")
async def status():
    return {"status": "ok"}


@app.post("/add-directory")
async def add_dir(dir: str):
    global_config.add_watch_dir(dir)
    dirs_modified.set()
    return {"msg": "added"}


@app.post("/remove-directory")
async def remove_dir(dir: str):
    global_config.remove_watch_dir(dir)
    dirs_modified.set()
    return {"msg": "removed"}


@app.get("/list-directories")
def list_dir():
    dirs = global_config.watch_dirs
    return {"directories": dirs}


@app.post("/stop")
async def stop():
    os.kill(os.getpid(), signal.SIGTERM)


def run_api_server():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file_handler": {
                "class": "logging.FileHandler",
                "filename": str(global_config.get_log_file("api_server")),
                "mode": "a",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["file_handler"],
                "level": logging.INFO,
            },
            "uvicorn.error": {
                "handlers": ["file_handler"],
                "level": logging.INFO,
            },
            "uvicorn.access": {
                "handlers": ["file_handler"],
                "level": logging.INFO,
            },
        },
    }
    try:
        uvicorn.run(app, host="localhost", port=1319, log_config=logging_config)
    except OSError:
        print(
            "Port 1319 is already in use, please make sure it is not used by other programs")
        return
    except:
        raise


def run_file_organizer():
    flag = True
    global_config.set_environs()
    logging.basicConfig(
        filename=global_config.get_log_file("file_organizer"), level=logging.INFO)
    logger = logging.getLogger("File Organizer")
    while flag:
        flag = False
        observers = []
        observer = Observer()
        for path in global_config.watch_dirs:
            observer.schedule(Handler(path, global_config, logger), path)
            observers.append(observer)
        observer.start()

        def stop_observers():
            for o in observers:
                o.unschedule_all()
                o.stop()
        try:
            while True:
                time.sleep(1)
                if dirs_modified.isSet():
                    # restart as the watch dirs have changed
                    flag = True
                    stop_observers()
                    dirs_modified.clear()
                    break
        except KeyboardInterrupt:
            stop_observers()

        for o in observers:
            o.join()


def main():
    threads = [Thread(target=run_api_server),
               Thread(target=run_file_organizer)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
