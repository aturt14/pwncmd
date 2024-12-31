from constants import BASE_URL
from utils import resolve_path
from constants import PROGRESS_ERR_MSG


import globals

from bs4 import BeautifulSoup

def get_progress(html, filename):
    soup = BeautifulSoup(html, 'html.parser')
    files = soup.find_all("a", {"class" : "text-decoration-none", "href" : True})
    for file in files:
        if filename in file.get("href"):
            progress_bar = file.find("div", {"class" : "progress-bar", "style" : True})
            if not progress_bar:
                continue
            progress_style = progress_bar.get("style").split(':')
            if not progress_style:
                continue
            progress = float(progress_style[1].strip('%'))
            progress = round(progress, 2)
            return progress
    return None


def show_progress(path = None):
    if not globals.logged_in:
        print("You are not logged in.")
        return
    if not path:
        path = globals.pwd
    else:
        path = resolve_path(path)
    progress_file_path = resolve_path(f"{path}/..")
    if path == "/" or path == "/dojos":
        print("man progress")
        return
    try:
        resp = globals.session.get(f"{BASE_URL}{progress_file_path}")
        if resp.status_code != 200:
            print(PROGRESS_ERR_MSG, f"Could not find current progress for {path}. Status code: {resp.status_code}")
            return
    except Exception as e:
        print(PROGRESS_ERR_MSG, e)
        return
    progress = get_progress(resp.text, path.split('/')[-1])
    if progress:
        print(f"Your progress in {path} is {progress} %.")
    else:
        print(PROGRESS_ERR_MSG, f"Could not find any progress in {progress_file_path}. ")
        ans = input("Wanna try it yourself? y/N\n")
        if ans.lower() == 'y':
            print(resp.text)
    
