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
        logging.info("build app")

        self.title("AppStalker")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry('{:.0f}x{:.0f}'.format(sw // 3, sh // 3))
        self.minsize(sw // 4, sh // 4)
        self.maxsize(sw // 2, sh // 2)

        iconpath = os.path.join(scripts.get_memdir(), 'icon.ico')
        if os.path.isfile(iconpath):
            self.iconbitmap(iconpath)
        else:
            logging.warning('missing icon: {}'.format(iconpath))

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
        logging.error("an error occured", exc_info=exc)
        # super().report_callback_exception(exc, val, tb)
        tk.messagebox.showerror(
            "an error occured",
            "{}: {}".format(val.__class__.__qualname__, val)
        )

    def event_view(self):
        logging.debug("event_view")
        if self.frame is self.view:
            return
        logging.info("Change to view")
        self.frame.grid_remove()
        self.frame = self.view
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def event_settings(self):
        logging.debug("event_settings")
        if self.frame is self.settings:
            return
        logging.info("Change to settings")
        self.frame.grid_remove()
        self.frame = self.settings
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def event_about(self):
        logging.debug("event_about")
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
    logging.getLogger('PIL').setLevel(logging.WARNING)


def main():
    configure_logging()
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
