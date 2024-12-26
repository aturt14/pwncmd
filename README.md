# pwncmd

**pwncmd** is an interactive shell for the [pwn.college](https://pwn.college) platform. It lets users start challenges and explore dojos and levels through a terminal interface.

## Features

- **Interactive Shell:** A UNIX-like interface for easy navigation.
- **Challenge Management:** Start and practice challenges directly without the cranky GUI.
- **Dojo Exploration:** List and interact with categorized dojos, modules, and levels.
- **Customizable Commands:** Set home directories, create aliases, and manage credentials.
- **Login Persistence:** Optionally save and encrypt your login credentials for quicker access in future sessions.
- **Command History:** Automatically saves command history, enabling you to easily reuse or modify previous commands.


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
### Basic Commands

`help` or `?`: Display a list of available commands.
`man <command>`: View the manual for a specific command.
`exit`, `quit`, `q`, or `:x`: Exit the application.

### Navigation

`cd <path>`: Change working directory (relative or absolute paths supported).
`ls`: List dojos, modules, or levels in the current directory.
`set-home <path>`: Set the default home directory.

### User Management

`login`: Log in to your pwn.college account.
`logout`: Log out of your account.
`profile`: Display user statistics (username, belt, awards).

### Challenges

`start <level_name>` or `s <level_name>`: Start a specified level.
`practice <level_name>` or `p <level_name>`: Start a level in practice mode.
`desc <level_name>` or `x/s <level_name>`: Print the description of a level.

### Configuration

`alias <alias_name>=<command>`: Create a custom alias for a command.
`remember-me`: Save login credentials (encrypted, but with a hardcoded key).
`forget`: Forget and remove saved login credentials.

## Contributing
Disclaimer:

This application is *not* bug-free. 

In best case, when you find a bug, you solve it yourself and just create a pull request. If that isn't for some reason possible, there is a slight chance that I will find time to solve the issue for you, so just create an issue and pray to the Matrix.

# Known bugs
1. Listing files in `/dojos` doesn't show actual ASU courses.
2. Backspace can remove the `>>` when typing a command.
