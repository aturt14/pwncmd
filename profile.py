from auth import login
from constants import PROFILE_ERR_MSG, PROFILE_URL
import globals

from bs4 import BeautifulSoup

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


def view_profile():
    if not globals.logged_in:
        login()
    resp = globals.session.get(PROFILE_URL)
    if resp.status_code != 200:
        print(PROFILE_ERR_MSG, resp.text, f"\n{resp.status_code = }")
        return
    name, belt, awards = get_profile_info(resp.text)
    
    print_profile(name, belt, awards)


