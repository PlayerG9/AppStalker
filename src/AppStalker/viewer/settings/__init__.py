# -*- coding=utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *
from tkinter import messagebox

import os
import json
from datetime import datetime
import sqlite3 as sql

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
        self.dbconfig = DatabaseConfig(self)
        self.dbconfig.grid(sticky=EW)

    def on_place(self):
        pass


class StalkerProcess(tk.LabelFrame):
    pid_path = os.path.join(scripts.get_memdir(), 'pid.share')
    stalker_exe = os.path.join(scripts.get_appdir(), 'Stalker.exe')

    def __init__(self, master):
        super().__init__(master, text="Stalker")

        self.stalker_process: [psutil.Process, None] = None

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

    def restart(self, force):
        if self.stalker_process:
            self.stalker_process.kill()
        if self.stalker_process or force:
            os.startfile(self.stalker_exe)


class ConfigProcess(tk.LabelFrame):
    time_modes = [
        'seconds',
        'minutes'
    ]
    time_intervalls = [1, 2, 5, 10, 15, 20, 30]
    autostart_options = ['Disabled', 'User', 'All']

    def __init__(self, master):
        super().__init__(master, text="Configure")
        self.grid_columnconfigure(5, weight=1)

        self.configuration = self.load_config()

        self.stalker_exe = self.master.stalkerprocess.stalker_exe

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

        row += 1
        autostart_current = self.autostart_options[autostart.get_autostart_level(self.stalker_exe)]
        self.auto_start = tk.StringVar(
            self,
            autostart_current
        )
        self.autostart_current = self.auto_start.get()
        tk.Label(self, text="Autostart").grid(row=row, column=0, sticky=W)
        menu = tk.OptionMenu(self, self.auto_start, *self.autostart_options)
        menu.grid(row=row, column=1, sticky=EW)
        if autostart_current == 'All' and autostart.is_admin():
            menu.configure(state=DISABLED)
        elif not autostart.is_admin():
            menu['menu'].entryconfigure(2, state=DISABLED)

        row += 1
        tk.Button(self, text="Apply", width=7, command=self.apply).grid(row=row, column=0, columnspan=6, sticky=E)

    @staticmethod
    def load_config() -> dict:
        with open(os.path.join(scripts.get_memdir(), 'config.json')) as file:
            return json.load(file)

    def apply(self):
        self.configuration['time-interval'] = self.interval.get()
        self.configuration['time-mode'] = self.units.get()
        auto_start = self.auto_start.get()
        if self.autostart_current != auto_start:
            autostart.remove_all()
            if auto_start == 'User':
                autostart.add(self.stalker_exe, autostart.KEY_USER)
            elif autostart == 'All':
                autostart.add(self.stalker_exe, autostart.KEY_ALL)
            self.autostart_current = auto_start
        self.master.stalkerprocess.restart(force=False)


class DatabaseConfig(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Database")
        self.button = tk.Button(self, text="Optimize", command=self.vacuum)
        self.button.grid(row=0, columnspan=2, sticky=EW)
        tk.Label(self, text="Filesize: ").grid(row=1, column=0, sticky=EW)
        self.label = tk.Label(self, text="...")
        self.label.grid(row=1, column=1, sticky=EW)
        self.update_label()

    def vacuum(self):
        _text = self.button['text']
        self.button.configure(cursor='wait', text="Database get's optimized")
        try:
            with sql.connect(scripts.get_dbfile()) as conn:
                conn.execute('VACUUM')
        finally:
            self.button.configure(cursor='', text=_text)
            self.update_label()

    def update_label(self):
        try:
            size = os.path.getsize(scripts.get_dbfile())
            self.label.configure(text=self.format_size(size))
        except OSError:
            self.label.configure(text="couln't get database size")

    @staticmethod
    def format_size(size: int) -> str:
        FSIZES = (
            ('GB', 1024 ** 3),
            ('MB', 1024 ** 2),
            ('KB', 1024 ** 1),
            # ('B',  1024**0),
        )

        if size is None:
            return '-B'
        for st, sn in FSIZES:
            if size > sn:
                return '{:.2f}{}'.format(size / sn, st)
        return '{:d}B'.format(size)
