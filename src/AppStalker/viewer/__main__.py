# -*- coding=utf-8 -*-
r"""

"""
from tendo.singleton import SingleInstance
me = SingleInstance()

import tkinter as tk

import os

import scripts


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        iconpath = os.path.join(scripts.get_memdir(), 'icon.ico')
        if os.path.isfile(iconpath):
            self.iconbitmap(iconpath)

        self.menu = self['menu'] = tk.Menu(self, tearoff=0)
        self.menu.add_command(label='👁', command=self.event_view)
        self.menu.add_command(label='⚙', command=self.event_settings)
        self.menu.add_command(label='Ⓘ', command=self.event_about)

    def report_callback_exception(self, exc, val, tb):
        super().report_callback_exception(exc, val, tb)

    def event_view(self):
        pass

    def event_settings(self):
        pass

    def event_about(self):
        pass


def main():
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
