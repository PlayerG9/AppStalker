# -*- coding: utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *

import time
import datetime
import sqlite3 as sql

import scripts


class DataView(tk.LabelFrame):
    colormap = {}

    def __init__(self, master):
        if not self.colormap:
            self.init_colormap()

        super().__init__(master, text="View")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.ts = int(time.time())

        self.scrollfactor = 0.0

        self.canvas = tk.Canvas(
            self,
        )
        self.canvas.grid(row=0, column=0, sticky=NSEW)
        self.canvas.bind('<Button-2>', self.b2_down)
        self.canvas.bind('<B2-Motion>', self.b2_motion)

        self.xscroll = tk.Scrollbar(self, orient=HORIZONTAL, command=self.xview)
        self.xscroll.grid(row=1, column=0, sticky=EW)
        self.xscroll.bind('<ButtonRelease-1>', lambda e: self.undo_scroll())

        self.canvas.configure(xscrollcommand=self.xscrollcommand)

        self.lbl = tk.Label(self, anchor=W, text="...")
        self.lbl.grid(row=2, columnspan=2, sticky=EW)
        self.canvas.bind('<Motion>', self.evt_motion)
        self.debug_label = tk.Label(self, text='...')
        self.debug_label.grid(row=3, columnspan=2, sticky=EW)

        self.render()
        # self.canvas.create_text(0, 0, text="Hello World")
        # self.canvas.create_rectangle(0, 0, 100, 100, fill='pink')
        # self.canvas.create_rectangle(200, 200, 400, 300, fill='pink')

    @classmethod
    def init_colormap(cls):
        import random

        def get_tone() -> int:
            return random.randint(0, 127) + 127

        def get_color() -> str:
            r, g, b = get_tone(), get_tone(), get_tone()
            return '#{:02X}{:02X}{:02X}'.format(r, g, b)

        with sql.connect(scripts.get_dbfile()) as conn:
            cursor = conn.cursor()

            query = "SELECT rowid FROM executables"

            for rowid, in cursor.execute(query).fetchall():
                cls.colormap[rowid] = get_color()

    ####################################################################################################################
    # rendering
    ####################################################################################################################

    def render(self):
        self.clear()

        from_x = self.canvas.canvasx(-50)
        to_x = self.canvas.canvasx(self.canvas.winfo_width()+50)

        from_ts = self.x2ts(from_x)
        to_ts = self.x2ts(to_x)

        dt = datetime.datetime.fromtimestamp(from_ts)
        self.lbl.configure(text=dt.isoformat(sep=' '))

        points = []

        with sql.connect(scripts.get_dbfile()) as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM measurements WHERE ts BETWEEN ? AND ?'

            for exe_id, ts in cursor.execute(query, [from_ts, to_ts]).fetchall():
                # print(rowid, self.colormap[rowid])
                x = self.ts2x(ts)
                points.append((exe_id, x))

        if not points:
            return

        if len(points) < 2:
            return

        def iter_points():
            y = self.canvas.canvasy(self.canvas.winfo_height() - 50)
            for p in points:
                yield p[1]  # x
                yield y  # y
                # yield self.canvas.canvasx(p[1], 1)  # x
                # yield self.canvas.canvasy(y, 1)  # y

        self.canvas.create_line(*iter_points())

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
        self.adjust_scroll((arg+0.05)-0.5)

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
        w2 = w//2
        self.canvas.scan_mark(w2, 0)
        self.canvas.scan_dragto(int(w2-w2*self.scrollfactor), 0, gain=1)
        self.render()
        # self.canvas.xview_scroll(int(self.scrollfactor*5), UNITS)  # no smooth scroll

    def xscrollcommand(self, *_):  # a: str ~= '0.0', b: str ~= '1.0'
        if self.scrollfactor:
            return
        self.xscroll.set(0.45, 0.55)
