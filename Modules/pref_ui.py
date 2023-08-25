# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Preferences Dialog
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# ----------------------------------------
"""
A small dialog class, extending on the converted ui file.
"""
# ----------------------------------------
# Libraries
# ----------------------------------------

import os
import json

from PySide6.QtWidgets import QDialog

from Modules.deploy_files import save_config
from UserInterfaces.pyJSON_preferences import Ui_PrefDiag

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

class ui_preferences(QDialog, Ui_PrefDiag):

    def __init__(self, script_dir = ""):

        # call super constructor and setup ui
        super(ui_preferences, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Preferences")

        # set script dir
        if script_dir == "":
            self.script_dir = os.getcwd()
        else:
            self.script_dir = script_dir

        # load config and set values
        self.config = json.load(open(os.path.join(self.script_dir, "pyJSON_conf.json"), encoding = "utf8"),
                           cls = json.JSONDecoder)
        self.checkBox_verboseLog.setChecked(self.config["verbose_logging"])
        self.checkBox_ShowErrors.setChecked(self.config["show_error_representation"])

        # set signals
        self.pushButton_save.clicked.connect(self.set_prefs)
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.checkBox_verboseLog.stateChanged.connect(self.change_verbose_Log)
        self.checkBox_ShowErrors.stateChanged.connect(self.change_error_represenation)

    def change_verbose_Log(self):
        self.config["verbose_logging"] = self.checkBox_verboseLog.isChecked()

    def change_error_represenation(self):
        self.config["show_error_representation"] = self.checkBox_ShowErrors.isChecked()

    def set_prefs(self):
        save_config(self.script_dir, self.config)
        self.close()

    def cancel(self):
        self.close()