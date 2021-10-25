# -*- coding=utf-8 -*-
r"""

"""
from tendo.singleton import SingleInstance, SingleInstanceException

try:
    me = SingleInstance()
except SingleInstanceException:
    import sys
    import ctypes

    ctypes.windll.user32.MessageBoxW(None, "This programm is already running", "Only one instance allowed", 16)
    sys.exit(-1)

import tkinter as tk
import tkinter.messagebox

import os
import sys
import logging

import scripts
from viewer import about
from viewer import settings
from viewer import dataview


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AppStalker")
        self.geometry('{:.0f}x{:.0f}'.format(self.winfo_screenwidth() // 3, self.winfo_screenheight() // 3))

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


def configure_logging():
    filename = os.path.join(scripts.get_appdir(), 'logs', 'viewer.log')
    logging.basicConfig(
        format="{asctime} | {levelname:3.3} | {filename:<15} | {lineno:<3} | {funcName:<15} | {message}",
        style="{",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                filename=filename,
                mode='w',
                encoding='utf-8',
                errors='namereplace'  # https://docs.python.org/3/library/functions.html#open => \N{...}
            )
        ],
        level=logging.INFO if scripts.is_executable() else logging.DEBUG
    )
    # logging.getLogger('PIL').setLevel(logging.WARNING)


def main():
    configure_logging()
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
