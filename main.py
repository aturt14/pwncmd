#!/usr/bin/env python

import requests
import sys
import os
import base64
import ast

from bs4 import BeautifulSoup

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

BASE_URL = "https://pwn.college"
LOGIN_URL = f"{BASE_URL}/login?next=/?"
PROFILE_URL = f"{BASE_URL}/hacker/" # This url needs for some reason to end with /
DOJOS_URL = f"{BASE_URL}/dojos"

LOGIN_ERR_MSG = "An error occurred while trying to login:"
CMD_NOT_FOUND_MSG = "This command does not exist:"
PROFILE_ERR_MSG = "Could not reach your profile. Are you logged in?"
DOJOS_ERR_MSG = "An error occurred while getting dojos:"

SAVE_CREDS_WARNING = "You set remember creds to true. Be aware that this might not be secure."

INSECURE_KEY = bytes.fromhex("cafebabedeadbeef133713370ff1cebadbadbadbadcafebadbadbaddeadbeeff")
SAVED_CREDS_PATH = "./.login"
CONFIG_PATH = "./.config"


config = {"remember_creds" : False}
logged_in = False

# Shows in which dojo you currently are, e.g. you could go to Program Security, then pwd would be /Program Security
pwd = "/"

# Global session
session = requests.Session()

############# PROFILE ################

def print_profile(name):
    print(f"Username: {name}")

def get_profile_info(profile_html):
    soup = BeautifulSoup(profile_html, 'html.parser')
    name_element = soup.find('h1')
    if not name_element:
        print(PROFILE_ERR_MSG, f"Error occurred while trying to fetch username. Response: {profile_html}")
        return
    name = name_element.text
    return name

############# LOGIN ###############

def ask_for_creds():
    username = input("Username or email: ")
    password = input("Password: ")

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

def help():
    ...
def alias():
    ...
def login():
    global session, logged_in
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
        return
    if creds_incorrect(resp.text):
        print(LOGIN_ERR_MSG, "Incorrect credentials!")
        return
    if config["remember_creds"]:
        save_creds((username, password))
    print(f"Logged in successfully as {username}!")
    logged_in = True
    
    
def logout():
    global logged_in
    logged_in = False
def start_challenge():
    ...

def view_profile():
    global session
    resp = session.get(PROFILE_URL)
    if resp.status_code != 200:
        print(PROFILE_ERR_MSG, resp.text, f"\n{resp.status_code = }")
        return
    name = get_profile_info(resp.text)
    
    print_profile(name)

def parse_dojos(dojos_html):
    soup = BeautifulSoup(dojos_html, 'html.parser')
    scategories = soup.find_all("h2")
    categories = [category.text for category in scategories]
    sdojos = soup.find_all("ul", {"class" : "card-list"})
    names_by_category, progresses_by_category = {}, {}

    for i, category in enumerate(categories):
        names = [name.text for name in sdojos[i].find_all('h4', {'class' : 'card-title'})]
        progresses = [progress.get("style").split(':')[1].strip('%') for progress in sdojos[i].find_all("div", {"class" : "progress-bar"})]

        names_by_category[category] = names
        progresses_by_category[category] = progresses
    return categories, names_by_category, progresses_by_category
    
def print_dojos(dojos_html):
    from prettytable import PrettyTable  # Import for table formatting (install with pip if not available)
    
    categories, names_by_category, progresses_by_category = parse_dojos(dojos_html)
    
    for category in categories:
        print(f"====== {category} =====")
        
        table = PrettyTable()
        table.field_names = ["Dojo Name", "Progress"] if logged_in else ["Dojo Name"]
        table.align["Dojo Name"] = "l"
        if logged_in:
            table.align["Progress"] = "r" 
        
        for name, progress in zip(names_by_category[category], progresses_by_category[category]):
            if logged_in:
                progress = round(float(progress), 2)
                table.add_row([name, f"{progress}%"])
            else:
                table.add_row([name])
        
        print(table)
    
def show_dojos():
    global session
    resp = session.get(DOJOS_URL)
    if resp.status_code != 200:
        print(DOJOS_ERR_MSG, f"Status code not 200 ({resp.status_code}).")
        return
    print_dojos(resp.text)

def resolve_cmd(cmd):
    commands = {
        "help" : help,
        "?" : help,
        "alias" : alias,
        "login" : login,
        "logout" : logout,
        "start" : start_challenge,
        "s" : start_challenge,
        "profile" : view_profile,
        "dojos" : show_dojos,
        "remember-me" : remember_creds,
        "forget" : forget_and_remove,
        "q" : quit,
        ":x" : quit,
        "exit" : quit,
        "quit" : quit,
    } 
    try:
        cmd_func = commands[cmd]
    except KeyError:
        print(CMD_NOT_FOUND_MSG, cmd)
        return
    cmd_func()
    
def prompt():
    print("(pwncmd) ", end="", flush=True)
    return input().strip()

def interactive_shell():
    global config
    if not read_config():
        write_config(config)
    while True:
        cmd = prompt()
        resolve_cmd(cmd)

def main():
    if len(sys.argv) > 1:
        ...
    else:
        interactive_shell()


if __name__ == "__main__":
    main()

