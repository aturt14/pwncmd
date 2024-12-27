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


SAVE_CREDS_WARNING = "You set remember creds to true. Be aware that this might not be secure."

INSECURE_KEY = bytes.fromhex("cafebabedeadbeef133713370ff1cebadbadbadbadcafebadbadbaddeadbeeff")

SAVED_CREDS_PATH = "./.login"
CONFIG_PATH = "./.config"
HISTORY_PATH = "./.pwncmd_history"
PWNCMDRC_PATH = "./.pwncmdrc"
