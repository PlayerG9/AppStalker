# -*- coding=utf-8 -*-
r"""
import winreg as reg
import os

def AddToRegistry():

    # in python __file__ is the instant of
    # file path where it was executed
    # so if it was executed from desktop,
    # then __file__ will be
    # c:\users\current_user\desktop
    pth = os.path.dirname(os.path.realpath(__file__))

    # name of the python file with extension
    s_name="mYscript.py"

    # joins the file name to end of path address
    address=os.join(pth,s_name)

    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = HKEY_CURRENT_USER
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"

    # open the key to make changes to
    open = reg.OpenKey(key,key_value,0,reg.KEY_ALL_ACCESS)

    # modify the opened key
    reg.SetValueEx(open,"any_name",0,reg.REG_SZ,address)

    # now close the opened key
    reg.CloseKey(open)
"""
import winreg
import ctypes


def is_admin():
    import os
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        raise SystemError("couln't check if user has admin provileges")


KEY_ALL = winreg.HKEY_USERS  # or winreg.HKEY_CLASSES_ROOT?
KEY_USER = winreg.HKEY_CURRENT_USER
KEY_PATH = 'Software\Microsoft\Windows\CurrentVersion\Run'
VALUE_NAME = 'AppStalker'


def is_added(hkey=None, valcheck: str = None):
    hkey = _get_hkey(hkey)

    try:
        key = winreg.OpenKey(hkey, KEY_PATH, 0, winreg.KEY_READ)

        if valcheck:
            if valcheck != winreg.QueryValueEx(key, VALUE_NAME)[0]:
                raise ValueError('invalid entry')

        winreg.CloseKey(key)

        return True
    except OSError:
        return False


def add(path: str, hkey=None):
    hkey = _get_hkey(hkey)

    key = winreg.OpenKey(hkey, KEY_PATH, 0, winreg.KEY_WRITE)

    winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, path)  # maybe winreg.REG_BINARY

    winreg.CloseKey(key)


def remove(hkey=None):
    hkey = _get_hkey(hkey)

    winreg.DeleteKey(hkey, KEY_PATH)


def _get_hkey(hkey):
    if hkey is None:
        if is_admin():
            return KEY_ALL
        else:
            return KEY_USER
    else:
        return hkey
