# -*- coding=utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

import sqlite3 as sql
from datetime import datetime

import scripts


class ExecutableDisplay(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(2, weight=1)

        self.widgets = {
            'name': tk.Message(self),
            'exe': tk.Message(self, bg='pink'),
            'cmdline': tk.Message(self),
            'create_time': tk.Message(self),
            'username': tk.Message(self)
        }
        for i, (key, widget) in enumerate(self.widgets.items()):
            label = key.replace('_', ' ').title()
            tk.Label(self, text=label).grid(row=i, column=0, sticky=W)
            widget.configure(cursor='hand2', anchor=NW, aspec=None)
            widget.bind(
                '<Configure>',
                lambda e: e.widget.configure(width=e.widget.winfo_width())
            )
            widget.bind('<Button>', self.copy)
            widget.grid(row=i, column=2, sticky=EW)

        ttk.Separator(self, orient=VERTICAL).grid(row=0, column=1, rowspan=len(self.widgets), sticky=NS)
        self.clear()

    def clear(self):
        for widget in self.widgets.values():
            widget.configure(text='...')

    def display(self, exe_id: int):
        with sql.connect(scripts.get_dbfile()) as conn:
            conn.row_factory = sql.Row
            cursor = conn.cursor()

            query = "SELECT * FROM executables WHERE rowid = ?"

            cursor.execute(query, [exe_id])
            item: sql.Row = cursor.fetchone()

        for key, widget in self.widgets.items():
            if key in item.keys():
                value = item[key]
                if isinstance(value, float):
                    value = datetime.fromtimestamp(value).isoformat(sep=' ', timespec='seconds')
                widget.configure(text=value)
            else:
                widget.configure(text="~ERROR~")

    def copy(self, event):
        self.clipboard_clear()
        self.clipboard_append(event.widget['text'])
        top = tk.Toplevel(self)
        top.overrideredirect(True)
        lbl = tk.Label(top, text='Copied', relief=SUNKEN, borderwidth=2)
        lbl.grid()
        top.update_idletasks()
        top.geometry('{}x{}+{}+{}'.format(lbl.winfo_width(), lbl.winfo_height(), event.x_root, event.y_root))
        top.after(500, top.destroy)
