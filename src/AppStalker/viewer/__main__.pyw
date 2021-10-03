# -*- coding=utf-8 -*-
r"""

"""
from tendo.singleton import SingleInstance
me = SingleInstance()

import tkinter as tk
import tkinter.messagebox

import os
import sys

import scripts
import about
import settings
import dataview


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AppStalker")

        iconpath = os.path.join(scripts.get_memdir(), 'icon.ico')
        if os.path.isfile(iconpath):
            self.iconbitmap(iconpath)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu = self['menu'] = tk.Menu(self, tearoff=0)
        self.menu.add_command(label='👁', command=self.event_view)
        self.menu.add_command(label='⚙', command=self.event_settings)
        self.menu.add_command(label='Ⓘ', command=self.event_about)

        self.view = dataview.DataView(self)
        self.settings = settings.Settings(self)
        if '--settings' in sys.argv:
            self.frame: tk.Widget = self.settings
        else:
            self.frame: tk.Widget = self.view
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def report_callback_exception(self, exc, val, tb):
        super().report_callback_exception(exc, val, tb)
        tk.messagebox.showerror(
            "an error occured",
            "{}: {}".format(val.__class__.__qualname__, val)
        )

    def event_view(self):
        if self.frame is self.view:
            return
        self.frame.grid_remove()
        self.frame = self.view
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def event_settings(self):
        if self.frame is self.settings:
            return
        self.frame.grid_remove()
        self.frame = self.settings
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def event_about(self):
        about.About(self)


def main():
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
