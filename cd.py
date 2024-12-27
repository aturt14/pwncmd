# cd.py
import globals
from utils import clean_path


def change_directory(dir = None):
    if not dir:
        globals.pwd = globals.config["home"]
        return
    # Absolute path
    if dir.startswith('/'):
        globals.pwd = clean_path(dir)
    else:
        globals.pwd = clean_path(f"{globals.pwd}/{dir}")


