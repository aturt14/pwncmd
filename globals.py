# globals.py
import requests

# Shows in which dojo you currently are, e.g. you could go to Program Security, then pwd would be /Program Security
pwd = "/"

config = {"remember_creds" : False, "home" : "/", "aliases" : {}, "ssh_privkey_path" : None}
logged_in = False

current_level_descriptions = {"pwd" : "aaah"}
current_level_ids = {"pwd" : "aaah"}
current_level_cids = {"pwd" : "aaah"}
is_solved = {"pwd" : "aaah"}
running_level = None

username = None


# Global session
session = requests.Session()


