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
        self.canvas.bind('<Configure>', lambda e: self.render())

        self.xscroll = tk.Scrollbar(self, orient=HORIZONTAL, command=self.xview)
        self.xscroll.grid(row=1, column=0, sticky=EW)
        self.xscroll.bind('<ButtonRelease-1>', lambda e: self.undo_scroll())

        self.canvas.configure(xscrollcommand=self.xscrollcommand)

        self.lbl = tk.Label(self, anchor=W, text="...")
        self.lbl.grid(row=2, columnspan=2, sticky=EW)
        self.canvas.bind('<Motion>', self.evt_motion)
        self.debug_label = tk.Label(self, text='...')
        self.debug_label.grid(row=3, columnspan=2, sticky=EW)

        # self.render()
        # self.canvas.create_text(0, 0, text="Hello World")
        # self.canvas.create_rectangle(0, 0, 100, 100, fill='pink')
        # self.canvas.create_rectangle(200, 200, 400, 300, fill='pink')

    @classmethod
    def init_colormap(cls):
        import random

        def get_tone() -> int:
            return random.randint(0, 127)  # + 127

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

        if len(points) < 2:
            self.canvas.create_text(
                self.canvas.canvasx(self.winfo_width()//3),
                self.canvas.canvasy(self.winfo_height()//2, 1),
                text="Nothing here"
            )
            return

        high = 1
        last_exe_id = None
        joints = []

        ay = self.canvas.winfo_height() - 20
        by = ay - 20

        for exe_id, x in points:
            if exe_id is not last_exe_id:
                high = not high
                last_exe_id = exe_id

                joints.append((x, ay if high else by))

                if len(joints) >= 2:
                    color = self.colormap[exe_id]
                    self.canvas.create_line(
                        *joints,
                        fill=color,
                        width=5,
                        capstyle=BUTT,
                        joinstyle=ROUND,
                        smooth=False
                    )

                joints.clear()

            joints.append((x, ay if high else by))

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
