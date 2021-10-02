# -*- coding: utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *


class DataView(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="View")
        self.bind('<Map>', lambda e: self.on_place())

        row = 0

        tk.Label(self, text="").grid(row=row, column=0, sticky=W)

    def on_place(self):
        pass
