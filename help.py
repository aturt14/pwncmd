# help.py
from utils import clear_screen
import time

def help():
    print("Commands:")
    cmds = """        "help" or "?" - Shows this text.
        "man <cmd_name>" - Manual for <cmd_name>.
        "alias" - Create an alias for a command.
        "login" Log into you pwn.college account.
        "logout" - Log out of your pwn.college account.
        "start <level_name>" or "s <level_name>" - Start <level_name>..
        "practice <level_name>" or "p <level_name>" - Practice <level_name>.
        "profile" - Check out your fantastic stats.
        "dojos" - Show dojos.
        "ls" - List dojos/modules/levels in working directory.
        "set-home" - Set default home path.
        "remember-me" - Remember login credentials.
        "forget" - Forget and remove login credentials.
        "cd" - Change working directory.
        "desc <level_name>" or "x/s <level_name>" - Print description of <level_name>.
        "clear" : Clear screen.
        "q" or ":x" or "exit" or "quit" - Exit.
    """
    print(cmds)
    print("If something doesn't work as expected, RTFM.")
    print("If you are sure it is an error in the code, submit an issue to GitHub.")

def man(cmd_name):
    MAN_HELP = """Displays the list of available commands."""

    MAN_MAN = """
    Shows the manual for a specific command.
    Example:

    (pwncmd)-[/]
    >> man man

        Shows the manual for a specific command.
        Example:

        (pwncmd)-[/]
        >> man man

            Shows the manual for a specific command.
            Example:

            (pwncmd)-[/]
            >> man man

                Shows the manual for a specific command.
                Example:
                    RecursionError
    """
    MAN_ALIAS = """
    Creates an alias for a command. 
    Example:

    (pwncmd)-[/]
    >> alias li=login
    Typing li triggers login.
    """
    MAN_LOGIN = """
    Logs into your pwn.college account. If you don't have remember-me on, login will prompt you for username/email and password.
    Example with remember-me:

    (pwncmd)-[/]
    >> login
    You set remember creds to true. Be aware that this might not be secure.
    Logged in successfully as hacker!
    
    Example without remember-me:

    (pwncmd)-[/]
    >> login
    Username or email: 1337hacker
    Password:
    Logged in successfully as 1337hacker!
    """
    MAN_LOGOUT = """
    Logs out of your pwn.college account.
    """
    MAN_START = """
    Starts the specified level. If you are not logged in, it will run login first.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> s level1
    Starting level1 in file-struct-exploits in software-exploitation...
    level1 started successfully!
    """
    MAN_PRACTICE = """
    Runs the specified level in practice mode.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> p level1
    Starting level1 in file-struct-exploits in software-exploitation...
    level1 started successfully!
    """
    MAN_PROFILE = """
    Displays your statistics. If you are not logged in, it will login automatically.
    Example:

    (pwncmd)-[/]
    >> profile
    Username: 1337hacker
    Belt: black
    Awarded for completing the Pwntools Tutorials dojo.
    """
    MAN_DOJOS = """
    Shows the available dojos.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> dojos
    ====== Getting Started =====
    +-----------------------+----------+-------------------+
    | Dojo                  | Progress |              Path |
    +-----------------------+----------+-------------------+
    | Getting Started       | 100.0 %  |          /welcome |
    | Linux Luminarium      |  1.19 %  | /linux-luminarium |
    | Computing 101         | 71.21 %  |    /computing-101 |
    | Playing With Programs | 52.11 %  |     /fundamentals |
    +-----------------------+----------+-------------------+
    ====== Core Material =====
    +------------------------+----------+-------------------------+
    | Dojo                   | Progress |                    Path |
    +------------------------+----------+-------------------------+
    | Intro to Cybersecurity | 74.44 %  | /intro-to-cybersecurity |
    | Program Security       | 100.0 %  |       /program-security |
    | System Security        | 84.21 %  |        /system-security |
    | Software Exploitation  | 38.73 %  |  /software-exploitation |
    +------------------------+----------+-------------------------+
    ====== Community Material =====
    ...
    """
    MAN_LS = """
    Lists dojos, modules, or levels in the current directory. This is an essential command for pwncmd. When you change directory (man cd) and want to see what dojos, modules or levels are there, you use ls. Note that ls can NOT be used with an argument. You always need to cd first.
    Example:

    (pwncmd)-[/software-exploitation]
    >> ls
    Printing modules..
    +--------------------------------+----------+--------------------------------------------------------+
    | Module                         | Progress | Path                                                   |
    +--------------------------------+----------+--------------------------------------------------------+
    | Return Oriented Programming    |  100.0 % | /software-exploitation/return-oriented-programming/    |
    | Format String Exploits         |  100.0 % | /software-exploitation/format-string-exploits/         |
    | File Struct Exploits           |   65.0 % | /software-exploitation/file-struct-exploits/           |
    | Dynamic Allocator Misuse       |    0.0 % | /software-exploitation/dynamic-allocator-misuse/       |
    | Exploitation Primitives        |    0.0 % | /software-exploitation/memory-mastery/                 |
    | Dynamic Allocator Exploitation |    0.0 % | /software-exploitation/dynamic-allocator-exploitation/ |
    | Microarchitecture Exploitation |    0.0 % | /software-exploitation/speculative-execution/          |
    | Kernel Exploitation            |    0.0 % | /software-exploitation/kernel-exploitation/            |
    +--------------------------------+----------+--------------------------------------------------------+
    """
    MAN_SETHOME = """
    Sets the default home path to argv[1]. This is useful when you are currently working on a specific module - you can set your home there and then every time you start pwncmd, you will be right there.
    Example:

    (pwncmd)-[/]
    >> set-home /software-exploitation/file-struct-exploits
    HOME = /software-exploitation/file-struct-exploits
    """
    MAN_REMEMBERME = """
    Remembers your login credentials. The credentials are saved in ./.login and are encrypted using AES-256. This unfortunately doesn't guarantee them any security, as the key is hardcoded. Be aware of that if you are going to use it.
    Example:

    (pwncmd)-[/]
    >> remember-me
    You set remember creds to true. Be aware that this might not be secure.
    """
    MAN_FORGET = """
    Forgets and removes your login credentials if you saved them using remember-me.
    Example:

    (pwncmd)-[/]
    >> forget
    You've been successfully forgotten.
    """
    MAN_CD = """
    Changes the working directory to argv[1]. If no arguments given, changes working directory to home (see man set-home). You can use either absolute or relative paths. 
    pwncmd works on a similar principle as UNIX's filesystem. Each route on pwn.college which contains either dojos, modules or levels can be interpreted as a directory which contains those files. When you cd to e.g. software-exploitation, you can then use ls to list all the modules there. In order to start a challenge, you need to have pwd = dojo/module_of_the_chall.
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> cd ..
    (pwncmd)-[/software-exploitation]
    >> cd dynamic-allocator-misuse
    (pwncmd)-[/software-exploitation/dynamic-allocator-misuse]
    >>
    You can see the current working directory at \\(pwncmd\\)-\\[(.*)\\]
    """
    MAN_DESCRIPTION = """
    Prints the description of the specified level. When your working directory contains levels, you can print the description of a specified one using desc <level_name> or x/s <level_name>.
    Example:

    (pwncmd)-[/software-exploitation/dynamic-allocator-misuse]
    >> x/s level1.0
    Exploit a use-after-free vulnerability to get the flag.
    """
    MAN_FLAG = """
    Asks for the flag for currently running challenge. If no challenge is running, an argument is reqired (level name).
    Example:

    (pwncmd)-[/software-exploitation/file-struct-exploits]
    >> flag level1
    You set remember creds to true. Be aware that this might not be secure.
    Logged in successfully as 1337hack3r!
    Flag: pwn.college{test}
    You already solved this
    """
    MAN_CLEAR = """
    Clears screen. Removes the waste you put in. Hides flags you entered.
    """
    MAN_EXIT = """
    Exits the application.
    """


    man_entries = {
        "help" : MAN_HELP,
        "?" : MAN_HELP,
        "man" : MAN_MAN,
        "alias" : MAN_ALIAS,
        "login" : MAN_LOGIN,
        "logout" : MAN_LOGOUT,
        "start" : MAN_START,
        "s" : MAN_START,
        "practice" : MAN_PRACTICE,
        "p" : MAN_PRACTICE,
        "profile" : MAN_PROFILE,
        "dojos" : MAN_DOJOS,
        "ls" : MAN_LS,
        "set-home" : MAN_SETHOME,
        "remember-me" : MAN_REMEMBERME,
        "forget" : MAN_FORGET,
        "cd" : MAN_CD,
        "desc" : MAN_DESCRIPTION,
        "x/s" : MAN_DESCRIPTION,
        "flag" : MAN_FLAG,
        "clear" : MAN_CLEAR,
        "q" : MAN_EXIT,
        ":x" : MAN_EXIT,
        "exit" : MAN_EXIT,
        "quit" : MAN_EXIT,
    }
    try: 
        print(man_entries[cmd_name])
        if cmd_name == "clear":
            time.sleep(3)
            print("Example:")
            time.sleep(1)
            clear_screen()
    except KeyError:
        help()
 
