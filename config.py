from typing import List
import yaml
from collections import namedtuple
from dataclasses import dataclass 
import os

Directory = namedtuple('Directory', ['path', 'description'])

@dataclass
class Config:
    dirs: List[Directory]

    def description(self) -> str:
        dr =  '\n'.join([f"{d.path}:{d.description}" for d in self.dirs])
        return "The following directories are available:\n" + dr + "\n"

def load_config(path:str) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    dirs = load_dirs(data['folders'])
    for d in dirs:
        if not os.path.exists(d.path):
            os.makedirs(d.path)
    return Config(dirs)
    
def load_dirs(data:list) -> List[Directory]:
    dirs = []
    for item in data:
        item:dict
        k,v = item.popitem()
        if type(v) == str:
            dirs.append(Directory(k,v))
        elif type(v) == list:
            for d in load_dirs(v):
                dirs.append(Directory(k + '/' + d.path, d.description))
    return dirs