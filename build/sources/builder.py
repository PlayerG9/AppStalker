import os
from os.path import abspath, join, dirname
import subprocess
import shutil


appdir = abspath(join(dirname(__file__), '..', '..'))
os.chdir(appdir)  # switch to workdir
if 'README.md' not in os.listdir('.'):
    raise EnvironmentError('invalid starting directory')
builddir = join(appdir, 'build', 'build')
distdir = join(appdir, 'build', 'dist')
sourcedir = join(appdir, 'build', 'sources')
projectdir = join(appdir, 'src', 'AppStalker')
PYINSTALLER = join(appdir, '_venv', 'Scripts', 'pyinstaller.exe')


skip_compile = False


CMD = [
    PYINSTALLER,
    '--distpath', distdir,
    '--workpath', builddir,
    '--noconfirm',
    '--clean',
    '--specpath', builddir,

    '--paths', projectdir,
    '--paths', join(projectdir, 'stalker'),

    '--runtime-hook', join(sourcedir, 'hooker.py'),
    '--additional-hooks-dir', sourcedir,

    '--add-data', join(projectdir, 'memory') + os.pathsep + "memory",

    '--noconsole',
    '--icon', join(sourcedir, 'file.ico'),

    '--name', "Stalker",

    join(projectdir, 'stalker', '__main__.pyw')
]

# build stalker
if not skip_compile:
    process = subprocess.run(CMD)
    process.check_returncode()

CMD = [
    PYINSTALLER,
    '--distpath', distdir,
    '--workpath', builddir,
    '--noconfirm',
    '--clean',
    '--specpath', builddir,

    '--paths', projectdir,
    '--paths', join(projectdir, 'viewer'),

    '--runtime-hook', join(sourcedir, 'hooker.py'),
    '--additional-hooks-dir', sourcedir,

    # already collected from stalker
    # '--add-data', join(projectdir, 'memory') + os.pathsep + "memory",

    '--windowed',
    '--icon', join(sourcedir, 'icon.ico'),

    '--name', "Viewer",

    join(projectdir, 'viewer', '__main__.pyw')
]

# build viewer
if not skip_compile:
    process = subprocess.run(CMD)
    process.check_returncode()

os.chdir(distdir)
# remove old programm
if os.path.isdir('AppStalker'):
    shutil.rmtree('AppStalker')
os.mkdir('AppStalker')

# copy files from stalker and viewer (combine them to one programm)
shutil.copytree('Stalker', 'AppStalker', dirs_exist_ok=True)
shutil.copytree('Viewer', 'AppStalker', dirs_exist_ok=True)

os.chdir('AppStalker')  # go into new programm-dir

os.remove(join('memory', 'data.sl3'))  # remove database (should be freshly build on first start)

os.mkdir('logs')  # create dir for logs
os.mkdir('libs')  # create dir for .pyd files
os.mkdir('windll')  # create dir for .dll files

# move specific files
for file in os.listdir():
    if file.startswith(('python',)): continue
    _, ext = os.path.splitext(file)
    if ext == '.pyd':
        shutil.move(file, 'libs')
    elif ext == '.dll':
        shutil.move(file, 'windll')
