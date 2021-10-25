import os
import sys
import functools


@functools.cache
def is_executable() -> bool:
    return getattr(sys, 'frozen', False)


@functools.cache
def get_appdir() -> str:
    if is_executable():  # running as .exe
        return os.path.dirname(__file__)
    else:  # running a .py
        return os.path.dirname(__file__)


@functools.cache
def get_memdir() -> str:
    return os.path.join(get_appdir(), 'memory')


@functools.cache
def get_dbfile() -> str:
    return os.path.join(get_appdir(), 'memory', 'data.sl3')


def get_config(key: str = None, default=...) -> dict:
    import json

    configpath = os.path.join(get_memdir(), 'config.json')
    configfile = open(configpath)
    try:
        config: dict = json.load(configfile)
    finally:
        configfile.close()
    if key:
        if default is not ...:
            return config.get(key, default)
        else:
            return config[key]
    else:
        return config
