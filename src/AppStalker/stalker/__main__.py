# -*- coding=utf-8 -*-
r"""
while True:
    user32 = ctypes.windll.user32
    h_wnd = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))

    process_id = pid.value
    process = psutil.Process(pid.value)
    process_name = process.name()
    process_start = str(process)[-10:-2]
    process_file = process.cmdline()

    if process_name not in process_list.keys():
        process_list[process_name] = [process_id, [process_start], process_file]

    if process_start not in process_list[process_name][1]:
        process_list[process_name][1].append(process_start)

    if lastprocess != process_name and process_name not in ["System Idle Process"]:
        cur_time = time.asctime(time.localtime(time.time())).split(" ")[3]
        time_list[-1] = [cur_time, process_name]
        time_list.append([])

    lastprocess = process_name
    time.sleep(1)
    counter += 1
    if counter >= countermax:
        counter = 0
        time_list[-1] = [time.asctime(time.localtime(time.time())).split(" ")[3], process_name]
        save()
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

import scripts


class Application:
    def __init__(self):
        self.job = schedule.every().minute.at(':00').do(self.task)
        self.icon: IconHint = Icon(
            name="Name",
            icon=self.get_icon(),
            title="Title",
            menu=Menu(
                MenuItem(
                    text="Quit",
                    action=self.quit
                )
            )
        )
        self.schedule_thread = threading.Thread(target=self.schedule_handler, name="SysTrayIcon", daemon=True)
        self.running = None

    def run(self):
        self.running = True
        self.schedule_thread.start()
        self.icon.run()  # I would prefer if icon.run() is in a thread but then the systray-icon won't show
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
        self.running = False
        self.icon.stop()

    def task(self):
        self.icon.notify(title="Measuring", message=__file__)

    ####################################################################################################################

    @staticmethod
    def get_icon() -> Image.Image:
        iconpath = os.path.join(os.path.dirname(__file__), 'memory', 'icon.png')
        try:
            image = Image.open(iconpath)
        except FileNotFoundError:
            image = Image.new('RGBA', [30, 30], 'cyan')
        return image

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
        format="{time} | {level} | {filename} | {fileno} | {func} | {msg}",
        style="{",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                filename=filename,
                mode='w',
                encoding='utf-8'
            )
        ]
    )


def main():
    configure_logging()
    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
