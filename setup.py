from distutils.core import setup
import py2exe

setup(data_files = [('res', ['res/checked.ico', 'res/notchecked.ico'])],
      windows=['ntoq_gui.py'],
      options = {
          "py2exe": {"dll_excludes":["MSVCP90.dll"]}
          }
      )

