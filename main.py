#!/usr/bin/env python

import requests
import sys
from bs4 import BeautifulSoup

BASE_URL = "https://pwn.college"
LOGIN_URL = f"{BASE_URL}/login?next=/?"
PROFILE_URL = f"{BASE_URL}/hacker/" # This url needs for some reason to end with /

LOGIN_ERR_MSG = "An error occurred while trying to login:"
CMD_NOT_FOUND_MSG = "This command does not exist:"
PROFILE_ERR_MSG = "Could not reach your profile. Are you logged in?"

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

def help():
    ...
def alias():
    ...
def login():
    global session
    nonce = get_nonce()
    if not nonce:
        print("Login failed..")
        return
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
    print(f"Logged in successfully as {username}!")
    
    
def logout():
    ...
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

