import os
import sys


def get_appdir() -> str:
    if getattr(sys, 'frozen', False):  # running as .exe
        return os.path.dirname(__file__)
    else:  # running a .py
        return os.path.dirname(__file__)
