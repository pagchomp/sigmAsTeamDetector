import sys
from cx_Freeze import setup, Executable

import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

#if sys.platform == "win32":
#    base = "Win32GUI"
base = None

setup(name = "sigmA's Team Detector" ,
      version = "1.6" ,
      description = "" ,
      # options = {'build_exe': build_options},
      executables = [Executable("sigmAsTeamDetector.py", base = base)])