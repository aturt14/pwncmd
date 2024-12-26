#!/usr/bin/env python

import requests
import sys

def help():
    ...
def alias():
    ...
def login():
    ...
def logout():
    ...
def start_challenge():
    ...

def resolve_cmd(cmd):
    commands = {
        "help" : help,
        "?" : help,
        "alias" : alias,
        "login" : login,
        "logout" : logout,
        "start" : start_challenge,
        "s" : start_challenge,
    } 

def prompt():
    print("(pwncmd) ", end="", flush=True)
    return input().split()

def interactive_shell():
    while True:
        cmd = prompt()
        resolve_cmd(cmd)

def main():
    if len(sys.argv) > 1:
        ...
    else:
        interactive_shell()


if __name__ == "__main__":
    main()

