# globals.config.py
from constants import CONFIG_PATH, SAVE_CREDS_WARNING, SAVED_CREDS_PATH
from utils import clean_path
import globals

import ast
import os

def read_config():
    try:
        with open(CONFIG_PATH, "r") as config_file:
            config_str = config_file.read().strip()
    except FileNotFoundError:
        return False
    if config_str:
        globals.config = ast.literal_eval(config_str)
        return True
    return False
    

def write_config(config):
    with open(CONFIG_PATH, "w") as config_file:
        config_file.write(str(config))

def remember_creds():
    globals.config["remember_creds"] = True
    
    write_config(globals.config)
    print(SAVE_CREDS_WARNING)

def forget_and_remove():
    globals.config["remember_creds"] = False
    os.remove(SAVED_CREDS_PATH)

    write_config(globals.config)
    print("You've been successfully forgotten.")

def set_home(new_home = None):
    if not new_home:
        return
    new_home = clean_path(new_home)
    globals.config["home"] = new_home

    write_config(globals.config)
    print(f"HOME = {new_home}")

def alias(argv1):
    try:
        alias, alias_cmd = argv1.split('=')
    except ValueError:
        print("man alias")
        return

    globals.config["aliases"][alias] = alias_cmd

    write_config(globals.config)
    print(f"Typing {alias} triggers {alias_cmd}.")


