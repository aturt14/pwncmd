# utils.py
from constants import HISTORY_PATH, LOGIN_URL, LOGIN_ERR_MSG, BASE_URL
import globals

import readline
import re
import os
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from bs4 import BeautifulSoup

def clean_path(input_path):
    normalized_path = os.path.normpath(input_path)
    valid_path = normalized_path
    
    return valid_path.replace("//", '/')

def resolve_path(path):
    if path.startswith('/'):
        # Absolute path
        return clean_path(path)
    else:
        return clean_path(f"{globals.pwd}/{path}")



def save_and_quit():
    readline.write_history_file(HISTORY_PATH)
    quit()

def clear_screen():
    os.system("clear") # You better not use windows

def get_nonce():
    resp = globals.session.get(LOGIN_URL)
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


def get_csrf_token():
    resp = globals.session.get(f"{BASE_URL}{globals.pwd}")
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
        print(f"CSRF token not found at {BASE_URL}{globals.pwd}..")


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


