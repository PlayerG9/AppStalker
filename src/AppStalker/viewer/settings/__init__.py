# -*- coding=utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *
from tkinter import messagebox

import os
import json
from datetime import datetime

import psutil

import scripts
from . import autostart


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
        self.lbl_is_running.grid(row=row, column=1, sticky=NW)
        self.lbl_is_running.configure(width=20, height=20)
        self.lbl_is_running.bind('<ButtonRelease-1>', lambda e: self.change_stalker_state())
        # self.btn_change_stalker_state = tk.Button(self, command=self.change_stalker_state)
        # self.btn_change_stalker_state.grid(row=row, column=1, sticky=W)

        row += 1
        tk.Label(self, text="Running since").grid(row=row, column=0, sticky=W)
        self.lbl_running_since = tk.Label(self)
        self.lbl_running_since.grid(row=row, column=1, sticky=W)

        self.after(200, self.update_info)

    def load_stalker(self):
        if os.path.isfile(self.pid_path):
            with open(self.pid_path, 'r') as file:
                try:
                    pid = int(file.read())
                    self.stalker_process = psutil.Process(pid)
                    self.lbl_running_since.configure(
                        text=datetime.fromtimestamp(
                            self.stalker_process.create_time()
                        ).isoformat(sep=" ", timespec='seconds')
                    )
                    return
                except (ValueError, psutil.NoSuchProcess):  # failed to load pid or outdated pid
                    pass
        self.lbl_running_since.configure(text="⎯⎯⎯⎯⎯")
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
    time_modes = [
        'seconds',
        'minutes'
    ]
    time_intervalls = [1, 2, 5, 10, 15, 20, 30]

    def __init__(self, master):
        super().__init__(master, text="Configure")

        self.configuration = self.load_config()

        row = 0

        tk.Label(self, text="Measurement every ").grid(row=row)
        time_interval = self.configuration.get('time-interval')
        self.interval = tk.IntVar(
            self,
            value=time_interval if time_interval in self.time_intervalls else self.time_intervalls[3]
        )
        menu = tk.OptionMenu(self, self.interval, *self.time_intervalls)
        menu.configure(relief=FLAT)
        menu.grid(row=row, column=1, sticky=EW)

        time_mode = self.configuration.get('time-mode')
        self.units = tk.StringVar(
            self,
            value=time_mode if time_mode in self.time_modes else self.time_modes[0]
        )
        menu = tk.OptionMenu(self, self.units, *self.time_modes)
        menu.configure(relief=FLAT)
        menu.grid(row=row, column=2, sticky=EW)

    @staticmethod
    def load_config() -> dict:
        with open(os.path.join(scripts.get_memdir(), 'config.json')) as file:
            return json.load(file)
