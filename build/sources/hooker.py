import sys
import os

BASE = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE, 'libs'))
os.add_dll_directory(os.path.join(BASE, 'windll'))
