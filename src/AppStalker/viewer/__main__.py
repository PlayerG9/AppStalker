# -*- coding=utf-8 -*-
r"""

"""
from tendo.singleton import SingleInstance
me = SingleInstance()

import tkinter as tk


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

    def report_callback_exception(self, exc, val, tb):
        super().report_callback_exception(exc, val, tb)


def main():
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
