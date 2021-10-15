import os
import sys
import functools


@functools.cache
def get_appdir() -> str:
    if getattr(sys, 'frozen', False):  # running as .exe
        return os.path.dirname(__file__)
    else:  # running a .py
        return os.path.dirname(__file__)


@functools.cache
def get_memdir() -> str:
    return os.path.join(get_appdir(), 'memory')


@functools.cache
def get_dbfile() -> str:
    return os.path.join(get_appdir(), 'memory', 'data.sl3')
