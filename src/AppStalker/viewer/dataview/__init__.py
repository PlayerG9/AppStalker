# -*- coding: utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *


class DataView(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="View")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
        )
        self.canvas.grid(row=0, column=0, sticky=NSEW)
        self.canvas.bind('<Button-2>', self.b2_down)
        self.canvas.bind('<B2-Motion>', self.b2_motion)

        self.xscroll = tk.Scrollbar(self, orient=HORIZONTAL, command=self.xview)
        self.xscroll.grid(row=1, column=0, sticky=EW)
        self.xscroll.bind('<ButtonRelease-1>', lambda e: self.undo_scroll())

        self.scrollfactor = 0.0

        self.canvas.configure(xscrollcommand=self.xscrollcommand)

    ####################################################################################################################
    # rendering
    ####################################################################################################################

    def render(self):
        pass

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
        # self.canvas.xview_scroll(int(self.scrollfactor*5), UNITS)  # no smooth scroll

    def xscrollcommand(self, *_):  # a: str ~= '0.0', b: str ~= '1.0'
        if self.scrollfactor:
            return
        self.xscroll.set(0.45, 0.55)
