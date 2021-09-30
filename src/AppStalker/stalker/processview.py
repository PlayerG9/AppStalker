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
import ctypes
import ctypes.wintypes
import psutil


def get_process() -> psutil.Process:
    pid = get_pid()
    process = psutil.Process(pid=pid)
    return process


def get_pid():
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value
