# -*- coding=utf-8 -*-
r"""

"""
from tendo.singleton import SingleInstance
me = SingleInstance()

import schedule
from pystray import Icon, Menu, MenuItem
from pystray._win32 import Icon as IconHint
from PIL import Image

import threading
import os
import time
import logging
import sqlite3 as sql
import json

import scripts
import processview


class Application:
    def __init__(self):
        logging.info("Creating app")
        self.config = self.get_config()

        tm = self.config['time-mode']
        interval = self.config['time-interval']
        if not isinstance(interval, int) or not (0 < interval <= 60):
            raise ValueError('invalid time-interval {!r}'.format(interval))
        if tm == 'minutes':
            self.job = schedule.every(interval).minutes.at(':00').do(self.job)
        elif tm == 'seconds':
            self.job = schedule.every(interval).seconds.do(self.job)
        else:
            raise ValueError('invalid time-mode {!r}'.format(tm))

        self.icon: IconHint = Icon(
            name="where is this displayed?",
            icon=self.get_icon(),
            title="AppStalker",
            menu=Menu(
                MenuItem(
                    text="Quit",
                    action=self.quit
                )
            )
        )

        self.schedule_thread = threading.Thread(target=self.schedule_handler, daemon=True)
        self.running = None

    def run(self):
        logging.info("start running")
        self.running = True
        self.schedule_thread.start()
        self.icon.run()  # I would prefer if icon.run() is in a thread but then the systray-icon-menu won't show
        self.icon.visible = False

    def schedule_handler(self):
        while self.running:
            try:
                schedule.run_pending()
            except Exception as exception:
                self.warn_error(exception)
                raise exception
            time.sleep(0.5)

    def quit(self):
        logging.info("Stop app")
        self.running = False
        self.icon.stop()

    def task(self):
        process = processview.get_process()

    ####################################################################################################################

    @staticmethod
    def get_icon() -> Image.Image:
        iconpath = os.path.join(scripts.get_memdir(), 'icon.png')
        try:
            image = Image.open(iconpath)
            logging.debug("Opened icon")
        except FileNotFoundError:
            logging.warning("Failed to load icon")
            image = Image.new('RGBA', [30, 30], 'cyan')
        return image

    @staticmethod
    def get_config() -> dict:
        configpath = os.path.join(scripts.get_memdir(), 'config.json')
        configfile = open(configpath)
        try:
            config = json.load(configfile)
        finally:
            configfile.close()
        return config

    def warn_error(self, exception: Exception):
        if not self.icon.HAS_NOTIFICATION: return
        self.icon.notify(
            title="Measurement failed",
            message="Measurement failed due to an unexpected {}."
                    "({}: {})".format(
                exception.__class__.__name__,
                exception.__class__.__qualname__,
                ''.join(exception.args)
            )
        )


def configure_logging():
    filename = os.path.join(scripts.get_appdir(), 'logs', 'stalker.txt')
    logging.basicConfig(
        format="{asctime} | {levelname:<10} | {filename:<15} | {lineno:<3} | {funcName:<15} | {message}",
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
        level=logging.DEBUG
    )
    logging.getLogger('PIL').setLevel(logging.WARNING)


def main():
    configure_logging()
    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
