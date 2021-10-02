# -*- coding=utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *
from tkinter import messagebox

import os

import psutil

import scripts


class Settings(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Settings")
        self.grid_columnconfigure(0, weight=1)

        self.bind('<Map>', lambda e: self.on_place())

        self.stalkerprocess = StalkerProcess(self)
        self.stalkerprocess.grid(sticky=EW)
        self.configprocess = ConfigProcess(self)
        self.configprocess.grid(sticky=EW)

    def on_place(self):
        pass


class StalkerProcess(tk.LabelFrame):
    pid_path = os.path.join(scripts.get_memdir(), 'pid.share')
    stalker_exe = os.path.join(scripts.get_appdir(), 'Stalker.exe')

    def __init__(self, master):
        super().__init__(master, text="Stalker")

        self.stalker_process: psutil.Process = None

        row = 0

        tk.Label(self, text="Stalker process running: ").grid(row=row, column=0, sticky=W)
        self.lbl_is_running = tk.Frame(self, background='red', cursor='hand2')
        self.lbl_is_running.grid(row=row, column=1, sticky=NSEW)
        self.lbl_is_running.configure(width=20, height=20)
        self.lbl_is_running.bind('<ButtonRelease-1>', lambda e: self.change_stalker_state())
        # self.btn_change_stalker_state = tk.Button(self, command=self.change_stalker_state)
        # self.btn_change_stalker_state.grid(row=row, column=1, sticky=W)

        self.after(200, self.update_info)

    def load_stalker(self):
        if os.path.isfile(self.pid_path):
            with open(self.pid_path, 'r') as file:
                try:
                    pid = int(file.read())
                    self.stalker_process = psutil.Process(pid)
                    return
                except (ValueError, psutil.NoSuchProcess):  # failed to load pid or outdated pid
                    pass
        self.stalker_process = None

    def update_info(self):
        self.after(200, self.update_info)
        if self.stalker_process is None:
            self.load_stalker()
        alive = False
        if self.stalker_process:
            alive = self.stalker_process.is_running()

        if alive:
            bg = 'green'
            # self.lbl_is_running.configure(text='💀')
        else:
            bg = 'red'
            # self.lbl_is_running.configure(text='＋')
            self.stalker_process = None

        self.lbl_is_running.configure(background=bg)

    def change_stalker_state(self):
        if self.stalker_process:
            if messagebox.askokcancel(
                    "stop stalker",
                    "Are you sure you want to stop the stalker-process"
            ) is True:
                self.stalker_process.kill()
        else:
            if messagebox.askokcancel(
                "start stalker",
                "Are you sure you want to start the stalker process"
            ) is True:
                os.startfile(self.stalker_exe)


class ConfigProcess(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Configure")
        tk.Label(self, text="...").grid()
