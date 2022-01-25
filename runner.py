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
import tkinter.filedialog

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest, uic
import main
import os
import tkinter as tk
from tkinter import filedialog, messagebox


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

        # call the show function
        self.show()

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
        dir_path = tkinter.filedialog.askdirectory()
        try:
            os.chdir(dir_path)
        except FileNotFoundError as err:
            tkinter.messagebox.showerror(
                title = "[runner.py/ERROR]",
                message = "[runner.py/ERROR]: Directory does not exist."
            )
        except OSError as err:
            print(err)
        self.line.setText(dir_path)



# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":
    import sys

    # initialize the QtWidget
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_RunnerInstance()

    # running Tkinter modules to make my life easier
    tk_root = tk.Tk()
    tk_root.withdraw()

    # enter main loop
    sys.exit(app.exec_())