# -*- coding=utf-8 -*-
r"""

"""
import tkinter as tk
from tkinter.constants import *

import os
import logging

from PIL import Image, ImageTk

import scripts


class About(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.attributes('-toolwindow', True)
        self.title('AppStalker')

        width, height = 400, 128
        x = 135

        bg = 'white'

        self.geometry('{:.0f}x{:.0f}'.format(width, height))
        self.configure(bg=bg)
        self.resizable(False, False)

        iconpath = os.path.join(scripts.get_memdir(), 'icon.png')
        if os.path.isfile(iconpath):
            image: Image.Image = Image.open(iconpath)
            image = image.resize([height, height])
        else:
            image = Image.new('RGBA', [height, height])
            logging.warning('missing icon: {}'.format(iconpath))

        self.photoimage = ImageTk.PhotoImage(image)
        del image

        self.label_image = tk.Label(self, bg=bg, image=self.photoimage)
        self.label_image.place(x=0, y=0)

        self.header = tk.Label(self, bg=bg, font='16', text="AppStalker")
        self.header.place(x=x, y=5)
        self.text = tk.Message(self, bg=bg, anchor=NW, text=r"""
this software is in beta
no warranty
if you destroy your entire computer or create a robot uprising. that's on you man.
        """.strip(), width=width - x - 5)
        self.text.place(x=x, y=30, width=width - x, height=90)
        self.copyright = tk.Label(self, bg=bg, text="Copyright © 2021 PlayerG9")
        self.copyright.place(x=x, y=105)

        logging.debug('focus_force() + grab_set()')
        self.focus_force()
        self.grab_set()
        self.wait_window()
        logging.debug('{} gets destroyed'.format(self))
