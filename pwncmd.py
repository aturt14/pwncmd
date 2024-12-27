#!/usr/bin/env python

from re import error
import re
import requests
import sys
import os
import base64
import ast
import shutil
import getpass
import readline
import json

from bs4 import BeautifulSoup
from prettytable import PrettyTable
from colorama import Fore, Style

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Shows in which dojo you currently are, e.g. you could go to Program Security, then pwd would be /Program Security
pwd = "/"

BASE_URL = "https://pwn.college"
LOGIN_URL = f"{BASE_URL}/login?next=/?"
PROFILE_URL = f"{BASE_URL}/hacker/" # This url needs for some reason to end with /
DOJOS_URL = f"{BASE_URL}/dojos"
START_CHALLENGE_URL = f"{BASE_URL}/pwncollege_api/v1/docker"
SUBMIT_FLAG_URL = f"{BASE_URL}/api/v1/challenges/attempt"

LOGIN_ERR_MSG = "An error occurred while trying to login:"
CMD_NOT_FOUND_MSG = "This command does not exist:"
PROFILE_ERR_MSG = "Could not reach your profile. Are you logged in?"
DOJOS_ERR_MSG = "An error occurred while getting dojos:"


SAVE_CREDS_WARNING = "You set remember creds to true. Be aware that this might not be secure."

INSECURE_KEY = bytes.fromhex("cafebabedeadbeef133713370ff1cebadbadbadbadcafebadbadbaddeadbeeff")

SAVED_CREDS_PATH = "./.login"
CONFIG_PATH = "./.config"
HISTORY_PATH = './.pwncmd_history'

config = {"remember_creds" : False, "home" : "/", "aliases" : {}}
logged_in = False

current_level_descriptions = {"pwd" : "aaah"}
current_level_ids = {"pwd" : "aaah"}
current_level_cids = {"pwd" : "aaah"}
is_solved = {"pwd" : "aaah"}
running_level = None

username = None


# Global session
session = requests.Session()

def clear_screen():
    os.system("clear") # You better not use windows

############# PROFILE ################

def print_awards(awards):
    for award in awards:
        print(award)

def print_profile(name, belt, awards):
    print(f"Username: {name}")
    if belt:
        print(f"Belt: {belt}")
    if awards:
        print_awards(awards)

def get_profile_info(profile_html):
    soup = BeautifulSoup(profile_html, 'html.parser')
    name_element = soup.find('h1')
    if not name_element:
        print(PROFILE_ERR_MSG, f"Error occurred while trying to find username. Response: {profile_html}")
        return
    name = name_element.text
    belt_element = soup.find("img", {"class" : "scoreboard-belt"})
    belt = None
    if belt_element:
        belt = belt_element.get("src")
        if belt:
            belt = belt[35:belt.find('.')]
    awards = None
    h2 = soup.find("h2")
    if h2:
        awards_elements = h2.find_all("span", title=True)
        awards = [award.get("title") for award in awards_elements]

    return name, belt, awards

############# LOGIN ###############

def ask_for_creds():
    username = input("Username or email: ")
    password = getpass.getpass("Password: ")

    return username, password

def get_nonce():
    global session
    resp = session.get(LOGIN_URL)
    if resp.status_code != 200:
        print(LOGIN_ERR_MSG, resp.text)
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    nonce_input = soup.find('input', {'id' : 'nonce'})
    if nonce_input:
        nonce = nonce_input.get('value')
        return nonce
    print(LOGIN_ERR_MSG, "Could not find nonce!")
    return None

def creds_incorrect(resp_html):
    soup = BeautifulSoup(resp_html, 'html.parser')
    incorrect = soup.find("span", string="Your username or password is incorrect")
    if incorrect:
        return True
    return False

######## SAVE LOGIN ########

def encrypt(plain_text, key):
    iv = os.urandom(16)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()
    
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    
    return base64.b64encode(iv).decode('utf-8'), base64.b64encode(encrypted).decode('utf-8')

# Function to decrypt a string
def decrypt(iv, encrypted_text, key):
    iv = base64.b64decode(iv)
    encrypted_text = base64.b64decode(encrypted_text)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    padded_data = decryptor.update(encrypted_text) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plain_text = unpadder.update(padded_data) + unpadder.finalize()
    
    return plain_text.decode('utf-8')

def encrypt_creds(creds):
    username, password = creds
    creds_string = f"{username}\n{password}"
    return encrypt(creds_string, INSECURE_KEY)

def save_creds(creds):
    # Encrypt creds - note that this is NOT safe, if somebody gains access to this file, they will be able to decrypt them. However, storing passwords in plaintext is much worse.
    iv, encrypted_creds = encrypt_creds(creds)
    with open(SAVED_CREDS_PATH, "w") as creds_file:
        creds_file.write(f"{iv}\n{encrypted_creds}")

def decrypt_creds(iv, encrypted_creds):
    pt = decrypt(iv, encrypted_creds, INSECURE_KEY)
    username, password = pt.splitlines()
    return username, password

def load_creds():
    try:
        with open(SAVED_CREDS_PATH, "r") as creds_file:
            iv, encrypted_creds = creds_file.read().splitlines()
    except FileNotFoundError:
        return None, None
    if iv and encrypted_creds:
        username, password = decrypt_creds(iv, encrypted_creds)
    else: return None, None
    return username, password
        

########## CONFIG ##########

def read_config():
    global config
    try:
        with open(CONFIG_PATH, "r") as config_file:
            config_str = config_file.read().strip()
    except FileNotFoundError:
        return False
    if config_str:
        config = ast.literal_eval(config_str)
        return True
    return False
    

def write_config(config):
    with open(CONFIG_PATH, "w") as config_file:
        config_file.write(str(config))

def remember_creds():
    global config
    config["remember_creds"] = True
    
    write_config(config)
    print(SAVE_CREDS_WARNING)

def forget_and_remove():
    global config
    config["remember_creds"] = False
    os.remove(SAVED_CREDS_PATH)

    write_config(config)
    print("You've been successfully forgotten.")

def set_home(new_home = None):
    if not new_home:
        return
    global config
    new_home = clean_path(new_home)
    config["home"] = new_home

    write_config(config)
    print(f"HOME = {new_home}")

def alias(argv1):
    try:
        alias, alias_cmd = argv1.split('=')
    except ValueError:
        print("man alias")
        return

    global config
    config["aliases"][alias] = alias_cmd

    write_config(config)
    print(f"Typing {alias} triggers {alias_cmd}.")

########### GETTING HELP ############

def help():
    print("Commands:")
    cmds = """        "help" or "?" - Shows this text.
        "man <cmd_name>" - Manual for <cmd_name>.
        "alias" - Create an alias for a command.
        "login" Log into you pwn.college account.
        "logout" - Log out of your pwn.college account.
        "start <level_name>" or "s <level_name>" - Start <level_name>..
        "practice <level_name>" or "p <level_name>" - Practice <level_name>.
        "profile" - Check out your fantastic stats.
        "dojos" - Show dojos.
        "ls" - List dojos/modules/levels in working directory.
        "set-home" - Set default home path.
        "remember-me" - Remember login credentials.
        "forget" - Forget and remove login credentials.
        "cd" - Change working directory.
        "desc <level_name>" or "x/s <level_name>" - Print description of <level_name>.
        "q" or ":x" or "exit" or "quit" - Exit.
    """
    print(cmds)
    print("If something doesn't work as expected, RTFM.")
    print("If you are sure it is an error in the code, submit an issue to GitHub.")

def man(cmd_name):
    MAN_HELP = """Displays the list of available commands."""

    MAN_MAN = """
    Shows the manual for a specific command.
    Example:

    (pwncmd)-[/]
    >> man man

        Shows the manual for a specific command.
        Example:

        (pwncmd)-[/]
        >> man man

            Shows the manual for a specific command.
            Example:

            (pwncmd)-[/]
            >> man man

                Shows the manual for a specific command.
                Example:
                    RecursionError
    """
    MAN_ALIAS = """
    Creates an alias for a command. 
    Example:

    (pwncmd)-[/]
    >> alias li=login
    Typing li triggers login.
    """
    MAN_LOGIN = """
    Logs into your pwn.college account. If you don't have remember-me on, login will prompt you for username/email and password.
    Example with remember-me:

    (pwncmd)-[/]
    >> login
    You set remember creds to true. Be aware that this might not be secure.
    Logged in successfully as hacker!
    
    Example without remember-me:

    (pwncmd)-[/]
    >> login
    Username or email: 1337hacker
    Password:
    Logged in successfully as 1337hacker!
    """
    MAN_LOGOUT = """
    Logs out of your pwn.college account.
    """
    MAN_START = """
    Starts the specified level. If you are not logged in, it will run login first.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> s level1
    Starting level1 in file-struct-exploits in software-exploitation...
    level1 started successfully!
    """
    MAN_PRACTICE = """
    Runs the specified level in practice mode.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> p level1
    Starting level1 in file-struct-exploits in software-exploitation...
    level1 started successfully!
    """
    MAN_PROFILE = """
    Displays your statistics. If you are not logged in, it will login automatically.
    Example:

    (pwncmd)-[/]
    >> profile
    Username: 1337hacker
    Belt: black
    Awarded for completing the Pwntools Tutorials dojo.
    """
    MAN_DOJOS = """
    Shows the available dojos.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> dojos
    ====== Getting Started =====
    +-----------------------+----------+-------------------+
    | Dojo                  | Progress |              Path |
    +-----------------------+----------+-------------------+
    | Getting Started       | 100.0 %  |          /welcome |
    | Linux Luminarium      |  1.19 %  | /linux-luminarium |
    | Computing 101         | 71.21 %  |    /computing-101 |
    | Playing With Programs | 52.11 %  |     /fundamentals |
    +-----------------------+----------+-------------------+
    ====== Core Material =====
    +------------------------+----------+-------------------------+
    | Dojo                   | Progress |                    Path |
    +------------------------+----------+-------------------------+
    | Intro to Cybersecurity | 74.44 %  | /intro-to-cybersecurity |
    | Program Security       | 100.0 %  |       /program-security |
    | System Security        | 84.21 %  |        /system-security |
    | Software Exploitation  | 38.73 %  |  /software-exploitation |
    +------------------------+----------+-------------------------+
    ====== Community Material =====
    ...
    """
    MAN_LS = """
    Lists dojos, modules, or levels in the current directory. This is an essential command for pwncmd. When you change directory (man cd) and want to see what dojos, modules or levels are there, you use ls. Note that ls can NOT be used with an argument. You always need to cd first.
    Example:

    (pwncmd)-[/software-exploitation]
    >> ls
    Printing modules..
    +--------------------------------+----------+--------------------------------------------------------+
    | Module                         | Progress | Path                                                   |
    +--------------------------------+----------+--------------------------------------------------------+
    | Return Oriented Programming    |  100.0 % | /software-exploitation/return-oriented-programming/    |
    | Format String Exploits         |  100.0 % | /software-exploitation/format-string-exploits/         |
    | File Struct Exploits           |   65.0 % | /software-exploitation/file-struct-exploits/           |
    | Dynamic Allocator Misuse       |    0.0 % | /software-exploitation/dynamic-allocator-misuse/       |
    | Exploitation Primitives        |    0.0 % | /software-exploitation/memory-mastery/                 |
    | Dynamic Allocator Exploitation |    0.0 % | /software-exploitation/dynamic-allocator-exploitation/ |
    | Microarchitecture Exploitation |    0.0 % | /software-exploitation/speculative-execution/          |
    | Kernel Exploitation            |    0.0 % | /software-exploitation/kernel-exploitation/            |
    +--------------------------------+----------+--------------------------------------------------------+
    """
    MAN_SETHOME = """
    Sets the default home path to argv[1]. This is useful when you are currently working on a specific module - you can set your home there and then every time you start pwncmd, you will be right there.
    Example:

    (pwncmd)-[/]
    >> set-home /software-exploitation/file-struct-exploits
    HOME = /software-exploitation/file-struct-exploits
    """
    MAN_REMEMBERME = """
    Remembers your login credentials. The credentials are saved in ./.login and are encrypted using AES-256. This unfortunately doesn't guarantee them any security, as the key is hardcoded. Be aware of that if you are going to use it.
    Example:

    (pwncmd)-[/]
    >> remember-me
    You set remember creds to true. Be aware that this might not be secure.
    """
    MAN_FORGET = """
    Forgets and removes your login credentials if you saved them using remember-me.
    Example:

    (pwncmd)-[/]
    >> forget
    You've been successfully forgotten.
    """
    MAN_CD = """
    Changes the working directory to argv[1]. If no arguments given, changes working directory to home (see man set-home). You can use either absolute or relative paths. 
    pwncmd works on a similar principle as UNIX's filesystem. Each route on pwn.college which contains either dojos, modules or levels can be interpreted as a directory which contains those files. When you cd to e.g. software-exploitation, you can then use ls to list all the modules there. In order to start a challenge, you need to have pwd = dojo/module_of_the_chall.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> cd ..
    (pwncmd)-[/software-exploitation]
    >> cd dynamic-allocator-misuse
    (pwncmd)-[/software-exploitation/dynamic-allocator-misuse]
    >>
    You can see the current working directory at \\(pwncmd\\)-\\[(.*)\\]
    """
    MAN_DESCRIPTION = """
    Prints the description of the specified level. When your working directory contains levels, you can print the description of a specified one using desc <level_name> or x/s <level_name>.
    Example:

    (pwncmd)-[/software-exploitation/dynamic-allocator-misuse]
    >> x/s level1.0
    Exploit a use-after-free vulnerability to get the flag.
    """
    MAN_FLAG = """
    Asks for the flag for currently running challenge. If no challenge is running, an argument is reqired (level name).
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> flag level1
    You set remember creds to true. Be aware that this might not be secure.
    Logged in successfully as 1337hack3r!
    Flag: pwn.college{test}
    You already solved this
    """
    MAN_EXIT = """
    Exits the application.
    """

    man_entries = {
        "help" : MAN_HELP,
        "?" : MAN_HELP,
        "man" : MAN_MAN,
        "alias" : MAN_ALIAS,
        "login" : MAN_LOGIN,
        "logout" : MAN_LOGOUT,
        "start" : MAN_START,
        "s" : MAN_START,
        "practice" : MAN_PRACTICE,
        "p" : MAN_PRACTICE,
        "profile" : MAN_PROFILE,
        "dojos" : MAN_DOJOS,
        "ls" : MAN_LS,
        "set-home" : MAN_SETHOME,
        "remember-me" : MAN_REMEMBERME,
        "forget" : MAN_FORGET,
        "cd" : MAN_CD,
        "desc" : MAN_DESCRIPTION,
        "x/s" : MAN_DESCRIPTION,
        "flag" : MAN_FLAG,
        "q" : MAN_EXIT,
        ":x" : MAN_EXIT,
        "exit" : MAN_EXIT,
        "quit" : MAN_EXIT,
    }
    try: 
        print(man_entries[cmd_name])
    except KeyError:
        help()

def login():
    global session, logged_in, username
    nonce = get_nonce()
    if not nonce:
        print("Login failed..")
        return
    if not config["remember_creds"]:
        username, password = ask_for_creds()
    else:
        print(SAVE_CREDS_WARNING)
        username, password = load_creds()
        if not (username and password):
            username, password = ask_for_creds()
    login_data = {
        "name" : username,
        "password" : password,
        "_submit" : "Submit",
        "nonce" : nonce,
    }
    resp = session.post(LOGIN_URL, data=login_data)
    if resp.status_code != 200:
        print(LOGIN_ERR_MSG, f"POST request failed: {resp.text}")
        username = None
        return
    if creds_incorrect(resp.text):
        print(LOGIN_ERR_MSG, "Incorrect credentials!")
        username = None
        return
    if config["remember_creds"]:
        save_creds((username, password))
    print(f"Logged in successfully as {username}!")
    logged_in = True
    
    
def logout():
    global logged_in, session
    logged_in = False
    session = requests.Session()

def get_csrf_token():
    global session, pwd
    resp = session.get(f"{BASE_URL}{pwd}")
    if resp.status_code != 200:
        print("Error when trying to fetch CSRF token.")
        return

    """
    'csrfNonce': "9c1cefaea69d32613557c9d9974f778468cad975ea0a2abfe3517c32ec769609"
    """
    regex = r"'csrfNonce':\s\"([a-fA-F0-9]{64})\""
    match = re.search(regex, resp.text)

    if match:
        csrf_token = match.group(1)
        return csrf_token
    else:
        print(f"CSRF token not found at {BASE_URL}{pwd}..")

def update_level_info():
    global pwd
    resp = session.get(f"{BASE_URL}{pwd}")
    if resp.status_code != 200:
        print(f"Could not fetch {BASE_URL}{pwd}!")
        return None
    parse_levels(resp.text)

def get_level_id_by_name(level_name):
    global current_level_ids, current_level_cids, pwd
    if current_level_ids["pwd"] != pwd:
        update_level_info()
    try:
        return current_level_ids[level_name]
    except:
        if level_name in current_level_ids.values():
            return level_name
        print(f"{level_name} doesn't seem to be a vaild level name in {pwd}.")
        return None

def start_challenge(level_name = None, practice = False):
    if not level_name:
        print("Not starting anything.")
        return
    global pwd, session, running_level
    
    # Levels have different id's than names..
    level_id = get_level_id_by_name(level_name) 

    if not level_id:
        return

    if not logged_in:
        login()

    # We need to get anti csrf token first
    csrf_token = get_csrf_token()
    rheaders = {"CSRF-Token" : csrf_token}
    pwd_data = pwd.split('/')
    try:
        challenge_data = {
            "challenge" : level_id,
            "dojo" : pwd_data[1],
            "module" : pwd_data[2],
            "practice" : practice,
        }
    except IndexError:
        print(f"Go to a directory with challenges.")
        return

    resp = session.post(START_CHALLENGE_URL, json=challenge_data, headers=rheaders)
    print(f"Starting {level_name} in {pwd_data[2]} in {pwd_data[1]}...")

    if resp.status_code != 200:
        print(f"There was a problem starting the challenge. Check your network connection and if the details are correct.")
        print(resp.text)
        print(resp.status_code)
        return
    running_level = level_name
    print(f"{level_name} started successfully!")

def practice_challenge(level_name):
    start_challenge(level_name, True)

def get_level_cid_by_name(level_name):
    global current_level_cids, pwd
    if current_level_cids["pwd"] != pwd:
        update_level_info()
    try:
        return current_level_cids[level_name]
    except:
        print(f"{level_name} doesn't seem to be a vaild level name in {pwd}.")
        return None



def submit_flag(level_name = None):
    global running_level, session
    if not logged_in:
        login()
    if not level_name and running_level:
        level_name = running_level
    elif not (running_level or level_name):
        print(f"argv[1] should be the level name.")
        return
    challenge_cid = get_level_cid_by_name(level_name)
    flag = input("Flag: ")
    csrf_token = get_csrf_token()
    flag_headers = {"CSRF-Token" : csrf_token}
    flag_data = {
        "challenge_id" : challenge_cid,
        "submission" : flag,
    }
    resp = session.post(SUBMIT_FLAG_URL, json=flag_data, headers=flag_headers)
    if resp.status_code != 200:
        print(f"Error when fetching {SUBMIT_FLAG_URL}. Status code: {resp.status_code}, response: {resp.text}.")
        return
    resp_json = resp.json()
    try:
        print(resp_json["data"]["message"])
    except:
        print(f"Response in weird format: {resp.text}")
    
    
     

def view_profile():
    global session
    if not logged_in:
        login()
    resp = session.get(PROFILE_URL)
    if resp.status_code != 200:
        print(PROFILE_ERR_MSG, resp.text, f"\n{resp.status_code = }")
        return
    name, belt, awards = get_profile_info(resp.text)
    
    print_profile(name, belt, awards)

####### SHOW DOJOS #######
   
def show_dojos():
    global session
    resp = session.get(DOJOS_URL)
    if resp.status_code != 200:
        print(DOJOS_ERR_MSG, f"Status code not 200 ({resp.status_code}).")
        return
    print_dojos(resp.text)

########### CHANGE DIRECTORY ############

def clean_path(input_path):
    normalized_path = os.path.normpath(input_path)
    valid_path = normalized_path
    
    return valid_path.replace("//", '/')

def change_directory(dir = None):
    global pwd
    if not dir:
        pwd = config["home"]
        return
    # Absolute path
    if dir.startswith('/'):
        pwd = clean_path(dir)
    else:
        pwd = clean_path(f"{pwd}/{dir}")

########## LIST DIRECTORY ############

def parse_dojos(dojos_html):
    soup = BeautifulSoup(dojos_html, 'html.parser')
    scategories = soup.find_all("h2")
    categories = [category.text for category in scategories]
    sdojos = soup.find_all("ul", {"class" : "card-list"})
    names_by_category, progresses_by_category, paths_by_category = {}, {}, {}

    for i, category in enumerate(categories):
        names = [name.text for name in sdojos[i].find_all('h4', {'class' : 'card-title'})]
        progresses = [progress.get("style").split(':')[1].strip('%') for progress in sdojos[i].find_all("div", {"class" : "progress-bar"})]
        paths = [path.get("href") for path in sdojos[i].find_all("a", {"class" : "text-decoration-none"})]

        names_by_category[category] = names
        progresses_by_category[category] = progresses
        paths_by_category[category] = paths
    return categories, names_by_category, progresses_by_category, paths_by_category
    
def print_dojos(dojos_html):
    categories, names_by_category, progresses_by_category, paths_by_category = parse_dojos(dojos_html)
    
    for category in categories:
        print(f"====== {category} =====")
        
        table = PrettyTable()
        table.field_names = ["Dojo", "Progress", "Path"] if logged_in else ["Dojo", "Path"]
        table.align["Dojo"] = "l"
        table.align["Path"] = "r"
        if logged_in:
            table.align["Progress"] = "c" 
        
        for name, progress, path in zip(names_by_category[category], progresses_by_category[category], paths_by_category[category]):
            path = path.replace("/dojo", "")
            if logged_in:
                progress = round(float(progress), 2)
                table.add_row([name, f"{progress} %", path])
            else:
                table.add_row([name, path])
        
        print(table)
 

def no_flag(resp):
    print("No flag for you..")
    print("You are too deep. Go a few directories up.")

def print_ls_error(resp, flag = "flag{v3ry_s3cret}"):
    print("How did you hack me??")
    print(flag)

def print_colored_level(name, end = '\n'):
    global is_solved, running_level
    if name == running_level:
        print(f"{Fore.YELLOW}{name}{Style.RESET_ALL}", end = end)
    elif is_solved.get(name, False):
        print(f"{Fore.GREEN}{name}{Style.RESET_ALL}", end = end)
    else:
        print(f"{Fore.WHITE}{name}{Style.RESET_ALL}", end = end)


def print_levels(levels_html):
    global pwd, is_solved, running_level
    names, _ = parse_levels(levels_html)  

    if not names:
        print(f"No levels found in {pwd}.")
        return

    terminal_width = shutil.get_terminal_size().columns

    print(f"Levels in {pwd}:")
    print("-" * terminal_width)
    

    sorted_names = names

    mid_index = len(sorted_names) // 2 + len(sorted_names) % 2
    column1 = sorted_names[:mid_index]
    column2 = sorted_names[mid_index:]

    for level1, level2 in zip(column1, column2):
        print_colored_level(level1, end = (16 - len(level1)) * ' ')
        print_colored_level(level2)

    print("-" * terminal_width)

def parse_levels(levels_html):
    global current_level_descriptions, current_level_ids, current_level_cids, is_solved, pwd
    soup = BeautifulSoup(levels_html, 'html.parser')
    challenges = soup.find("div", {"id" : "challenges"})
    if not challenges:
        return None, None

    names = [name for name in challenges.find_all('span', {'class' : 'd-sm-block d-md-block d-lg-block'})]

    is_solved = {name.text.strip() : (name.find("i", {"class" : True}).get("class")[3].find("unsolved") == -1) for name in names if name.text.strip() != "Start" and name != "Practice"}
    names = [name.text.strip() for name in names if name.text.strip() != "Start" and name.text.strip() != "Practice"]
    descriptions = [desc.text.strip() for desc in challenges.find_all('div', {'class' : 'embed-responsive'})]
    ids = [id.get("value") for id in challenges.find_all('input', {'id' : 'challenge'})]
    challenge_ids = [chall_id.get("value") for chall_id in challenges.find_all('input', {'id' : 'challenge-id'})]

    current_level_descriptions = {"pwd" : pwd}
    for name, description in zip(names, descriptions):
        current_level_descriptions[name] = description
    current_level_ids = {"pwd" : pwd}
    for name, id in zip(names, ids):
        current_level_ids[name] = id
    for name, chall_id in zip(names, challenge_ids):
        current_level_cids[name] = int(chall_id)

    return names, descriptions
 


def print_modules(modules_html):
    global logged_in
    names, progresses, paths = parse_modules(modules_html)
    if not (names and progresses and paths):
        print("No modules found.")
        return
    
    # Create a table for neatly displaying modules
    table = PrettyTable()
    table.field_names = ["Module", "Progress", "Path"] if logged_in else ["Module", "Path"]
    table.align["Module"] = "l"
    if logged_in:
        table.align["Progress"] = "r"
    table.align["Path"] = "l"

    for name, progress, path in zip(names, progresses, paths):
        if logged_in:
            progress = round(float(progress), 2)
            table.add_row([name, f"{progress} %", path])
        else:
            table.add_row([name, path])
    
    print(table)

def parse_modules(modules_html):
    soup = BeautifulSoup(modules_html, 'html.parser')
    sfiles = soup.find("ul", {"class" : "card-list"})
    if not sfiles:
        return None, None, None

    names = [name.text for name in sfiles.find_all('h4', {'class' : 'card-title'})]
    progresses = [progress.get("style").split(':')[1].strip('%') for progress in sfiles.find_all("div", {"class" : "progress-bar"})]
    paths = [path.get("href") for path in sfiles.find_all("a", {"class" : "text-decoration-none"})]

    return names, progresses, paths
 

def list_files():
    global pwd, session
    LS_FUNCTIONS = [print_ls_error, print_dojos, print_modules, print_levels]
    effective_pwd = pwd
    filetype = pwd.count('/') # 1 = "Dojo", 2 = "Module", 3 = "Level" other = "Unknown Type"
    if pwd == "/":
        effective_pwd = "/dojos"
    if effective_pwd == "/dojos":
        filetype = 1
    else:
        filetype += 1
    try:
        ls_func = LS_FUNCTIONS[filetype]
    except IndexError:
        ls_func = no_flag
    resp = session.get(f"{BASE_URL}{effective_pwd}")
    if resp.status_code != 200:
        print(f"An error occurred while trying to list files in {pwd}:", f"Status code not 200 ({resp.status_code}).")
        return
    try:
        ls_func(resp.text)
    except error as e:
        print(f"An error occurred while trying to list files in {pwd}:", "Cannot list files in this directory.")
        print(e)

def print_level_description(level_name):
    global current_level_descriptions, pwd, session
    # Check if the level desc is cached
    if current_level_descriptions["pwd"] == pwd:
        try:
            print(current_level_descriptions[level_name])
        except KeyError:
            print(f"Level name {level_name} not found in {pwd}!")
        return
    resp = session.get(f"{BASE_URL}{pwd}")
    if resp.status_code != 200:
        print(f"Could not fetch {BASE_URL}{pwd}!")
        return
    parse_levels(resp.text)
    print_level_description(level_name)
    
def save_and_quit():
    readline.write_history_file(HISTORY_PATH)
    quit()
     
def resolve_cmd(cmd_str):
    global config
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
            cmd = config["aliases"][cmd_str]
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
    global pwd, username
    if logged_in:
        prompt_str = f"(pwncmd@{username})-[{pwd}]\n>> "
    else:
        prompt_str = f"(pwncmd)-[{pwd}]\n>> "

    return input(prompt_str).strip()

def interactive_shell():
    global config, pwd
    if not read_config():
        write_config(config)
    pwd = config["home"]

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

def main():
    if len(sys.argv) > 1:
        ...
    else:
        interactive_shell()


if __name__ == "__main__":
    main()

