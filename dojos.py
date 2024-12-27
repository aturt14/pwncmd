# dojos.py
from constants import DOJOS_URL, DOJOS_ERR_MSG
import globals


from bs4 import BeautifulSoup
from prettytable import PrettyTable

def parse_dojos(dojos_html):
    soup = BeautifulSoup(dojos_html, 'html.parser')
    scategories = soup.find_all("h2")
    categories = [category.text for category in scategories]
    sdojos = soup.find_all("ul", {"class" : "card-list"})
    names_by_category, progresses_by_category, paths_by_category = {}, {}, {}

    for i, category in enumerate(categories):
        names = [name.text for name in sdojos[i].find_all('h4', {'class' : 'card-title'})]
        progresses = [progress.get("style").split(':')[1].strip('%') for progress in sdojos[i].find_all("div", {"class" : "progress-bar"})]
        paths = [path.get("href") for path in sdojos[i].find_all("a", {"class" : "text-decoration-none"})]

        names_by_category[category] = names
        progresses_by_category[category] = progresses
        paths_by_category[category] = paths
    return categories, names_by_category, progresses_by_category, paths_by_category
    
def print_dojos(dojos_html):
    categories, names_by_category, progresses_by_category, paths_by_category = parse_dojos(dojos_html)
    
    for category in categories:
        print(f"====== {category} =====")
        
        table = PrettyTable()
        table.field_names = ["Dojo", "Progress", "Path"] if globals.logged_in else ["Dojo", "Path"]
        table.align["Dojo"] = "l"
        table.align["Path"] = "r"
        if globals.logged_in:
            table.align["Progress"] = "c" 
        
        for name, progress, path in zip(names_by_category[category], progresses_by_category[category], paths_by_category[category]):
            path = path.replace("/dojo", "")
            if globals.logged_in:
                progress = round(float(progress), 2)
                table.add_row([name, f"{progress} %", path])
            else:
                table.add_row([name, path])
        
        print(table)

def show_dojos():
    resp = globals.session.get(DOJOS_URL)
    if resp.status_code != 200:
        print(DOJOS_ERR_MSG, f"Status code not 200 ({resp.status_code}).")
        return
    print_dojos(resp.text)


