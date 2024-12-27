# shell.py
from help import help, man
from config import alias, forget_and_remove, set_home, remember_creds, forget_and_remove, read_config, write_config
from auth import login, logout
from challenge import start_challenge, practice_challenge
from profile import view_profile
from dojos import show_dojos
from list_files import list_files
from levels import print_level_description
from cd import change_directory
from flag import submit_flag
from utils import clear_screen, save_and_quit
from constants import COLOR1, COLOR2, COLOR3, CMD_NOT_FOUND_MSG, HISTORY_PATH
import globals

from colorama import Style
import readline


def resolve_cmd(cmd_str):
    ONE_ARG = {"cd", "set-home", "desc", "x/s", "start", "s", "practice", "p", "alias", "man", "flag"}
    commands = {
        "help" : help,
        "?" : help,
        "man" : man,
        "alias" : alias,
        "login" : login,
        "logout" : logout,
        "start" : start_challenge,
        "s" : start_challenge,
        "practice" : practice_challenge,
        "p" : practice_challenge,
        "profile" : view_profile,
        "dojos" : show_dojos,
        "ls" : list_files,
        "set-home" : set_home,
        "remember-me" : remember_creds,
        "forget" : forget_and_remove,
        "cd" : change_directory,
        "desc" : print_level_description,
        "x/s" : print_level_description, # gdb vibes
        "flag" : submit_flag,
        "clear" : clear_screen,
        "q" : save_and_quit,
        ":x" : save_and_quit,
        "exit" : save_and_quit,
        "quit" : save_and_quit,
    } 
    try:
        cmd = cmd_str.split()
        argv0 = cmd[0]
        cmd_func = commands[argv0]
    except KeyError:
        try:
            cmd = globals.config["aliases"][cmd_str]
            argv0 = cmd[0]
            cmd_func = commands[argv0]
        except KeyError:
            print(CMD_NOT_FOUND_MSG, cmd_str)
            return
    if len(cmd) > 1 and argv0 in ONE_ARG:
        cmd_func("".join(cmd[1:]))
    else:
        cmd_func()
    
def prompt():
    if globals.logged_in:
        prompt_str = f"{COLOR1}({Style.RESET_ALL}{COLOR3}pwncmd{Style.RESET_ALL}{COLOR1}@{Style.RESET_ALL}{COLOR2}{globals.username}{Style.RESET_ALL}{COLOR1})-[{Style.RESET_ALL}{globals.pwd}{COLOR1}]{Style.RESET_ALL}\n{COLOR2}>>{Style.RESET_ALL} "
    else:
        prompt_str = f"{COLOR1}({Style.RESET_ALL}{COLOR3}pwncmd{Style.RESET_ALL}{COLOR1})-[{Style.RESET_ALL}{globals.pwd}{COLOR1}]{Style.RESET_ALL}\n{COLOR2}>>{Style.RESET_ALL} "

    return input(prompt_str).strip()

def interactive_shell():
    if not read_config():
        write_config(globals.config)
    globals.pwd = globals.config["home"]

    try:
        readline.read_history_file(HISTORY_PATH)
    except FileNotFoundError:
        pass 
    try:
        while True:
            cmd = prompt()
            if cmd: 
                readline.add_history(cmd)
                resolve_cmd(cmd)
    except KeyboardInterrupt:
        save_and_quit()


