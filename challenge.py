# challenge.py
from levels import get_level_id_by_name
from utils import get_csrf_token
from auth import login
from constants import START_CHALLENGE_URL
import globals

def start_challenge(level_name = None, practice = False):
    if not level_name:
        print("Not starting anything.")
        return
    
    # Levels have different id's than names..
    level_id = get_level_id_by_name(level_name) 

    if not level_id:
        return

    if not globals.logged_in:
        login()

    # We need to get anti csrf token first
    csrf_token = get_csrf_token()
    rheaders = {"CSRF-Token" : csrf_token}
    pwd_data = globals.pwd.split('/')
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

    resp = globals.session.post(START_CHALLENGE_URL, json=challenge_data, headers=rheaders)
    print(f"Starting {level_name} in {pwd_data[2]} in {pwd_data[1]}...")

    if resp.status_code != 200:
        print(f"There was a problem starting the challenge. Check your network connection and if the details are correct.")
        print(resp.text)
        print(resp.status_code)
        return
    globals.running_level = level_name
    print(f"{level_name} started successfully!")

def practice_challenge(level_name):
    start_challenge(level_name, True)


