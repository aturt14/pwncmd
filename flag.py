# flag.py
from auth import login
from levels import get_level_cid_by_name
from utils import get_csrf_token
from constants import SUBMIT_FLAG_URL
import globals


def submit_flag(level_name_or_flag = None):
    level_name = globals.running_level
    flag = None
    # Check if it is a flag
    if level_name_or_flag:
        if "{" in level_name_or_flag: # Flags don't really need to be in the correct format, they just need to have the content in {}
            flag = level_name_or_flag
        else:
            level_name = level_name_or_flag
    if not globals.logged_in:
        login()
    if not level_name:
        print(f"argv[1] should be the level name.")
        return
    challenge_cid = get_level_cid_by_name(level_name)
    if not flag:
        flag = input("Flag: ")
    csrf_token = get_csrf_token()
    flag_headers = {"CSRF-Token" : csrf_token}
    flag_data = {
        "challenge_id" : challenge_cid,
        "submission" : flag,
    }
    resp = globals.session.post(SUBMIT_FLAG_URL, json=flag_data, headers=flag_headers)
    if resp.status_code != 200:
        print(f"Error when fetching {SUBMIT_FLAG_URL}. Status code: {resp.status_code}, response: {resp.text}.")
        return
    resp_json = resp.json()
    try:
        print(resp_json["data"]["message"])
    except:
        print(f"Response in weird format: {resp.text}")
 
