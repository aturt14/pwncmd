# cd.py
import globals
from utils import resolve_path



def change_directory(dir = None):
    if not dir:
        globals.pwd = globals.config["home"]
        return
    globals.pwd = resolve_path(dir) 
