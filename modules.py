import globals

from bs4 import BeautifulSoup
from prettytable import PrettyTable

def print_modules(modules_html):
    names, progresses, paths = parse_modules(modules_html)
    if not (names and progresses and paths):
        print("No modules found.")
        return
    
    # Create a table for neatly displaying modules
    table = PrettyTable()
    table.field_names = ["Module", "Progress", "Path"] if globals.logged_in else ["Module", "Path"]
    table.align["Module"] = "l"
    if globals.logged_in:
        table.align["Progress"] = "r"
    table.align["Path"] = "l"

    for name, progress, path in zip(names, progresses, paths):
        if globals.logged_in:
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
 
