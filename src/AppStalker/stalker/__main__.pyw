# -*- coding=utf-8 -*-
r"""

"""
from tendo.singleton import SingleInstance

me = SingleInstance()

import schedule
from pystray import Icon, Menu, MenuItem
from pystray._win32 import Icon as IconHint
from PIL import Image
import psutil

import threading
import os
# import sys
import time
import logging
import sqlite3 as sql
import json
import shlex
import atexit

import scripts
from stalker import processview


def add_pidfile():
    with open(pidfilepath, 'w') as file:
        file.write(str(os.getpid()))
    logging.info('pid-file added ({})'.format(os.getpid()))


def remove_pidfile():
    os.remove(pidfilepath)
    logging.info("pid-file removed")


pidfilepath = os.path.join(scripts.get_memdir(), 'pid.share')


class Application:
    def __init__(self):
        logging.info("Creating app")
        self.config = self.get_config()

        tm = self.config['time-mode']
        interval = self.config['time-interval']
        if not isinstance(interval, int) or not (0 < interval <= 60):
            raise ValueError('invalid time-interval {!r}'.format(interval))
        if tm == 'minutes':
            self.job = schedule.every(interval).minutes.at(':00').do(self.task).tag('measurement')
        elif tm == 'seconds':
            self.job = schedule.every(interval).seconds.do(self.task).tag('measurement')
        else:
            raise ValueError('invalid time-mode {!r}'.format(tm))

        self.icon: IconHint = Icon(
            name="where is this displayed?",
            icon=self.get_icon(),
            title="AppStalker",
            menu=Menu(
                MenuItem(
                    text="View",
                    action=self.start_viewer
                ),
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
        DatabaseHandler.init()
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

    @staticmethod
    def setup(icon: IconHint):
        icon.visible = True
        # if '--no-notify' not in sys.argv:
        #     schedule.every(5).seconds.do(lambda: (self.icon.notify("stalker is now running"), schedule.CancelJob)[1])

    def quit(self):
        logging.info("Stop app")
        self.running = False
        self.icon.stop()

    def task(self):
        process = processview.get_process()
        measurements = Measurements(self.config)
        measurements.add(process)

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
        logging.error("Measurement failed", exc_info=exception)
        self.icon.notify(
            title="Measurement failed",
            message="Measurement failed due to an unexpected {}."
                    "({}: {})".format(
                exception.__class__.__name__,
                exception.__class__.__qualname__,
                ''.join(exception.args)
            )
        )

    def start_viewer(self):
        logging.info("Start Viewer.exe")
        try:
            path = os.path.join(scripts.get_appdir(), 'Viewer.exe')
            os.startfile(path)
        except Exception as exception:
            self.warn_error(exception)


class Measurements:
    def __init__(self, config: dict):
        self.config = config  # currently not used

    @staticmethod
    def add(process: psutil.Process):
        logging.debug("Add process to database")
        with sql.connect(scripts.get_dbfile()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT rowid FROM executables WHERE create_time = ? LIMIT 1",
                [process.create_time()]
            )
            exe_id = cursor.fetchone()

            def get(attr: str, form: callable = None):
                try:
                    val = getattr(process, attr)()
                    if form:
                        val = form(val)
                except (AttributeError, ValueError):
                    return None
                return val

            if exe_id:  # exe_id = (exe_id,)
                exe_id = exe_id[0]
            else:
                cursor.execute("INSERT INTO executables "
                               "(name, exe, cmdline, create_time, username) "
                               "VALUES (?, ?, ?, ?, ?)",
                               [
                                   get('name'),
                                   get('exe'),
                                   get('cmdline', shlex.join),
                                   get('create_time'),
                                   get('username')
                               ]
                               )
                exe_id = cursor.lastrowid
            if not exe_id:
                raise IndexError('how the fuck did this happen?')
            cursor.execute("INSERT INTO measurements (exe_id) VALUES (?)", [exe_id])


class DatabaseHandler:
    database_structure = open(os.path.join(scripts.get_memdir(), 'db.sql'), 'r', encoding='utf-8').read()

    @classmethod
    def init(cls):
        logging.info("DatabaseHandler.init()")
        cls.ensure_structure()
        cls.delete_oldest()
        schedule.every(10).minutes.do(cls.delete_oldest).tag('database-utility')

    @staticmethod
    def delete_oldest():
        logging.debug("Delete oldest entrys")
        ts = time.time() - 15552000  # ~6 months (6*30*24*60*60)
        with sql.connect(scripts.get_dbfile()) as conn:
            conn.execute(r"DELETE FROM executables WHERE create_time < ?", [ts])
            conn.execute(r"DELETE FROM measurements WHERE ts < ?;", [ts])

    @classmethod
    def ensure_structure(cls):
        logging.debug("Ensure database-structure")
        with sql.connect(scripts.get_dbfile()) as conn:
            conn.executescript(cls.database_structure)


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
        level=logging.INFO if scripts.is_executable() else logging.DEBUG
    )
    logging.getLogger('PIL').setLevel(logging.WARNING)


def main():
    configure_logging()

    add_pidfile()
    atexit.register(remove_pidfile)

    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
