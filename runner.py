# ----------------------------------------
# pyJSON Converter + GUI runner module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------

import os

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest, uic

import tkinter as tk
from tkinter import messagebox, filedialog

import main
from deploy_files import deploy_schema
from schema_model import TreeClass, TreeItem

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

class Ui_RunnerInstance(QtWidgets.QMainWindow):
    def __init__(self):

        # we first call init from the super class, then load the UI file from designer
        super(Ui_RunnerInstance, self). __init__()
        uic.loadUi('main_window.ui', self)

        # adding in the signals for the line
        self.line = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.line.setText(os.getcwd())

        # adding in the signals for the buttons
        self.button_1 = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button_2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button_3 = self.findChild(QtWidgets.QPushButton, "pushButton_3")
        self.button_1.clicked.connect(self.wdsetter)
        self.button_2.clicked.connect(self.wdgetter)
        self.button_3.clicked.connect(self.diropener)

        # adding in the action functions
        self.openJSON = self.findChild(QtWidgets.QAction, 'actionOpen_JSON')
        self.openJSON.setStatusTip("Open a JSON file for editing. Gets validated against selected schema.")
        self.openJSON.triggered.connect(self.jsonopener)

        self.openJSON = self.findChild(QtWidgets.QAction, 'actionOpen_YAML')
        self.openJSON.setStatusTip("Open a YAML file for conversion and editing. Gets validated against selected schema.")
        self.openJSON.triggered.connect(self.yamlopener)

        # TreeView
        self.TreeView = self.findChild(QtWidgets.QTreeView, 'treeView')

        # call the show function
        self.show()

    # Button Function Definitions
    def wdgetter(self):
        result = os.getcwd()
        self.line.setText(result)

    def wdsetter(self):
        result = str(self.line.text())
        if os.path.isdir(result):
            self.button_1.setText("Success!")
            os.chdir(result)
            QtTest.QTest.qWait(2000)
            self.button_1.setText("Set new directory!")
        else:
            self.button_1.setText("ERROR: Check the path!")
            QtTest.QTest.qWait(2000)
            self.button_1.setText("Set new directory!")

    def diropener(self):
        dir_path = tk.filedialog.askdirectory()
        try:
            os.chdir(dir_path)
        except FileNotFoundError as err:
            tk.messagebox.showerror(
                title = "[runner.diropener/ERROR]",
                message = "[runner.diropener/ERROR]: Directory does not exist."
            )
        except OSError as err:
            print(err)
            print("[runner.diropener/INFO]: This error is created by cancelling the directory dialog and can be ignored...")
        self.line.setText(dir_path)

    # Definition Actions MenuBar
    def jsonopener(self):
        try:
            filepath = tk.filedialog.askopenfilename(filetypes = (('Java Script Object Notation', '*.json'),('All Files', '*.*')))
        except FileNotFoundError as err:
            print(err)
            tk.messagebox.showerror(
                title = "[runner.jsonopener/ERROR]",
                message = "[runner.jsonopener/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            print(err)
        print(filepath) # TODO fill this with life from main.py

    def yamlopener(self):
        try:
            filepath = tk.filedialog.askopenfilename(filetypes = (('YAML Ain\'t Markup Language', '*.yaml'),('All Files', '*.*')))
        except FileNotFoundError as err:
            print(err)
            tk.messagebox.showerror(
                title = "[runner.jsonopener/ERROR]",
                message = "[runner.jsonopener/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            print(err)
        print(filepath) # TODO fill this with life from main.py

# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":
    import sys

    # running Tkinter modules to make my life easier
    tk_root = tk.Tk()
    tk_root.withdraw()

    # initialize the QtWidget
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_RunnerInstance()

    # Set the Script Dir and do some checkups.
    script_dir = os.getcwd()
    if not os.path.isdir(os.path.join(script_dir, "Schemas")):
        print("[runner.main/INFO]: Schemas Directory is missing! Creating...")
        try:
            os.makedirs(os.path.join(script_dir, "Schemas"), exist_ok = True)
        except OSError as err:
            str_message = "[runner.main/FATAL]: Cannot create directory. Please check permissions!"
            tk.messagebox.showerror("[runner.main/FATAL]", str_message)
    if not os.path.isfile(os.path.join(script_dir, "Schemas/default.json")):
        print("[runner.main/INFO]: Default File is missing! Deploying...")
        deploy_schema(os.path.join(script_dir, "Schemas"))

    # loading the config of the tool

    # setup the view for the first time
    frame = main.decode_function('Schemas/default.json')
    pre_json = main.schema_to_py_gen(frame)
    pre_descr = main.schema_to_ref_gen(frame)
    model = main.py_to_tree(pre_json, pre_descr)

    ui.TreeView.setModel(model)

    # enter main loop
    sys.exit(app.exec_())