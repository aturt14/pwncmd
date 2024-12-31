# pwncmd

**pwncmd** is an interactive shell designed for the [pwn.college](https://pwn.college), providing users with a UNIX-like interface to launch challenges and navigate dojos.

![Preview](./img/preview.png)
## Features

- **Interactive Shell:** A UNIX-like interface for easy navigation.
- **Challenge Management:** *Start* and *practice* challenges directly without the cranky GUI.
- **Dojo Exploration:** List and interact with *dojos*, *modules*, and *levels*.
- **Customizable Commands:** Set *home directories*, create *aliases*, and save credentials.
- **Command History:** Automatically saves *command history*, enabling you to easily reuse or modify previous commands.
- **Custom Startup Commands** Define commands to be executed at each shell launch.


## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/pwncmd.git
cd pwncmd
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set permissions:
```bash
chmod +x ./pwncmd.py
```
4. Run the interactive shell:
```bash
./pwncmd.py
```

## Commands Overview
A non-exhaustive list of commands (for more, see `help` in the shell):
### Basic Commands

- `help` or `?`: Display a list of available commands.
- `man <command>`: View the manual for a specific command.
- `exit`, `quit`, `q`, or `:x`: Exit the application.
- `clear`: Clear screen.

### Navigation

- `cd <path_optional>`: Change working directory (relative or absolute paths supported).
- `ls <path_optional>`: List dojos, modules, or levels in a directory.
- `set-home <path>`: Set the default home directory.

### User Management

- `login`: Log in to your pwn.college account.
- `logout`: Log out of your account.
- `profile`: Display user statistics (username, belt, awards).

### Challenges

- `start <level_name>` or `s <level_name>`: Start a specified level.
- `practice <level_name>` or `p <level_name>`: Start a level in practice mode.
- `desc <level_name>` or `x/s <level_name>`: Print the description of a level.
- `flag <flag_or_level_name>`: Submit flag for a specific level.
- `progress <path_optional>`: Show progress for a dojo/module.

### Configuration

- `alias <alias_name>=<command>`: Create a custom alias for a command.
- `remember-me`: Save login credentials (encrypted, but with a hardcoded key).
- `forget`: Forget and remove saved login credentials.

## Custom Startup Commands
With the .pwncmdrc configuration file, you can define commands that are automatically executed every time you launch the shell. For instance, you could set `.pwncmdrc` to look like this:
```
login
ls
```
This will login automatically and then immediately list the *files* (dojos, modules, or levels) in the working directory. That can be useful when you are working on a specific module (and have it as your home path) and with this setting, you need only to type `s <level_name>` and you are good to go.

## Level colors
When logged in, levels will be displayed in the following colors:

1. Solved Level: Green
2. Current Level: Yellow
3. Other Levels: White

## Contributing
Disclaimer:

This application is **not** bug-free. 

Ideally, when you find a bug, you solve it yourself and just create a pull request. If that isn't for some reason possible, there is a slight chance that I will find time to solve the issue for you, so just create an issue and pray to the Matrix.

# Known bugs
1. Listing files in `/dojos` doesn't show actual ASU courses.
