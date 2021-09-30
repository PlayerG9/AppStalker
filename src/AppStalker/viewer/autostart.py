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


def isAdmin():
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


def is_added():
    pass


def add():
    pass


def remove():
    pass
