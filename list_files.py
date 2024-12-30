# list_files.py
from levels import print_levels
from modules import print_modules
from dojos import print_dojos
from constants import BASE_URL
import globals


def no_flag(resp):
    print("No flag for you..")
    print("You are too deep. Go a few directories up.")

def print_ls_error(resp, flag = "flag{v3ry_s3cret}"):
    print("How did you hack me??")
    print(flag)


def list_files(where = None):
    LS_FUNCTIONS = [print_ls_error, print_dojos, print_modules, print_levels]
    if not where:
        where = globals.pwd
    effective_pwd = where
    filetype = where.count('/') # 1 = "Dojo", 2 = "Module", 3 = "Level" other = "Unknown Type"
    if where == "/":
        effective_pwd = "/dojos"
    if effective_pwd == "/dojos":
        filetype = 1
    else:
        filetype += 1
    try:
        ls_func = LS_FUNCTIONS[filetype]
    except IndexError:
        ls_func = no_flag
    resp = globals.session.get(f"{BASE_URL}{effective_pwd}")
    if resp.status_code != 200:
        print(f"An error occurred while trying to list files in {where}:", f"Status code not 200 ({resp.status_code}).")
        return
    try:
        ls_func(resp.text, where)
    except:
        print(f"An error occurred while trying to list files in {where}:", "Cannot list files in this directory.")


