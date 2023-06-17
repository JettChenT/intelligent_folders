import platformdirs
from pathlib import Path
import os 
import yaml
import editor

APP_NAME = "FORG"
APP_AUTHOR = "JettChen"

def get_loc() -> Path:
    path =  Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))
    if not path.exists():
        os.makedirs(path)
    return path

def get_config_loc():
    loc =  get_loc() / "config.yml"
    # print(loc)
    if not loc.exists():
        print(f"Please insert your config file in {loc}")
        with open(loc, 'w') as f:
            f.write("# This is the config file for FORG, please insert your OPENAI API KEY here\n")
            f.write("openai:\n")
            f.write("  OPENAI_API_KEY: YOUR_API_KEY\n")
        print(f"Please insert your OPENAI API KEY in {loc}")
        editor.editor(filename=loc)
    return loc

def get_watch_dirs():
    loc = get_loc() / "watch_dirs.txt"
    if not loc.exists():
        open(loc, 'w').close()
    lines = open(loc).readlines()
    return [Path(l.strip()) for l in lines]

def add_watch_dir(dir:Path):
    loc = get_loc() / "watch_dirs.txt"
    with open(loc, 'a') as f:
        f.write(str(dir) + "\n")

def remove_watch_dir(dir:Path):
    loc = get_loc() / "watch_dirs.txt"
    lines = open(loc).readlines()
    lines = [l.strip() for l in lines]
    lines.remove(str(dir))
    with open(loc, 'w') as f:
        f.write("\n".join(lines))

class GlobalConfig:
    def __init__(self):
        # TODO: allow for more models in the future
        self.model_choice = "openai"
        self.openai_cfig = {}
        self.watch_dirs = get_watch_dirs() 
        tmp:dict = yaml.safe_load(open(get_config_loc()))
        if 'openai' in tmp.keys():
            self.openai_cfig = tmp['openai']
    
    def set_environs(self):
        for k,v in self.openai_cfig.items():
            if os.environ.get(k) is None:
                os.environ[k] = v
    
    def add_watch_dir(self, dir:Path):
        """Add a directory to watch"""
        self.watch_dirs.append(dir.resolve())
        add_watch_dir(dir)
    
    def remove_watch_dir(self, dir:Path):
        """Remove a directory from watch"""
        self.watch_dirs.remove(dir.resolve())
        remove_watch_dir(dir)
    
    def update_watch_dirs(self) -> bool:
        """Update the watch directories"""
        old = self.watch_dirs
        self.watch_dirs = get_watch_dirs()
        return old != self.watch_dirs
    
    def get_app_path(self) -> Path:
        return get_loc()
    
    def get_log_file(self, cat:str="") -> Path:
        return (get_loc()/f"{cat}log.txt").resolve()
 