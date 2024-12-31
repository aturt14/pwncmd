# constants.py
from colorama import Fore
# Terminal colors

COLOR1 = Fore.GREEN
COLOR2 = Fore.BLUE
COLOR3 = Fore.RED


BASE_URL = "https://pwn.college"
LOGIN_URL = f"{BASE_URL}/login?next=/?"
PROFILE_URL = f"{BASE_URL}/hacker/" # This url needs for some reason to end with /
DOJOS_URL = f"{BASE_URL}/dojos"
START_CHALLENGE_URL = f"{BASE_URL}/pwncollege_api/v1/docker"
SUBMIT_FLAG_URL = f"{BASE_URL}/api/v1/challenges/attempt"

LOGIN_ERR_MSG = "An error occurred while trying to login:"
CMD_NOT_FOUND_MSG = "This command does not exist:"
PROFILE_ERR_MSG = "Could not reach your profile. Are you logged in?"
DOJOS_ERR_MSG = "An error occurred while getting dojos:"
PROGRESS_ERR_MSG = "An error occurred while trying to find progress:"


SAVE_CREDS_WARNING = "You have enabled the option to remember credentials. Please note that this may pose a security risk." # Be formal and nice

INSECURE_KEY = bytes.fromhex("cafebabedeadbeef133713370ff1cebadbadbadbadcafebadbadbaddeadbeeff") # You totally don't see this

SAVED_CREDS_PATH = "./.login"
CONFIG_PATH = "./.config"
HISTORY_PATH = "./.pwncmd_history"
PWNCMDRC_PATH = "./.pwncmdrc"
