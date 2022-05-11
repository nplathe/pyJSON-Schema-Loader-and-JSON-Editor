# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\plathe\PycharmProjects\pyjson-converter-gui\pyJSON_interface.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.curr_descr_label_1 = QtWidgets.QLabel(self.centralwidget)
        self.curr_descr_label_1.setMaximumSize(QtCore.QSize(100, 16777215))
        self.curr_descr_label_1.setIndent(5)
        self.curr_descr_label_1.setObjectName("curr_descr_label_1")
        self.horizontalLayout_4.addWidget(self.curr_descr_label_1)
        self.current_JSON_label = QtWidgets.QLabel(self.centralwidget)
        self.current_JSON_label.setText("")
        self.current_JSON_label.setObjectName("current_JSON_label")
        self.horizontalLayout_4.addWidget(self.current_JSON_label)
        self.pushButton_save_md_JSON = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_save_md_JSON.setMaximumSize(QtCore.QSize(300, 16777215))
        self.pushButton_save_md_JSON.setObjectName("pushButton_save_md_JSON")
        self.horizontalLayout_4.addWidget(self.pushButton_save_md_JSON)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_5.setSpacing(2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.curr_descr_label2 = QtWidgets.QLabel(self.centralwidget)
        self.curr_descr_label2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.curr_descr_label2.setIndent(5)
        self.curr_descr_label2.setObjectName("curr_descr_label2")
        self.horizontalLayout_5.addWidget(self.curr_descr_label2)
        self.current_schema_combo_box = QtWidgets.QComboBox(self.centralwidget)
        self.current_schema_combo_box.setObjectName("current_schema_combo_box")
        self.horizontalLayout_5.addWidget(self.current_schema_combo_box)
        self.pushButton_load_md_JSON = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_load_md_JSON.setMaximumSize(QtCore.QSize(300, 16777215))
        self.pushButton_load_md_JSON.setObjectName("pushButton_load_md_JSON")
        self.horizontalLayout_5.addWidget(self.pushButton_load_md_JSON)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setObjectName("treeView")
        self.verticalLayout_2.addWidget(self.treeView)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1024, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_JSON = QtWidgets.QAction(MainWindow)
        self.actionOpen_JSON.setObjectName("actionOpen_JSON")
        self.actionOpen_YAML = QtWidgets.QAction(MainWindow)
        self.actionOpen_YAML.setObjectName("actionOpen_YAML")
        self.actionAdd_Schema = QtWidgets.QAction(MainWindow)
        self.actionAdd_Schema.setObjectName("actionAdd_Schema")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSelect_Schema = QtWidgets.QAction(MainWindow)
        self.actionSelect_Schema.setObjectName("actionSelect_Schema")
        self.actionCreate_JSON_from_selected_Schema = QtWidgets.QAction(MainWindow)
        self.actionCreate_JSON_from_selected_Schema.setObjectName("actionCreate_JSON_from_selected_Schema")
        self.actionValidate_input_against_selected_schema = QtWidgets.QAction(MainWindow)
        self.actionValidate_input_against_selected_schema.setObjectName("actionValidate_input_against_selected_schema")
        self.actionSave_as_default = QtWidgets.QAction(MainWindow)
        self.actionSave_as_default.setObjectName("actionSave_as_default")
        self.actionLoad_default_for_selected_schema = QtWidgets.QAction(MainWindow)
        self.actionLoad_default_for_selected_schema.setObjectName("actionLoad_default_for_selected_schema")
        self.actionReload_JSON_and_drop_Changes = QtWidgets.QAction(MainWindow)
        self.actionReload_JSON_and_drop_Changes.setObjectName("actionReload_JSON_and_drop_Changes")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_as = QtWidgets.QAction(MainWindow)
        self.actionSave_as.setObjectName("actionSave_as")
        self.menuFile.addAction(self.actionOpen_JSON)
        self.menuFile.addAction(self.actionOpen_YAML)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionAdd_Schema)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoad_default_for_selected_schema)
        self.menuFile.addAction(self.actionSave_as_default)
        self.menuEdit.addAction(self.actionCreate_JSON_from_selected_Schema)
        self.menuEdit.addAction(self.actionValidate_input_against_selected_schema)
        self.menuEdit.addAction(self.actionReload_JSON_and_drop_Changes)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.curr_descr_label_1.setText(_translate("MainWindow", "Current JSON:"))
        self.pushButton_save_md_JSON.setText(_translate("MainWindow", "Save/Overwrite as metadata.json in current directory"))
        self.curr_descr_label2.setText(_translate("MainWindow", "Current Schema:"))
        self.pushButton_load_md_JSON.setText(_translate("MainWindow", "Load metadata.json from current directory"))
        self.pushButton.setText(_translate("MainWindow", "Set new directory!"))
        self.pushButton_2.setText(_translate("MainWindow", "Get current directory!"))
        self.pushButton_3.setText(_translate("MainWindow", "Select directory!"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen_JSON.setText(_translate("MainWindow", "Open JSON..."))
        self.actionOpen_YAML.setText(_translate("MainWindow", "Open YAML..."))
        self.actionAdd_Schema.setText(_translate("MainWindow", "Add Schema..."))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences..."))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSelect_Schema.setText(_translate("MainWindow", "Select Schema"))
        self.actionCreate_JSON_from_selected_Schema.setText(_translate("MainWindow", "Create Blank from selected schema"))
        self.actionValidate_input_against_selected_schema.setText(_translate("MainWindow", "Validate input against selected schema"))
        self.actionSave_as_default.setText(_translate("MainWindow", "Save as default for selected schema"))
        self.actionLoad_default_for_selected_schema.setText(_translate("MainWindow", "Load default for selected schema"))
        self.actionReload_JSON_and_drop_Changes.setText(_translate("MainWindow", "Reload JSON and drop Changes..."))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave_as.setText(_translate("MainWindow", "Save as..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
