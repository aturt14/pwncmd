# levels.py
from constants import BASE_URL
import globals

from bs4 import BeautifulSoup
from colorama import Fore, Style
import shutil

def get_level_cid_by_name(level_name):
    if globals.current_level_cids["pwd"] != globals.pwd:
        update_level_info()
    try:
        return globals.current_level_cids[level_name]
    except:
        print(f"{level_name} doesn't seem to be a vaild level name in {globals.pwd}.")
        return None

def update_level_info():
    resp = globals.session.get(f"{BASE_URL}{globals.pwd}")
    if resp.status_code != 200:
        print(f"Could not fetch {BASE_URL}{globals.pwd}!")
        return None
    parse_levels(resp.text)

def get_level_id_by_name(level_name):
    if globals.current_level_ids["pwd"] != globals.pwd:
        update_level_info()
    try:
        return globals.current_level_ids[level_name]
    except:
        if level_name in globals.current_level_ids.values():
            return level_name
        print(f"{level_name} doesn't seem to be a vaild level name in {globals.pwd}.")
        return None



def print_level_description(level_name):
    # Check if the level desc is cached
    if globals.current_level_descriptions["pwd"] == globals.pwd:
        try:
            print(globals.current_level_descriptions[level_name])
        except KeyError:
            print(f"Level name {level_name} not found in {globals.pwd}!")
        return
    resp = globals.session.get(f"{BASE_URL}{globals.pwd}")
    if resp.status_code != 200:
        print(f"Could not fetch {BASE_URL}{globals.pwd}!")
        return
    parse_levels(resp.text)
    print_level_description(level_name)

def print_colored_level(name, end = '\n'):
    if name == globals.running_level:
        print(f"{Fore.YELLOW}{name}{Style.RESET_ALL}", end = end)
    elif globals.is_solved.get(name, False):
        print(f"{Fore.GREEN}{name}{Style.RESET_ALL}", end = end)
    else:
        print(f"{Fore.WHITE}{name}{Style.RESET_ALL}", end = end)


def print_levels(levels_html, where):
    names, _ = parse_levels(levels_html, where)  

    if not names:
        print(f"No levels found in {where}.")
        return

    terminal_width = shutil.get_terminal_size().columns

    print(f"Levels in {where}:")
    print("+" + "-" * (terminal_width - 2) + "+")
    

    sorted_names = names

    mid_index = len(sorted_names) // 2 + len(sorted_names) % 2
    column1 = sorted_names[:mid_index]
    column2 = sorted_names[mid_index:]

    for level1, level2 in zip(column1, column2):
        print_colored_level(level1, end = (16 - len(level1)) * ' ')
        print_colored_level(level2)

    print("-" * terminal_width)

def parse_levels(levels_html, where):
    soup = BeautifulSoup(levels_html, 'html.parser')
    challenges = soup.find("div", {"id" : "challenges"})
    if not challenges:
        return None, None

    names = [name for name in challenges.find_all('span', {'class' : 'd-sm-block d-md-block d-lg-block'})]

    globals.is_solved = {name.text.strip() : (name.find("i", {"class" : True}).get("class")[3].find("unsolved") == -1) for name in names if name.text.strip() != "Start" and name != "Practice"}
    names = [name.text.strip() for name in names if name.text.strip() != "Start" and name.text.strip() != "Practice"]
    descriptions = [desc.text.strip() for desc in challenges.find_all('div', {'class' : 'embed-responsive'})]
    ids = [id.get("value") for id in challenges.find_all('input', {'id' : 'challenge'})]
    challenge_ids = [chall_id.get("value") for chall_id in challenges.find_all('input', {'id' : 'challenge-id'})]

    globals.current_level_descriptions = {"pwd" : where}
    for name, description in zip(names, descriptions):
        globals.current_level_descriptions[name] = description
    globals.current_level_ids = {"pwd" : where}
    for name, id in zip(names, ids):
        globals.current_level_ids[name] = id
    for name, chall_id in zip(names, challenge_ids):
        globals.current_level_cids[name] = int(chall_id)

    return names, descriptions
 
