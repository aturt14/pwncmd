# auth.py
from utils import encrypt, decrypt, get_nonce
from constants import INSECURE_KEY, SAVED_CREDS_PATH, SAVE_CREDS_WARNING, LOGIN_ERR_MSG, LOGIN_URL
import globals


from bs4 import BeautifulSoup
import getpass
import requests


def creds_incorrect(resp_html):
    soup = BeautifulSoup(resp_html, 'html.parser')
    incorrect = soup.find("span", string="Your username or password is incorrect")
    if incorrect:
        return True
    return False

def ask_for_creds():
    username = input("Username or email: ")
    password = getpass.getpass("Password: ")

    return username, password

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


def login():
    nonce = get_nonce()
    if not nonce:
        print("Login failed..")
        return
    if not globals.config["remember_creds"]:
        globals.username, password = ask_for_creds()
    else:
        print(SAVE_CREDS_WARNING)
        globals.username, password = load_creds()
        if not (globals.username and password):
            globals.username, password = ask_for_creds()
    login_data = {
        "name" : globals.username,
        "password" : password,
        "_submit" : "Submit",
        "nonce" : nonce,
    }
    resp = globals.session.post(LOGIN_URL, data=login_data)
    if resp.status_code != 200:
        print(LOGIN_ERR_MSG, f"POST request failed: {resp.text}")
        globals.username = None
        return
    if creds_incorrect(resp.text):
        print(LOGIN_ERR_MSG, "Incorrect credentials!")
        globals.username = None
        return
    if globals.config["remember_creds"]:
        save_creds((globals.username, password))
    print(f"Logged in successfully as {globals.username}!")
    globals.logged_in = True
    
    
def logout():
    globals.logged_in = False
    globals.session = requests.Session()


