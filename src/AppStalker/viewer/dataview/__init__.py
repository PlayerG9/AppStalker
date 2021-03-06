# -*- coding: utf-8 -*-
r"""

"""
import logging
import tkinter as tk
from tkinter.constants import *

import time
import datetime
import sqlite3 as sql

import scripts
from .executabledisplay import ExecutableDisplay


class DataView(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="View")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.ts = int(time.time())
        self.colormap = {}

        self.scrollfactor = 0.0
        self.ranges = []

        self.display = ExecutableDisplay(self)
        self.display.grid(row=0, columnspan=2, sticky=NSEW)

        self.canvas = tk.Canvas(
            self,
            height=100,
            background='white'
        )
        self.canvas.grid(row=1, column=0, sticky=NSEW)
        self.canvas.bind('<Button-2>', self.b2_down)
        self.canvas.bind('<B2-Motion>', self.b2_motion)
        self.canvas.bind('<Configure>', lambda e: self.render())
        self.canvas.scan_mark(0, 0)
        self.canvas.scan_dragto(300, 0, gain=1)

        self.xscroll = tk.Scrollbar(self, orient=HORIZONTAL, command=self.xview)
        self.xscroll.grid(row=2, column=0, sticky=EW)
        self.xscroll.bind('<ButtonRelease-1>', lambda e: self.undo_scroll())

        self.canvas.configure(xscrollcommand=self.xscrollcommand)

        self.lbl = tk.Label(self, anchor=W, text="...")
        self.lbl.grid(row=3, columnspan=2, sticky=EW)
        self.canvas.bind('<Motion>', self.evt_motion)
        self.debug_label = tk.Label(self, text='...')
        if not scripts.is_executable():
            self.debug_label.grid(row=4, columnspan=2, sticky=EW)

        self.render(autoupdate=True)

    def get_color(self, exe_id: int):
        import random

        def get_tone() -> int:
            return random.randint(0, 127) + 127

        def get_color() -> str:
            r, g, b = get_tone(), get_tone(), get_tone()
            return '#{:02X}{:02X}{:02X}'.format(r, g, b)

        try:
            return self.colormap[exe_id]
        except KeyError:
            color = self.colormap[exe_id] = get_color()
            return color

        # with sql.connect(scripts.get_dbfile()) as conn:
        #     cursor = conn.cursor()
        #
        #     query = "SELECT rowid FROM executables"
        #
        #     for rowid, in cursor.execute(query).fetchall():
        #         cls.colormap[rowid] = get_color()

    ####################################################################################################################
    # rendering
    ####################################################################################################################

    def render(self, *, autoupdate: bool = False):
        if autoupdate:
            logging.debug('auto-update-rendering')
            self.after(5000, lambda: self.render(autoupdate=True))

        self.clear()

        self.draw_times()

        from_x = self.canvas.canvasx(-50)
        to_x = self.canvas.canvasx(self.canvas.winfo_width() + 50)

        from_ts = self.x2ts(from_x)
        to_ts = self.x2ts(to_x)

        points = []

        with sql.connect(scripts.get_dbfile()) as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM measurements WHERE ts BETWEEN ? AND ?'

            for exe_id, ts in cursor.execute(query, [from_ts, to_ts]).fetchall():
                # print(rowid, self.colormap[rowid])
                x = self.ts2x(ts)
                points.append((exe_id, x))

        ranges = self.ranges
        ranges.clear()

        last_id = None
        start = None

        for exe_id, x in points:  # needs to get improved (end is cut)
            if exe_id is not last_id:
                last_id = exe_id
                if start is not None:
                    ranges.append((start, x, exe_id))
                start = x

        for left_x, right_x, exe_id in ranges:
            self.canvas.create_rectangle(left_x, 30, right_x, 2000, fill=self.get_color(exe_id))

    def draw_times(self):
        w = self.canvas.winfo_width()
        
        y = self.canvas.canvasy(2)

        x = self.canvas.canvasx(w // 2)
        dt = datetime.datetime.fromtimestamp(self.x2ts(x))
        self.canvas.create_text(
            x,
            y,
            text=dt.strftime('%Y-%m-%d'),  # todo customizable in settings
            anchor=N
        )
        x = self.canvas.canvasx(0 + 5)
        dt = datetime.datetime.fromtimestamp(self.x2ts(x))
        self.canvas.create_text(
            x,
            y,
            text=dt.strftime('%H:%M:%S'),  # todo customizable in settings
            anchor=NW
        )
        x = self.canvas.canvasx(w - 5)
        dt = datetime.datetime.fromtimestamp(self.x2ts(x))
        self.canvas.create_text(
            x,
            y,
            text=dt.strftime('%H:%M:%S'),  # todo customizable in settings
            anchor=NE
        )

    def clear(self):
        self.canvas.delete(ALL)

    def x2ts(self, x: int) -> int:
        return x + self.ts

    def ts2x(self, ts: int) -> int:
        return ts - self.ts

    ####################################################################################################################
    # debug/info
    ####################################################################################################################

    def evt_motion(self, event):
        x = self.canvas.canvasx(event.x, 1)
        y = self.canvas.canvasy(event.y, 1)
        ts = self.x2ts(x)
        dt = datetime.datetime.fromtimestamp(ts)
        self.lbl.configure(text=dt.isoformat(sep=' '))
        self.debug_label.configure(text='{}x{}'.format(x, y))

        for from_x, to_x, exe_id in self.ranges:
            if from_x <= x <= to_x:
                self.display.display(exe_id)
                break
        else:
            self.display.clear()

    ####################################################################################################################
    # canvas scrolling
    ####################################################################################################################

    def b2_down(self, event):
        self.canvas.scan_mark(event.x, 0)

    def b2_motion(self, event):
        self.canvas.scan_dragto(event.x, 0, gain=1)

    def xview(self, mode: str, arg: str, _=None):
        if mode != 'moveto':
            return
        arg = float(arg)  # '0.0' <= arg <= '0.9'
        self.adjust_scroll((arg + 0.05) - 0.5)

    def adjust_scroll(self, val):
        if not self.scrollfactor:
            self.after(20, self.update_scroll)
        self.scrollfactor = val

    def undo_scroll(self):
        self.scrollfactor = None

    def update_scroll(self):
        if not self.scrollfactor:
            return
        self.after(25, self.update_scroll)
        w = self.canvas.winfo_width()
        w2 = w // 2
        self.canvas.scan_mark(w2, 0)
        self.canvas.scan_dragto(int(w2 - w2 * self.scrollfactor), 0, gain=1)

        x = self.canvas.canvasx(w2)
        ts = self.x2ts(x)
        dt = datetime.datetime.fromtimestamp(ts)
        self.lbl.configure(text=dt.isoformat(sep=' '))
        self.render()
        # self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill='black', width=2)
        # self.canvas.xview_scroll(int(self.scrollfactor*5), UNITS)  # no smooth scroll

    def xscrollcommand(self, *_):  # a: str ~= '0.0', b: str ~= '1.0'
        if self.scrollfactor:
            return
        self.xscroll.set(0.45, 0.55)
