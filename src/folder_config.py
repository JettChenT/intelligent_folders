from typing import List
import yaml
from collections import namedtuple
from dataclasses import dataclass 
import os
from pathlib import Path

Directory = namedtuple('Directory', ['path', 'description'])

@dataclass
class FolderConfig:
    dirs: List[Directory]

    def description(self) -> str:
        dr =  '\n'.join([f"{d.path}:{d.description}" for d in self.dirs])
        return "The following directories are available:\n" + dr + "\n"

def load_config(path) -> FolderConfig:
    path = Path(path)
    with open(path) as f:
        data = yaml.safe_load(f)
    dirs = load_dirs(data['folders'])
    for d in dirs:
        tpath = path.parent/d.path
        if not os.path.exists(tpath):
            os.makedirs(tpath)
    return FolderConfig(dirs)
    
def load_dirs(data:list) -> List[Directory]:
    dirs = []
    for item in data:
        if type(item)==dict:
            k,v = item.popitem()
            if type(v) == str:
                dirs.append(Directory(k,v))
            elif type(v) == list:
                for d in load_dirs(v):
                    dirs.append(Directory(k + '/' + d.path, d.description))
        elif type(item)==str:
            dirs.append(Directory(item, item))
    return dirs