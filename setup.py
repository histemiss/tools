from distutils.core import setup
import py2exe

setup(
    data_files = [('res', ['res/checked.ico', 'res/notchecked.ico'])],
    windows =[{
        "script":'ntoq_gui.py',
        "icon_resources":[
            (1, "res/test.ico")
        ]}],
    options = {
        "py2exe": {
            "dll_excludes":["MSVCP90.dll"],
#            "bundle_files":1
        }
    }
)

