# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Main Module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# Callejon - Metropolis
# Tallah - The Generation Of Danger
# ----------------------------------------
# Libraries
# ----------------------------------------
# import 3rd party and system libraries
import json
import logging
import logging as lg
import multiprocessing
import os
import platform
import regex as re
import shutil
import subprocess

# import tkinter modules
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

# import PyQt libraries
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QModelIndex, Qt, QPoint
from PyQt5.QtGui import QBrush, QColor, QGuiApplication, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QComboBox, QStyledItemDelegate, QStyle, QWidget, QVBoxLayout, \
    QFileDialog

# import of modules
import jsonio_lib
import jsonsearch_lib
from deploy_files import deploy_schema, deploy_config, save_config, saveMainIndex
from ModifiedTreeModel import ModifiedTreeClass as TreeClass

# import the converted user interface
from pyJSON_interface import Ui_MainWindow


# ----------------------------------------
# Variables and Functions
# ----------------------------------------



# Special delegator for the tree model in order to handle enums in the schema
class EnumDropDownDelegate(QStyledItemDelegate):
    """
    A custom delegate class based off QStyledItemDelegate. Passes most data to the standard editor, except for
    enumerators, which is noted down in the schema.
    """
    def __init__(self):
        """
        Constructor
        """
        super(EnumDropDownDelegate, self).__init__()

    def createEditor(self, parent, option, index):
        """
        When data is to be edited, the delegate provides an Editor, which is, most of the time, a QWidget.
        TODO: Implement QSpinBoxes for integers and floats

        Args:
            parent (object): parent of the QWidget to be.
            option (object): option that might be passed to the constructor of the QWidget
            index (QModelIndex): the QModelIndex of the item that was clicked

        Returns:
            QWidget: the editor QWidget - a drop down menu for enumerators, a line edit (the standard) otherwise
        """
        pathList = []
        curItem = index.model().getItem(index)
        pathList.append(curItem.getData(0))
        while curItem.getParent().getData(0) != "Schema Key":
            curItem = curItem.getParent()
            pathList.append(curItem.getData(0))
        currSchem = json.load(open(os.path.join(script_dir, "Schemas", config["last_schema"]), encoding = "utf8"), cls=json.JSONDecoder)
        while len(pathList) > 0:
            currKey = pathList.pop()
            currSchem = currSchem["properties"][currKey]
        if "enum" in currSchem.keys():
            lg.debug("custom delegate editor selected...")
            dropDownEnum = QtWidgets.QComboBox(parent)
            dropDownEnum.setFrame(False)
            dropDownEnum.addItem("(none)")
            for i in currSchem["enum"]:
                dropDownEnum.addItem(i)
            return dropDownEnum
        else:
            widget = QStyledItemDelegate.createEditor(QStyledItemDelegate(), parent, option, index)
            return widget

    def setEditorData(self, editor, index):
        """
        Passes the data from the model to the editor

        Args:
            editor (QWidget): the QWidget for which the data needs to be set
            index (QModelIndex): the index of the item to be edited

        Returns:
        """
        if isinstance(editor, QtWidgets.QComboBox):
            item = index.model().getItem(index)
            value = item.getDataArray()[2]
            if value == '':
                editor.setCurrentText("(none)")
            else:
                editor.setCurrentText(value)
        else:
            QStyledItemDelegate.setEditorData(QStyledItemDelegate(), editor, index)

    def setModelData(self, editor, model, index):
        """
        Passes data from the editor to the model
        Args:
            editor (QWidget): the QWidget for which the data needs to be set
            model (TreeClass): the model of the TreeView
            index (QModelIndex): the index of the item to be edited

        Returns:
        """
        if isinstance(editor, QtWidgets.QComboBox):
            value = editor.currentText()
            if value == "(none)":
                model.setData(index, "", Qt.EditRole)
            else:
                model.setData(index, value, Qt.EditRole)
        else:
            QStyledItemDelegate.setModelData(QStyledItemDelegate(), editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        """
        updates the QWidget, e.g. when the size of the window changes

        Args:
            editor (QWidget): the QWidget which needs to get updated
            option (Object): option that needs to be passed to setGeometry
            index (QModelIndex): the index of the item the editor is located at

        Returns:
        """
        if index.column == 2 and index.model().data(index, Qt.EditRole).getDataArray()[3]:
            editor.setGeometry(option.rect)
        else:
            QStyledItemDelegate.updateEditorGeometry(QStyledItemDelegate(), editor, option, index)


# class for a small additional window showing search results.
class SearchWindow(QWidget):
    """
    The SearchWindow Class is a simple QWidget for showing search results in a list-view.
    """
    def __init__(self):
        """
        Constructor containing all the signal-slot-connections and information about the window
        """
        super(SearchWindow, self).__init__()

        # Layout, Formatting
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle("pyJSON - Search Results")

        # Widgets
        self.searchListView = QtWidgets.QListView()
        self.searchListView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.searchListView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.searchListView.customContextMenuRequested.connect(self.onCustomContextMenu)

        # Add Widgets to layout
        layout.addWidget(self.searchListView)

    def onCustomContextMenu(self, index):
        """
        Custom context Menu

        Args:
            index (QPoint): The QPoint the right click was executed at.

        Returns:
        """
        list_index = self.searchListView.indexAt(index)
        if list_index.isValid():
            item_menu = QtWidgets.QMenu("Item menu")
            entry1 = item_menu.addAction("Open...")
            entry1.triggered.connect(self.openFile)
            entry2 = item_menu.addAction("Open File Location...")
            entry2.triggered.connect(self.openFileLocation)
            item_menu.exec_(self.searchListView.viewport().mapToGlobal(index))

    def openFile(self):
        """
        A function to initialise opening the selected path in the ListView with the associated tool. Conviniently enough
        with Windows, explorer.exe passes the attempt of opening a file to the app for us.

        Returns:
        """
        index = self.searchListView.selectedIndexes()[0]
        item = self.searchListView.model().itemFromIndex(index)
        if platform.system() == "Windows":
            subprocess.Popen('explorer '+item.text())

    def openFileLocation(self):
        """
        Opens the path to the file.

        Returns:
        """
        index = self.searchListView.selectedIndexes()[0]
        item = self.searchListView.model().itemFromIndex(index)
        if platform.system() == "Windows":
            path = os.path.dirname(item.text())
            lg.info(path)
            subprocess.Popen('explorer '+path)


# class extension of my GUI, containing all functions related to the GUI
class UiRunnerInstance(QMainWindow, Ui_MainWindow):
    """
    The main window class, which is a subclass of the converted interface class generated from the ui XML file. It contains
    all the slots for functionality of the ui.
    """
    def __init__(self):
        """
        Constructor. Sets up all signals and slots, decorates the buttons, creates status tips, links the deleagte to
        the 2nd column, etc...
        """
        # we first call init from the super class, then load the translated py file file from designer
        super(UiRunnerInstance, self).__init__()
        self.setupUi(self)

        title = "pyJSON Schema Loader and JSON Editor"
        self.setWindowTitle(title)

        # text label for the current dir
        self.label_curDir.setText(os.getcwd())

        # adding in the signals for the buttons
        self.pushButton_dirSel.clicked.connect(self.diropener)
        self.pixmap_dirOpen = getattr(QStyle, "SP_FileDialogNewFolder")
        self.icon_dirOpen = self.style().standardIcon(self.pixmap_dirOpen)
        self.pushButton_dirSel.setIcon(self.icon_dirOpen)
        self.pushButton_dirSel.setText("")

        self.pushButton_new.clicked.connect(self.set_blank_from_schema)
        self.pixmap_new = getattr(QStyle, "SP_FileIcon")
        self.icon_new = self.style().standardIcon(self.pixmap_new)
        self.pushButton_new.setIcon(self.icon_new)
        self.pushButton_new.setText("")

        self.pushButton_open.clicked.connect(self.jsonopener)
        self.pixmap_open = getattr(QStyle, "SP_DirOpenIcon")
        self.icon_open = self.style().standardIcon(self.pixmap_open)
        self.pushButton_open.setIcon(self.icon_open)
        self.pushButton_open.setText("")

        self.pushButton_save.clicked.connect(self.save_function)
        self.pixmap_save = getattr(QStyle, "SP_DialogSaveButton")
        self.icon_save = self.style().standardIcon(self.pixmap_save)
        self.pushButton_save.setIcon(self.icon_save)
        self.pushButton_save.setText("")

        self.pushButton_search.clicked.connect(self.search_Dirs)
        self.pixmap_search = getattr(QStyle, "SP_FileDialogContentsView")
        self.icon_search = self.style().standardIcon(self.pixmap_search)
        self.pushButton_search.setIcon(self.icon_search)
        self.pushButton_search.setText("")

        self.pushButton_addSchema.clicked.connect(self.copy_schema_to_storage)
        self.pixmap_addSchema = getattr(QStyle, "SP_FileDialogDetailedView")
        self.icon_addSchema = self.style().standardIcon(self.pixmap_addSchema)
        self.pushButton_addSchema.setIcon(self.icon_addSchema)
        self.pushButton_addSchema.setText("")

        # JSON related functions in the menu bar
        self.actionOpen_JSON.triggered.connect(self.jsonopener)
        self.actionSave_as.triggered.connect(self.save_as_function)
        self.actionSave.triggered.connect(self.save_function)
        self.actionReload_JSON_and_drop_Changes.triggered.connect(self.reloader_function)

        # Schema related functions in the menu bar
        self.actionAdd_Schema.triggered.connect(self.copy_schema_to_storage)
        self.actionCreate_JSON_from_selected_Schema.triggered.connect(self.set_blank_from_schema)
        self.actionLoad_default_for_selected_schema.triggered.connect(self.load_default)
        self.actionSave_as_default.triggered.connect(self.save_default)
        self.actionValidate_input_against_selected_schema.triggered.connect(self.validate_Function)

        # Index related functions in the menu bar
        self.actionCheck_indexes.triggered.connect(self.callWatchdog)

        # Drop-Down Menu
        self.curr_schem_ddm = self.findChild(QComboBox, "current_schema_combo_box")
        self.curr_schem_ddm.currentTextChanged.connect(self.combobox_selected)

        self.searchList = None

        # set the delegate for the view
        self.delegate = EnumDropDownDelegate()
        self.TreeView.setItemDelegateForColumn(2, self.delegate)

        # call the show function
        self.show()


    # Button Function Definitions

    def diropener(self):
        """
        lets the user open a directory to be indexed.

        Returns:
        """
        #dir_path = os.path.normpath(tk.filedialog.askdirectory())
        dir_path = os.path.normpath(
            QFileDialog.getExistingDirectory(
                caption = "Select Directory for indexing",
                directory = config["last_dir"]
            )
        )
        try:
            os.chdir(dir_path)
            if dir_path == '' or dir_path == '.':
                raise OSError("[pyJSON.diropener/WARN]: Directory selection aborted!")
            config["last_dir"] = dir_path
            save_config(script_dir, config)
            self.label_curDir.setText(dir_path)
            jsonsearch_lib.StartIndex(script_dir, dir_path, index_dict)
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.diropener/ERROR]",
                message="[pyJSON.diropener/ERROR]: Directory does not exist."
            )
        except OSError as err:
            if re.match(re.compile('\[WinError\s123\]'), str(err)):
                lg.warning("[pyJSON.diropener/WARN]: Directory selection aborted!")
            else:
                lg.warning(err)
        self.dirselect_repopulate()


    # Definition Actions MenuBar

    def jsonopener(self):
        """
        Reads a JSON document, prepares the model for the TreeView widget and attaches it to said view.

        Returns:
        """
        try:
            #filepath_str = tk.filedialog.askopenfilename(
            #    filetypes=(('Java Script Object Notation', '*.json'), ('All Files', '*.*')))
            filepath_str = QFileDialog.getOpenFileName(
                caption = "Open a JSON Document...",
                directory = config["last_dir"],
                filter = "Java Script Object Notation (*.json);; All Files (*.*)"
            )[0]
            if filepath_str == '':
                raise OSError("[pyJSON.jsonopener/WARN]: File Selection aborted!")
            if not os.path.isfile(filepath_str):
                raise FileNotFoundError("[pyJSON.jsonopener/ERROR]: Specified file does not exist.")

            filepath = os.path.normpath(filepath_str)
            read_frame = jsonio_lib.decode_function(filepath)
            if type(read_frame) is int and read_frame == -999:
                raise FileNotFoundError("[pyJSON.jsonopener/ERROR]: Specified file does not exist.")
            # TODO: VALIDATION TESTING HERE
            schema_read = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
            schema_frame = jsonio_lib.schemaToPyGen(schema_read, mode = "description")
            schema_title = jsonio_lib.schemaToPyGen(schema_read, mode = "title")
            schema_type = jsonio_lib.schemaToPyGen(schema_read, mode = "type")
            new_tree = jsonio_lib.py_to_tree(read_frame, schema_type, schema_title, schema_frame,
                                             TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))
            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
            if new_tree:
                config["last_JSON"] = filepath
                save_config(script_dir, config)
                self.curr_json_label.setText(filepath)

        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.jsonopener/ERROR]",
                message="[pyJSON.jsonopener/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            lg.error(err)


    def combobox_repopulate(self):
        """
        sets up the QComboBox for schemas and updates its entries, if a schema gets added.

        Returns:
        """
        self.curr_schem_ddm.blockSignals(True)
        if self.curr_schem_ddm.count != 0:
            self.curr_schem_ddm.clear()
        schema_list = os.listdir(os.path.join(script_dir, "Schemas"))
        for x in schema_list:
            self.curr_schem_ddm.addItem(x)
        self.curr_schem_ddm.update()
        self.curr_schem_ddm.blockSignals(False)


    def dirselect_repopulate(self):
        """
        Sets up the other QCombobox utilised for the indexed directories and updates its entries accordingly.

        Returns:
        """
        selection_list = list(index_dict.keys())
        selection_list.remove("cur_index")
        self.curr_dir_comboBox.blockSignals(True)
        if self.curr_dir_comboBox.count != 0:
            self.curr_dir_comboBox.clear()
        self.curr_dir_comboBox.addItem("  (none)")
        if selection_list is not None and type(selection_list) is list:
            for i in selection_list:
                self.curr_dir_comboBox.addItem(i)
        else:
            if selection_list is not None:
                self.curr_dir_comboBox.addItem(selection_list)
        if config["last_dir"] is not None:
            self.curr_dir_comboBox.setCurrentText(config["last_dir"])
        else:
            self.curr_dir_comboBox.setCurrentText("  (none)")
        self.curr_dir_comboBox.blockSignals(False)


    def combobox_selected(self):
        """
        A slot that gets triggered when the QComboBox emits a changed-Signal. Sets the new schema and reconstructs
        the model for the TreeView

        Returns:

        """
        lg.info("\n----------\nswapped schema!\n----------")
        selected = self.curr_schem_ddm.currentText()
        try:
            schema = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", selected))
            if type(schema) is int and schema == -999:
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.combobox_selected/ERROR]: Schema File is missing!")
            schema_frame = jsonio_lib.schemaToPyGen(schema, mode = "description")
            schema_title = jsonio_lib.schemaToPyGen(schema, mode = "title")
            schema_type = jsonio_lib.schemaToPyGen(schema, mode = "type")

            if not config["last_JSON"] is None:
                read_frame = jsonio_lib.decode_function(config["last_JSON"])
                new_tree = jsonio_lib.py_to_tree(read_frame, schema_type, schema_title, schema_frame,
                                                 TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))
                self.TreeView.reset()
                self.TreeView.setModel(new_tree)
                self.TreeView.expandAll()
                new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
                if new_tree:
                    config["last_schema"] = selected
                    save_config(script_dir, config)
            else:
                config["last_schema"] = selected
                save_config(script_dir, config)
                self.set_blank_from_schema()
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title = "[pyJSON.copy_schema_to_storage/ERROR]",
                message = str(err)
            )


    def copy_schema_to_storage(self):
        """
        creates an internal copy of said schema. fail-safes in not overwriting existing schemas.

        Returns:
        """
        lg.info("\n----------\nCopying schema to tool storage.\n-----------")
        try:
            #filepath = os.path.normpath(tk.filedialog.askopenfilename(
            #    filetypes=(('Java Script Object Notation', '*.json'), ('All Files', '*.*'))))
            filepath = QFileDialog.getOpenFileName(
                caption = "Select a JSON Schema for Import...",
                directory = config["last_dir"],
                filter = "Java Script Object Notation (*.json);; All Files (*.*)"
            )[0]
            if filepath == '':
                raise OSError("[pyJSON.copy_schema_to_storage/WARN]: File Selection aborted!")
            if not os.path.isfile(filepath):
                raise FileNotFoundError("[pyJSON.copy_schema_to_storage/ERROR]: Specified file does not exist.")
            if filepath == os.path.join(script_dir, "Schemas", os.path.basename(filepath)):
                tk.messagebox.showwarning(
                    title = "[pyJSON.copy_schema_to_storage/WARN]",
                    message = "[pyJSON.copy_schema_to_storage/WARN]: Source schema seems to be already in the schema " +
                            "folder. It will not be copied."
                )
            else:
                shutil.copyfile(filepath, os.path.join(script_dir, "Schemas", os.path.basename(filepath)))
            self.combobox_repopulate()
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title = "[pyJSON.copy_schema_to_storage/ERROR]",
                message = "[pyJSON.copy_schema_to_storage/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            lg.error(err)


    def save_as_function(self):
        """
        first, calls a dialog for saving a file. Then creates a dictionary from the TreeView model and writes it as
        JSON Document to the file system at the given path.

        Returns:
        """
        #selected_path = os.path.normpath(tk.filedialog.asksaveasfilename(
        #    filetypes=(('Java Script Object Notation', '*.json'), ('All Files', '*.*'))))
        selected_path = QFileDialog.getSaveFileName(
            caption = "Save as...",
            directory = config["last_dir"] + "/_meta.json",
            filter = "Java Script Object Notation (*.json);; All Files (*.*)",

        )[0]
        if selected_path == '' or selected_path == ".":
            lg.info("[pyJSON.save_curr_json/INFO]: Either file selection aborted or you have selected a very odd path.")
        else:
            if re.match(pattern=re.compile(".*\.json$"), string=selected_path) is None:
                selected_path = selected_path + ".json"
            tree = self.TreeView.model()
            json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
            try:
                with open(selected_path, "w", encoding='utf8') as out:
                    json.dump(json_frame, out, indent=4, ensure_ascii=False)
                    config["last_JSON"] = selected_path
                    save_config(script_dir, config)
                    self.curr_json_label.setText(selected_path)
                    self.callWatchdog()
            except OSError as err:
                lg.error(err)
                tk.messagebox.showerror(
                    title="[pyJSON.save_curr_json/ERROR]",
                    message="[pyJSON.save_curr_json/ERROR]: File seems to neither exist nor writable!"
                )


    def save_function(self):
        """
        Writes changes of a JSON document to the file system. Calls save_as_function(), if not saved yet.

        Returns:

        """
        if config["last_JSON"] is None:
            self.save_as_function()
        else:
            tree = self.TreeView.model()
            json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
            try:
                with open(config["last_JSON"], "w", encoding='utf8') as out:
                    json.dump(json_frame, out, indent=4, ensure_ascii=False)
            except OSError as err:
                lg.error(err)
                tk.messagebox.showerror(
                    title="[pyJSON.save_curr_json/ERROR]",
                    message="[pyJSON.save_curr_json/ERROR]: File seems to neither exist nor writable!"
                )


    def set_blank_from_schema(self):
        """
        Creates a TreeView model with empty value fields to be edited and exported as JSON document.

        Returns:
        """
        lg.info("\n----------\nGenerating Blank from Schema\n----------")
        try:
            curr_schem = jsonio_lib.decode_function(
                os.path.join(
                    script_dir,
                    "Schemas",
                    config["last_schema"]
                )
            )

            if type(curr_schem) is int and curr_schem == -999:
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.combobox_selected/ERROR]: Schema File is missing!")

            pre_json = jsonio_lib.schemaToPyGen(curr_schem)
            pre_descr = jsonio_lib.schemaToPyGen(curr_schem, mode = "descr")
            pre_title = jsonio_lib.schemaToPyGen(curr_schem, mode = "title")
            pre_type = jsonio_lib.schemaToPyGen(curr_schem, mode = "type")

            new_tree = jsonio_lib.py_to_tree(pre_json, pre_type, pre_title, pre_descr,
                                             TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())

            if new_tree:
                config["last_JSON"] = None
                save_config(script_dir, config)
                self.curr_json_label.setText("None")

        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.set_blank_from_schema/ERROR]",
                message="[pyJSON.set_blank_from_schema/ERROR]: Specified schema does not exist.\nPlease select " +
                        "another schema and repeat!"
            )
        except OSError as err:
            lg.error(err)

    # saves default values into the default folder.
    def save_default(self):
        """
        stores a copy of the current JSON on a schema basis in the "Default" directory, which can be loaded later on.

        Returns:
        """
        lg.info("\n----------\nSaving default for Schema " + config["last_schema"] + "\n----------")
        tree = self.TreeView.model()
        json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
        try:
            with open(os.path.join(script_dir, "Default", config["last_schema"]), "w", encoding='utf8') as out:
                json.dump(json_frame, out, indent=4, ensure_ascii=False)
        except OSError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.save_default/ERROR]",
                message="[pyJSON.save_default/ERROR]: File seems to neither exist nor writable!"
            )

    def load_default(self):
        """
        creates a TreeView model from the default that was stored in the tools directory structure

        Returns:
        """
        lg.info("\n----------\nLoading default for Schema " + config["last_schema"] + "\n----------")
        try:

            if not os.path.isfile(os.path.join(script_dir, "Default", config["last_schema"])):
                raise FileNotFoundError("[pyJSON.load_default/ERROR]: No default file found!")
            if not os.path.isfile(os.path.join(script_dir, "Schemas", config["last_schema"])):
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.load_default/ERROR]: Selected schema not found!")

            default_values = jsonio_lib.decode_function(os.path.join(script_dir, "Default", config["last_schema"]))

            schema_read = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
            schema_descr = jsonio_lib.schemaToPyGen(schema_read, mode = "description")
            schema_type = jsonio_lib.schemaToPyGen(schema_read, mode = "type")
            schema_title = jsonio_lib.schemaToPyGen(schema_read, mode = "title")

            new_tree = jsonio_lib.py_to_tree(default_values, schema_type, schema_title, schema_descr,
                                             TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())

            if new_tree:
                config["last_JSON"] = None
                save_config(script_dir, config)
                self.curr_json_label.setText("None")
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.load_default/ERROR]",
                message=str(err)
            )


    def reloader_function(self):
        """
        drops all changes made and reverts to the last known saved state or a blank.

        Returns:
        """
        lg.info("\n----------\nLoading default for Schema " + config["last_schema"] + "\n----------")
        if config["last_JSON"] is None:
            lg.warning("No last JSON found, defaulting to Blank.")
            self.set_blank_from_schema()
        else:
            try:
                if not config["last_JSON"] is None:
                    if not os.path.isfile(config["last_JSON"]):
                        raise FileNotFoundError("[pyJSON.reloader_function/ERROR]: Last JSON file not found!")
                    if not os.path.isfile(os.path.join(script_dir, "Schemas", config["last_schema"])):
                        self.combobox_repopulate()
                        raise FileNotFoundError("[pyJSON.reloader_function/ERROR]: Selected schema not found!")

                    values = jsonio_lib.decode_function(os.path.join(config["last_JSON"]))

                    schema_read = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
                    schema_descr = jsonio_lib.schemaToPyGen(schema_read, mode = "description")
                    schema_type = jsonio_lib.schemaToPyGen(schema_read, mode = "type")
                    schema_title = jsonio_lib.schemaToPyGen(schema_read, mode = "title")

                    new_tree = jsonio_lib.py_to_tree(values, schema_type, schema_title, schema_descr,
                                                     TreeClass(
                                                         data=["Schema Key", "Key Title", "Value", "Type", "Description"]))

                    self.TreeView.reset()
                    self.TreeView.setModel(new_tree)
                    self.TreeView.expandAll()
                    new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
                else:
                    self.set_blank_from_schema()

            except FileNotFoundError as err:
                lg.error(err)
                tk.messagebox.showerror(
                    title="[pyJSON.load_default/ERROR]",
                    message=str(err)
                )

    def validate_Function(self):
        """
        converts the tree keys and values to JSON and validates the JSON document agains the selected schema

        Returns:
        """
        tree = self.TreeView.model()
        curr_json_py = jsonio_lib.tree_to_py(tree.root_node.childItems)
        curr_json = json.dumps(curr_json_py)
        result = jsonio_lib.validator_vars(curr_json, os.path.join(script_dir, "Schemas", config["last_schema"]))
        match result:
            case 0:
                tk.messagebox.showinfo(
                    title="[pyJSON.validate_Function/INFO]",
                    message="The JSON is valid against the schema!"
                )
            case 1:
                tk.messagebox.showerror(
                    title="[pyJSON.validate_Function/ERROR]",
                    message="The JSON is not valid against the schema!"
                )
            case 2:
                tk.messagebox.showerror(
                    title="[pyJSON.validate_Function/ERROR]",
                    message="The schema is not valid against its meta schema!"
                )
            case -999:
                tk.messagebox.showerror(
                    title="[pyJSON.validate_Function/ERROR]",
                    message="The schema is not accessible!"
                )

    # SEARCH RELATED FUNCTIONS


    def search_Dirs(self):
        """
        initialises the search and instances and/or opens the widget containing the search results

        Returns:
        """
        if self.searchList is None:
            self.searchList = SearchWindow()

        if not self.searchList.isVisible():
            # get geometries
            mainCurrW = self.geometry().width()
            mainCurrH = self.geometry().height()
            mainCurrX = self.geometry().x()
            mainCurrY = self.geometry().y()
            currScreen = QGuiApplication.screenAt(QPoint(mainCurrX, mainCurrY))
            desktopW = currScreen.availableGeometry().width()

            # multi desktop setups handling
            if desktopW < mainCurrX:
                desktopW += QGuiApplication.screenAt(QPoint(1, 1)).availableGeometry().width()
            if mainCurrX + mainCurrW + 315 > desktopW:
                offsetX = mainCurrX + mainCurrW - 315
            else:
                offsetX = mainCurrX + mainCurrW + 15

            # call the window
            self.searchList.setGeometry(offsetX, mainCurrY, 300, mainCurrH)
            self.searchList.show()
        if self.curr_dir_comboBox.currentText() != "  (none)":
            path = self.curr_dir_comboBox.currentText()
            currSchem = self.curr_schem_ddm.currentText()
            if index_dict[path] and os.path.exists(path):
                indexJsonFile = os.path.join(script_dir, "Indexes", "index" + str(index_dict[path]) + ".json")
                fileIndex = json.load(open(indexJsonFile, encoding = "utf8"))
                lg.info("[pyJSON.search_Dirs/INFO]: Retrieved index of " + path + ".")
                resultIndex = jsonsearch_lib.schemaMatchingSearch(fileIndex["files"], currSchem, script_dir)
                tree = self.TreeView.model()
                jsonFrame = jsonio_lib.tree_to_py(tree.root_node.childItems)
                flattenedFrame = {}
                flattenedFrame = jsonsearch_lib.dictFlattenDict(jsonFrame, flattenedFrame)
                for i in list(flattenedFrame.keys()):
                    if flattenedFrame[i] == "":
                        del flattenedFrame[i]
                if len(flattenedFrame) > 0:
                    resultIndex = jsonsearch_lib.fSearch(resultIndex, flattenedFrame)
                if len(resultIndex) != 0:
                    resultModel = QStandardItemModel()
                    for i in resultIndex:
                        item = QStandardItem(i)
                        resultModel.appendRow(item)
                        self.searchList.searchListView.setModel(resultModel)
                else:
                    lg.warning("[pyJSON.search_Dirs/WARN]: No results found!")
                    tk.messagebox.showwarning(
                        title = "[pyJSON.search_Dirs/WARN]",
                        message = "No results found!"
                    )
        else:
            lg.warning("[pyJSON.search_Dirs/WARN]: No directory for search selected!")
            tk.messagebox.showwarning(
                title = "[pyJSON.search_Dirs/WARN]",
                message = "No directory for search selected!"
            )

    def callWatchdog(self):
        """
        function responsible for executing the re-indexing on a regular basis
        Returns:

        """
        tk.messagebox.showinfo(
            title = "[pyJSON.callWatchdog/INFO]",
            message = "Checking and updating indexes, if applicable."
        )
        jsonsearch_lib.watchdog(script_dir, index_dict)


    def closeEvent(self, event):
        """
        a specific handler receiving QCloseEvents of the main window in order
        to not only closing it, but all windows of the app.

        Args:
            event (QCloseEvent): the close event to be processed

        Returns:

        """
        if self.searchList:
            self.searchList.close()

class BackgroundBrushDelegate(QStyledItemDelegate):
    """
    Another QStyledItemDelegate inheriting class for coloring the not-to-be-edited columns
    """
    def __init__(self, brush: QBrush, parent):
        """
        Constructor
        Args:
            brush (QBrush): a brush containing specific parameters, like colors.
            parent (object): the Parent Object.
        """
        super(BackgroundBrushDelegate, self).__init__()
        self.brush = brush

    def initStyleOption(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        """
        sets the color to the cells the delegate is assigned to

        Args:
            option (QStyleOptionViewItem):  passes other options
            index (QModelIndex): the QModelIndex to be modified

        Returns:
        """
        super(BackgroundBrushDelegate, self).initStyleOption(option, index)
        option.backgroundBrush = self.brush


# ----------------------------------------
# Execution
# ----------------------------------------


if __name__ == "__main__":
    import sys

    now = datetime.now()
    multiprocessing.freeze_support()  # needed function for the subprocess crawler

    # set Script Directory
    script_dir = os.getcwd()

    # running Tkinter modules to make my life easier
    tk_root = tk.Tk()
    tk_root.withdraw()

    # initialize the QtWidget
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiRunnerInstance()

    # check and create or load the config of the tool
    if not os.path.isfile(os.path.join(script_dir, "pyJSON_conf.json")):
        lg.info("[pyJSON.main/INFO]: Config is missing. Creating one for you.")
        deploy_config(script_dir)
    config = json.load(open(os.path.join(script_dir, "pyJSON_conf.json"), encoding = "utf8"), cls=json.JSONDecoder)

    # initialize logging
    lg = logging.getLogger()
    lg.setLevel("DEBUG")
    formatter = logging.Formatter(fmt=u'%(asctime)s: %(message)s')

    # If logging is set to be in file, checkups have to be done
    if config["verbose_logging"]:
        if not os.path.isdir(os.path.join(script_dir, "Logs")):
            print("[pyJSON.main/INFO]: Logs Directory is missing! Creating...")
            try:
                os.makedirs(os.path.join(script_dir, "Logs"), exist_ok=True)
            except OSError as err:
                print(err)
                str_message = "[pyJSON.main/FATAL]: Cannot create directory. Please check permissions!"
                tk.messagebox.showerror("[pyJSON.main/FATAL]", str_message)

        print(os.path.join(os.getcwd(), "Logs", (now.strftime('%Y%m%d_%H_%M_%S') + ".log")))
        file_handler = logging.FileHandler(
            os.path.join(os.getcwd(), "Logs", (now.strftime('%Y%m%d_%H_%M_%S') + ".log")))
        file_handler.setFormatter(formatter)
        lg.addHandler(file_handler)

    # A stream handler for the log.

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    lg.addHandler(stream_handler)

    lg.info("            __ _____ _____ _____ ")
    lg.info(" ___ _ _ __|  |   __|     |   | |")
    lg.info("| . | | |  |  |__   |  |  | | | |")
    lg.info("|  _|_  |_____|_____|_____|_|___|")
    lg.info("|_| |___|                      ")
    lg.info("==============================")
    lg.info("The pyJSON Schema Loader and JSON Editor")
    lg.info("==============================")
    lg.info("Start time: " + str(now))
    lg.info("Operating System: " + platform.platform())
    lg.info("Python Version: " + platform.python_version())
    lg.info("Python Implementation: " + platform.python_implementation())
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        lg.info("Frozen Environment (e.g. PyInstaller) : Yes")
    else:
        lg.info("Frozen Environment (e.g. PyInstaller) : No")


    # Do some checkups.
    if not os.path.isdir(os.path.join(script_dir, "Schemas")):
        lg.info("[pyJSON.main/INFO]: Schemas Directory is missing! Creating...")
        try:
            os.makedirs(os.path.join(script_dir, "Schemas"), exist_ok=True)
        except OSError as err:
            lg.error(err)
            str_message = "[pyJSON.main/FATAL]: Cannot create directory. Please check permissions!"
            tk.messagebox.showerror("[pyJSON.main/FATAL]", str_message)
    if not os.path.isfile(os.path.join(script_dir, "Schemas/default.json")):
        lg.info("[pyJSON.main/INFO]: Default File is missing! Deploying...")
        deploy_schema(os.path.join(script_dir, "Schemas"))

    if not os.path.isdir(os.path.join(script_dir, "Default")):
        lg.info("[pyJSON.main/INFO]: Defaults Directory is missing! Creating...")
        try:
            os.makedirs(os.path.join(script_dir, "Default"), exist_ok=True)
        except OSError as err:
            lg.error(err)
            str_message = "[pyJSON.main/FATAL]: Cannot create directory. Please check permissions!"
            tk.messagebox.showerror("[pyJSON.main/FATAL]", str_message)

# Load or create and save the main index file
    index_dict = {
        "cur_index": 0
    }
    if not (os.path.isfile(os.path.join(script_dir, "Indexes/pyJSON_S_index.json"))):
        lg.warning("[pyJSON_search/WARN]: Index file is missing. Create index from scratch.")
        try:
            os.mkdir(os.path.join(script_dir, "Indexes"))
        except FileExistsError as err:
            pass
        saveMainIndex(script_dir, index_dict)
    else:
        try:
            index_dict = json.load(open(os.path.join(script_dir, "Indexes/pyJSON_S_index.json"), encoding = "utf8"), cls=json.JSONDecoder)
        except OSError as err:
            lg.error(err)
            lg.error("[pyJSON_search/ERROR]: Cannot read or access Index file. Defaulting to blank Index.")

    # setup the view for the first time
    if not os.path.isfile(os.path.join(script_dir, "Schemas", config["last_schema"])):
        lg.warning("[pyJSON.main/WARN]: Schema in config is missing. Falling back to default.")
        frame = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", "default.json"))
        config["last_schema"] = "default.json"
        save_config(script_dir, config)
    else:
        frame = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
    if config["last_JSON"] is None:
        lg.info("\n----------\nGenerating blank from schema\n----------")
        st_pre_json = jsonio_lib.schemaToPyGen(frame)
        ui.curr_json_label.setText("None")
    else:
        if os.path.isfile(config["last_JSON"]):
            st_pre_json = jsonio_lib.decode_function(config["last_JSON"])
            ui.curr_json_label.setText(os.path.normpath(config["last_JSON"]))
        else:
            lg.warning("\n----------\nJSON is missing!!\nGenerating blank from schema\n----------")
            tk.messagebox.showwarning(
                title="[pyJSON/WARN]",
                message="[pyJSON/WARN]: Last JSON not found. Defaulting to blank."
            )
            st_pre_json = jsonio_lib.schemaToPyGen(frame)
            ui.curr_json_label.setText("None")
            config["last_JSON"] = None
            save_config(script_dir, config)

    lg.info("\n----------\nGenerating reference from schema\n----------")
    st_pre_descr = jsonio_lib.schemaToPyGen(frame, mode = "description")
    st_pre_title = jsonio_lib.schemaToPyGen(frame, mode = "title")
    st_pre_type = jsonio_lib.schemaToPyGen(frame, mode = "type")
    lg.info("\n----------\nConstructing Tree, please wait.\n---------")
    model = jsonio_lib.py_to_tree(st_pre_json, st_pre_type, st_pre_title, st_pre_descr,
                                  TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))
    ui.label_curDir.setText(config["last_dir"])

    ui.TreeView.setModel(model)

    # setting the column width for each column after setting the model.
    ui.TreeView.setColumnWidth(0, 200)
    ui.TreeView.setColumnWidth(1, 150)
    ui.TreeView.setColumnWidth(2, 350)
    ui.TreeView.setColumnWidth(3, 50)
    ui.TreeView.setColumnWidth(4, 500)

    # column colors using several delegates
    delegate1 = BackgroundBrushDelegate(brush=QBrush(QColor(240, 240, 240, 255)), parent=QBrush(Qt.white))

    ui.TreeView.setItemDelegateForColumn(0, delegate1)
    ui.TreeView.setItemDelegateForColumn(1, delegate1)
    ui.TreeView.setItemDelegateForColumn(3, delegate1)
    ui.TreeView.setItemDelegateForColumn(4, delegate1)
    ui.TreeView.expandAll()

    ui.combobox_repopulate()
    ui.dirselect_repopulate()
    ui.curr_schem_ddm.blockSignals(True)
    ui.curr_schem_ddm.setCurrentText(config["last_schema"])
    ui.curr_schem_ddm.blockSignals(False)

    jsonsearch_lib.watchdog(script_dir, index_dict)

    # enter main loop
    sys.exit(app.exec_())