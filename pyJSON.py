# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Main Module
# author: N. Plathe
# ----------------------------------------
"""
This is the main module, extending on the interface and implementing functions that call on the modules.
"""
# ----------------------------------------
# pyJSONs main repo:
# https://github.com/nplathe/pyJSON-Schema-Loader-and-JSON-Editor
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
import os
import platform
import regex as re
import shutil
import subprocess
from datetime import datetime

# import PySide libraries
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QModelIndex, Qt, QPoint
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import QMainWindow, QStyledItemDelegate, QStyle, QWidget, QVBoxLayout, \
    QFileDialog, QMessageBox, QStyleOptionViewItem

# import of modules
from Modules import jsonio_lib, jsonsearch_lib
from Modules.deploy_files import deploy_schema, deploy_config, save_config, save_main_index
from Modules.ModifiedTreeModel import ModifiedTreeClass as TreeClass

# import the converted user interface
from UserInterfaces.pyJSON_interface import Ui_MainWindow
from Modules.pref_ui import ui_preferences


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

        Args:
            parent (QWidget): parent of the QWidget to be.
            option (object): option that might be passed to the constructor of the QWidget
            index (QModelIndex): the QModelIndex of the item that was clicked

        Returns:
            QWidget: the editor QWidget - a drop down menu for enumerators, a line edit (the standard) otherwise
        """

        cur_item = index.model().getItem(index)
        value_type = cur_item.get_data(3)
        cur_meta = cur_item.all_metadata()
        value_type2 = cur_item.get_metadata("type")

        if value_type2 is not None:
            lg.debug("Last Type fetched: " + value_type2)
            lg.debug("Type of item in model: " + value_type)
            if "enum" in cur_meta.keys():
                lg.debug("custom delegate editor selected...")
                dropDownEnum = QtWidgets.QComboBox(parent)
                dropDownEnum.setFrame(False)
                dropDownEnum.addItem("(none)")
                for i in cur_meta["enum"]:
                    dropDownEnum.addItem(i)
                return dropDownEnum
            else:
                widget = QStyledItemDelegate.createEditor(QStyledItemDelegate(), parent, option, index)
                return widget
        else:
            widget = QStyledItemDelegate.createEditor(QStyledItemDelegate(), parent, option, index)
            return widget

    def setEditorData(self, editor, index):
        """
        Passes the data from the model to the editor

        Args:
            editor (QWidget): the QWidget for which the data needs to be set
            index (QModelIndex): the index of the item to be edited
        """
        if isinstance(editor, QtWidgets.QComboBox):
            item = index.model().getItem(index)
            value = item.get_data_array()[2]
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
        """
        if isinstance(editor, QtWidgets.QComboBox): # handle combobox data
            value = editor.currentText()
            if value == "(none)":
                model.setData(index, "", Qt.EditRole)
            else:
                model.setData(index, value, Qt.EditRole)
        else: # handle arrays and everything else

            # array value insertion
            if model.getItem(index).get_data(3) == 'array':
                if editor.text() != '':
                    model.beginInsertRows(index, index.row(), index.row() + 1)
                    lg.info("[pyJSON.EnumDropDownDelegate.setModelData/INFO]: Detected an entry for an array."
                            + " Inserting the entry as a child node...")
                    model.add_node(parent = model.getItem(index), data = ["", "", editor.text(), "string", "Array Item"])
                    model.endInsertRows()
                    ui.TreeView.expandAll()  #todo: move this out and split delegate into own file
                else:
                    lg.info("[pyJSON.EnumDropDownDelegate.setModelData/INFO]: Will not add a node since text is empty.")

            # array value removal
            elif (editor.text() == '' and
                    model.getItem(index).get_parent().get_data(3) == 'array' and
                    model.getItem(index).get_data(3) != 'object'):
                lg.info("[pyJSON.EnumDropDownDelegate.setModelData/INFO]: Detected an empty entry of an array."
                        + " Removing node from TreeView...")
                model.beginRemoveRows(index, index.row(), index.row() + 1)
                model.removeRows(index.row(), 1, index.parent())
                model.endRemoveRows()

            # editing objects mess with the structure...
            elif model.getItem(index).get_data(3) == 'object':
                lg.info("[pyJSON.EnumDropDownDelegate.setModelData/INFO]: Tried to edit an object."
                        + " Ommiting input.")
                pass # so we just don't touch it.

            else: # pass everything else to the standard delegate function
                QStyledItemDelegate.setModelData(QStyledItemDelegate(), editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        """
        updates the QWidget, e.g. when the size of the window changes

        Args:
            editor (QWidget): the QWidget which needs to get updated
            option (Object): option that needs to be passed to setGeometry
            index (QModelIndex): the index of the item the editor is located at
        """
        QStyledItemDelegate.updateEditorGeometry(QStyledItemDelegate(), editor, option, index)

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

    def initStyleOption(self, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        """
        sets the color to the cells the delegate is assigned to

        Args:
            option (QStyleOptionViewItem):  passes other options
            index (QModelIndex): the QModelIndex to be modified
        """
        super(BackgroundBrushDelegate, self).initStyleOption(option, index)
        option.backgroundBrush = self.brush

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
        self.searchListView.customContextMenuRequested.connect(self.on_custom_context_menu)

        # Add Widgets to layout
        layout.addWidget(self.searchListView)

    def on_custom_context_menu(self, index):
        """
        Custom context Menu

        Args:
            index (QPoint): The QPoint the right click was executed at.
        """
        list_index = self.searchListView.indexAt(index)
        if list_index.isValid():
            item_menu = QtWidgets.QMenu("Item menu")
            entry1 = item_menu.addAction("Open in pyJSON...")
            entry1.triggered.connect(self.open_in_pyjson)
            entry2 = item_menu.addAction("Open in Editor...")
            entry2.triggered.connect(self.open_file)
            entry3 = item_menu.addAction("Open File Location...")
            entry3.triggered.connect(self.open_file_location)
            item_menu.exec(self.searchListView.viewport().mapToGlobal(index))

    def open_in_pyjson(self):
        """
        A function for opening a JSON in the pyJSON window itself
        """
        index = self.searchListView.selectedIndexes()[0]
        item = self.searchListView.model().itemFromIndex(index)
        if ui:
            ui.jsonopener(filepath_str = item.text())

    def open_file(self):
        """
        A function to initialise opening the selected path in the ListView with the associated tool. Conveniently enough
        with Windows, explorer.exe passes the attempt of opening a file to the app for us.
        """
        index = self.searchListView.selectedIndexes()[0]
        item = self.searchListView.model().itemFromIndex(index)
        if platform.system() == "Windows":
            subprocess.Popen('explorer '+item.text())

    def open_file_location(self):
        """
        Opens the path to the file.
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
    def __init__(self, config = None, script_dir = "", index_dict = None):
        """
        Constructor. Sets up all signals and slots, decorates the buttons, creates status tips, links the deleagte to
        the 2nd column, etc...

        Args:
            config (dict): handover config from loading before entering the loop.
            script_dir (str): the script directory.
            index_dict: handover index_dict from loading.
        """
        # we first call init from the super class, then load the translated py file file from designer
        super(UiRunnerInstance, self).__init__()
        self.setupUi(self)

        # init dicts and script_dir variable
        if config is None:
            self.config = {
                "last_dir": os.getcwd(),
                "last_schema": "default.json",
                "last_JSON": None,
                "verbose_logging": False,
                "show_error_representation": True
            }
        else:
            self.config = config

        if script_dir is None:
            self.script_dir = os.getcwd()
        else:
            self.script_dir = script_dir

        if index_dict is None:
            self.index_dict = {
                "cur_index": 0
            }
        else:
            self.index_dict = index_dict

        # window decoration
        title = "pyJSON Schema Loader and JSON Editor"
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("./icon.ico"))

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

        self.pushButton_search.clicked.connect(self.search_dirs)
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
        self.actionValidate_input_against_selected_schema.triggered.connect(self.validate_function)

        # Index related functions in the menu bar
        self.actionCheck_indexes.triggered.connect(self.call_watchdog)

        # other menu bar entries
        self.actionPreferences.triggered.connect(self.call_prefdiag)

        # Drop-Down Menu
        self.current_schema_combo_box.currentTextChanged.connect(self.combobox_selected)

        self.searchList = None
        self.prefdiag = None

        # set the delegate for the view
        self.delegate = EnumDropDownDelegate()
        self.TreeView.setItemDelegateForColumn(2, self.delegate)

        # right click context menu
        self.TreeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TreeView.customContextMenuRequested.connect(self.on_custom_context_menu)

        # load data from the config, if present.
        if config["last_JSON"] is not None:
            self.jsonopener(filepath_str = config["last_JSON"])
        else:
            self.set_blank_from_schema()

        # setting the column width for each column after setting the model.
        self.TreeView.setColumnWidth(0, 200)
        self.TreeView.setColumnWidth(1, 150)
        self.TreeView.setColumnWidth(2, 350)
        self.TreeView.setColumnWidth(3, 50)
        self.TreeView.setColumnWidth(4, 500)

        # column colors using several delegates
        delegate1 = BackgroundBrushDelegate(brush = QBrush(QColor(240, 240, 240, 255)), parent = QBrush(Qt.white))

        self.TreeView.setItemDelegateForColumn(0, delegate1)
        self.TreeView.setItemDelegateForColumn(1, delegate1)
        self.TreeView.setItemDelegateForColumn(3, delegate1)
        self.TreeView.setItemDelegateForColumn(4, delegate1)
        self.TreeView.expandAll()

        self.combobox_repopulate()
        self.dirselect_repopulate()
        self.current_schema_combo_box.blockSignals(True)
        self.current_schema_combo_box.setCurrentText(self.config["last_schema"])
        self.current_schema_combo_box.blockSignals(False)

        # call the show function
        self.show()

    def on_custom_context_menu(self, index):  #todo: either fill this with life or throw it out!
        """
        Custom context menu for the tree view widget.

        Args:
            index (QPoint): The QPoint the right click was executed at.
        """
        list_index = self.TreeView.indexAt(index)
        if list_index.isValid():
            item_type = self.TreeView.model().getItem(list_index).get_data(3)
            item_menu = QtWidgets.QMenu("Item menu")
            entry1 = item_menu.addAction("Remove this node...")
            if item_type == 'array':
                entry2 = item_menu.addAction("Add entries to this array...")
            item_menu.exec(self.TreeView.viewport().mapToGlobal(index))


    def diropener(self): # Button Function Definitions
        """
        lets the user open a directory to be indexed.
        """
        dir_path = os.path.normpath(
            QFileDialog.getExistingDirectory(
                caption = "Select Directory for indexing",
                dir = self.config["last_dir"]
            )
        )
        try:
            os.chdir(dir_path)
            if dir_path == '' or dir_path == '.':
                raise OSError("[pyJSON.diropener/WARN]: Directory selection aborted!")
            config["last_dir"] = dir_path
            save_config(self.script_dir, self.config)
            jsonsearch_lib.start_index(self.script_dir, dir_path, self.index_dict)
        except (FileNotFoundError, OSError) as err:
            lg.error(err)
            if isinstance(err, FileNotFoundError):
                QMessageBox.critical(
                    self,
                    "[pyJSON.diropener/ERROR]",
                    "Directory does not exist."
                )
        self.dirselect_repopulate()


    def jsonopener(self, filepath_str = None): # Definition Actions MenuBar
        """
        Reads a JSON document, prepares the model for the TreeView widget and attaches it to said view.

        Args:
            filepath_str(str): If set, the path to use gets overwritten and QFileDialog is not called
        """
        try:
            if not filepath_str:
                filepath_str = QFileDialog.getOpenFileName(
                    caption = "Open a JSON Document...",
                    dir = self.config["last_dir"],
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
            schema_read = jsonio_lib.decode_function(os.path.join(self.script_dir, "Schemas", self.config["last_schema"]))
            schema_meta = jsonio_lib.schema_to_py_gen(schema_read, mode = "meta")
            new_tree = jsonio_lib.py_to_tree(read_frame, schema_meta,
                                             TreeClass(data=["JSON Structure", "Title", "Value", "Type", "Description"]),
                                             self.config["show_error_representation"])
            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
            if new_tree:
                self.config["last_JSON"] = filepath
                save_config(self.script_dir, self.config)
                self.curr_json_label.setText(filepath)

        except (FileNotFoundError, OSError) as err:
            lg.error(err)
            if isinstance(err, FileNotFoundError):
                QMessageBox.warning(
                    self,
                    "[pyJSON.jsonopener/ERROR]",
                    "[pyJSON.jsonopener/ERROR]: Specified file does not exist.",
                )


    def combobox_repopulate(self):
        """
        sets up the QComboBox for schemas and updates its entries, if a schema gets added.
        """
        self.current_schema_combo_box.blockSignals(True)
        if self.current_schema_combo_box.count != 0:
            self.current_schema_combo_box.clear()
        schema_list = os.listdir(os.path.join(self.script_dir, "Schemas"))
        for x in schema_list:
            self.current_schema_combo_box.addItem(x)
        self.current_schema_combo_box.update()
        self.current_schema_combo_box.blockSignals(False)


    def dirselect_repopulate(self):
        """
        Sets up the other QCombobox utilised for the indexed directories and updates its entries accordingly.
        """
        selection_list = list(self.index_dict.keys())
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
        if self.config["last_dir"] is not None:
            self.curr_dir_comboBox.setCurrentText(self.config["last_dir"])
        else:
            self.curr_dir_comboBox.setCurrentText("  (none)")
        self.curr_dir_comboBox.blockSignals(False)


    def combobox_selected(self):
        """
        A slot that gets triggered when the QComboBox emits a changed-Signal. Sets the new schema and reconstructs
        the model for the TreeView
        """
        lg.info("\n----------\nswapped schema!\n----------")
        selected = self.current_schema_combo_box.currentText()
        try:
            schema = jsonio_lib.decode_function(os.path.join(self.script_dir, "Schemas", selected))
            if type(schema) is int and schema == -999:
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.combobox_selected/ERROR]: Schema File is missing!")
            schema_meta = jsonio_lib.schema_to_py_gen(schema, mode = "meta")

            if not self.config["last_JSON"] is None:
                read_frame = jsonio_lib.decode_function(self.config["last_JSON"])
                new_tree = jsonio_lib.py_to_tree(read_frame, schema_meta,
                                                 TreeClass(data=["JSON Structure", "Title", "Value", "Type", "Description"]),
                                                 self.config["show_error_representation"])
                self.TreeView.reset()
                self.TreeView.setModel(new_tree)
                self.TreeView.expandAll()
                new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
                if new_tree:
                    self.config["last_schema"] = selected
                    save_config(self.script_dir, self.config)
            else:
                self.config["last_schema"] = selected
                save_config(self.script_dir, self.config)
                self.set_blank_from_schema()
        except FileNotFoundError as err:
            lg.error(err)
            QMessageBox.critical(
                self,
                "[pyJSON.copy_schema_to_storage/ERROR]",
                str(err)
            )


    def copy_schema_to_storage(self):
        """
        creates an internal copy of said schema. Fail-safes in not overwriting existing schemas.
        """
        lg.info("\n----------\nCopy function - schema to tool storage\n-----------")
        try:
            filepath = QFileDialog.getOpenFileName(
                caption = "Select a JSON Schema for Import...",
                dir = self.config["last_dir"],
                filter = "Java Script Object Notation (*.json);; All Files (*.*)"
            )[0]
            if filepath == '':
                raise OSError("[pyJSON.copy_schema_to_storage/WARN]: File Selection aborted!")
            if not os.path.isfile(filepath):
                raise FileNotFoundError("[pyJSON.copy_schema_to_storage/ERROR]: Specified file does not exist.")
            if filepath == os.path.join(self.script_dir, "Schemas", os.path.basename(filepath)):
                QMessageBox.warning(
                    self,
                    "[pyJSON.copy_schema_to_storage/WARN]",
                    "Source schema seems to be already in the schema  folder. It will not be copied."
                )
            else:
                shutil.copyfile(filepath, os.path.join(self.script_dir, "Schemas", os.path.basename(filepath)))
            self.combobox_repopulate()
        except (FileNotFoundError, OSError) as err:
            lg.error(err)
            if isinstance(err, FileNotFoundError):
                QMessageBox.critical(
                    self,
                    "[pyJSON.copy_schema_to_storage/ERROR]",
                    "Specified file does not exist."
                )


    def save_as_function(self):
        """
        first, calls a dialog for saving a file, then creates a dictionary from the TreeView model and writes it as
        JSON Document to the file system at the given path.
        """
        selected_path = QFileDialog.getSaveFileName(
            caption = "Save as...",
            dir = self.config["last_dir"] + "/_meta.json",
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
                    self.config["last_JSON"] = selected_path
                    save_config(self.script_dir, self.config)
                    self.curr_json_label.setText(selected_path)
                    self.call_watchdog()
            except OSError as err:
                lg.error(err)
                QMessageBox.critical(
                    self,
                    "[pyJSON.save_curr_json/ERROR]",
                    "File seems to neither exist nor writable!"
                )


    def save_function(self):
        """
        Writes changes of a JSON document to the file system. Calls save_as_function(), if not saved yet.
        """
        if self.config["last_JSON"] is None:
            self.save_as_function()
        else:
            tree = self.TreeView.model()
            json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
            try:
                with open(self.config["last_JSON"], "w", encoding='utf8') as out:
                    json.dump(json_frame, out, indent=4, ensure_ascii=False)
            except OSError as err:
                lg.error(err)
                QMessageBox.critical(
                    self,
                    "[pyJSON.save_curr_json/ERROR]",
                    "File seems to neither exist nor writable!"
                )


    def set_blank_from_schema(self):
        """
        Creates a TreeView model with empty value fields to be edited and exported as JSON document.
        """
        lg.info("\n----------\nGenerating Blank from Schema\n----------")
        try:
            curr_schem = jsonio_lib.decode_function(
                os.path.join(
                    self.script_dir,
                    "Schemas",
                    self.config["last_schema"]
                )
            )

            if type(curr_schem) is int and curr_schem == -999:
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.combobox_selected/ERROR]: Schema File is missing!")

            pre_json = jsonio_lib.schema_to_py_gen(curr_schem)
            pre_meta = jsonio_lib.schema_to_py_gen(curr_schem, mode = "meta")
            new_tree = jsonio_lib.py_to_tree(pre_json, pre_meta,
                                             TreeClass(data=["JSON Structure", "Title", "Value", "Type", "Description"]),
                                             self.config["show_error_representation"])

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())

            if new_tree:
                self.config["last_JSON"] = None
                save_config(self.script_dir, self.config)
                self.curr_json_label.setText("None")

        except (FileNotFoundError, OSError) as err:
            lg.error(err)
            if isinstance(err, FileNotFoundError):
                QMessageBox.critical(
                    self,
                    "[pyJSON.set_blank_from_schema/ERROR]",
                    "Specified schema does not exist.\nPlease select another schema and repeat!"
                )

    # saves default values into the default folder.
    def save_default(self):
        """
        stores a copy of the current JSON on a schema basis in the "Default" directory, which can be loaded later on.
        """
        lg.info("\n----------\nSaving default for Schema " + self.config["last_schema"] + "\n----------")
        tree = self.TreeView.model()
        json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
        try:
            with open(os.path.join(self.script_dir, "Default", self.config["last_schema"]), "w", encoding='utf8') as out:
                json.dump(json_frame, out, indent=4, ensure_ascii=False)
        except OSError as err:
            lg.error(err)
            QMessageBox.critical(
                self,
                "[pyJSON.save_default/ERROR]",
                "File seems to neither exist nor writable!"
            )

    def load_default(self):
        """
        creates a TreeView model from the default that was stored in the tools directory structure
        """
        lg.info("\n----------\nLoading default for Schema " + self.config["last_schema"] + "\n----------")
        try:

            if not os.path.isfile(os.path.join(self.script_dir, "Default", self.config["last_schema"])):
                raise FileNotFoundError("[pyJSON.load_default/ERROR]: No default file found!")
            if not os.path.isfile(os.path.join(self.script_dir, "Schemas", self.config["last_schema"])):
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.load_default/ERROR]: Selected schema not found!")

            default_values = jsonio_lib.decode_function(os.path.join(self.script_dir, "Default", self.config["last_schema"]))

            schema_read = jsonio_lib.decode_function(os.path.join(self.script_dir, "Schemas", self.config["last_schema"]))
            schema_meta = jsonio_lib.schema_to_py_gen(schema_read, mode = "meta")
            new_tree = jsonio_lib.py_to_tree(default_values, schema_meta,
                                             TreeClass(data=["JSON Structure", "Title", "Value", "Type", "Description"]),
                                             self.config["show_error_representation"])

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())

            if new_tree:
                self.config["last_JSON"] = None
                save_config(self.script_dir, self.config)
                self.curr_json_label.setText("None")
        except FileNotFoundError as err:
            lg.error(err)
            QMessageBox.critical(
                self,
                "[pyJSON.load_default/ERROR]",
                str(err)
            )


    def reloader_function(self):
        """
        drops all changes made and reverts to the last known saved state or a blank.
        """
        lg.info("\n----------\nLoading default for Schema " + self.config["last_schema"] + "\n----------")
        if self.config["last_JSON"] is None:
            lg.warning("No last JSON found, defaulting to Blank.")
            self.set_blank_from_schema()
        else:
            try:
                if not self.config["last_JSON"] is None:
                    if not os.path.isfile(self.config["last_JSON"]):
                        raise FileNotFoundError("[pyJSON.reloader_function/ERROR]: Last JSON file not found!")
                    if not os.path.isfile(os.path.join(self.script_dir, "Schemas", self.config["last_schema"])):
                        self.combobox_repopulate()
                        raise FileNotFoundError("[pyJSON.reloader_function/ERROR]: Selected schema not found!")

                    values = jsonio_lib.decode_function(os.path.join(self.config["last_JSON"]))

                    schema_read = jsonio_lib.decode_function(os.path.join(self.script_dir, "Schemas", self.config["last_schema"]))
                    schema_meta = jsonio_lib.schema_to_py_gen(schema_read, mode = "meta")

                    new_tree = jsonio_lib.py_to_tree(values, schema_meta,
                        TreeClass(data=["JSON Structure", "Title", "Value", "Type", "Description"]),
                        self.config["show_error_representation"])

                    self.TreeView.reset()
                    self.TreeView.setModel(new_tree)
                    self.TreeView.expandAll()
                    new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
                else:
                    self.set_blank_from_schema()

            except FileNotFoundError as err:
                lg.error(err)
                QMessageBox.critical(
                    self,
                    "[pyJSON.load_default/ERROR]",
                    str(err)
                )

    def validate_function(self):
        """
        converts the tree keys and values to JSON and validates the JSON document agains the selected schema
        """
        tree = self.TreeView.model()
        curr_json_py = jsonio_lib.tree_to_py(tree.root_node.childItems)
        curr_json = json.dumps(curr_json_py)
        result = jsonio_lib.validator_vars(curr_json, os.path.join(self.script_dir, "Schemas", self.config["last_schema"]))
        match result:
            case 0:
                QMessageBox.information(
                    self,
                    "[pyJSON.validate_function/INFO]",
                    "The JSON is valid against the schema!"
                )
            case 1:
                QMessageBox.warning(
                    self,
                    "[pyJSON.validate_Function/ERROR]",
                    "The JSON is not valid against the schema!"
                )
            case 2:
                QMessageBox.warning(
                    self,
                    "[pyJSON.validate_Function/ERROR]",
                    "The schema is not valid against its meta schema!"
                )
            case -999:
                QMessageBox.critical(
                    self,
                    "[pyJSON.validate_Function/ERROR]",
                    "The schema is not accessible!"
                )

    # SEARCH RELATED FUNCTIONS


    def search_dirs(self):
        """
        initialises the search and instances and/or opens the widget containing the search results

        Returns:
        """
        if self.searchList is None:
            self.searchList = SearchWindow()

        if not self.searchList.isVisible():
            # get geometries
            main_curr_w = self.geometry().width()
            main_curr_h = self.geometry().height()
            main_curr_x = self.geometry().x()
            main_curr_y = self.geometry().y()
            curr_screen = QGuiApplication.screenAt(QPoint(main_curr_x, main_curr_y))
            desktop_w = curr_screen.availableGeometry().width()

            # multi desktop setups handling
            if desktop_w < main_curr_x:
                desktop_w += QGuiApplication.screenAt(QPoint(1, 1)).availableGeometry().width()
            if main_curr_x + main_curr_w + 315 > desktop_w:
                offsetX = main_curr_x + main_curr_w - 315
            else:
                offsetX = main_curr_x + main_curr_w + 15

            # call the window
            self.searchList.setGeometry(offsetX, main_curr_y, 300, main_curr_h)
            self.searchList.show()
        if self.curr_dir_comboBox.currentText() != "  (none)":
            path = self.curr_dir_comboBox.currentText()
            curr_schem = self.current_schema_combo_box.currentText()
            if self.index_dict[path] and os.path.exists(path):
                index_json_file = os.path.join(self.script_dir, "Indexes", "index" + str(self.index_dict[path]) + ".json")
                file_index = json.load(open(index_json_file, encoding = "utf8"))
                lg.info("[pyJSON.search_Dirs/INFO]: Retrieved index of " + path + ".")
                result_index = jsonsearch_lib.schema_matching_search(file_index["files"], curr_schem, self.script_dir)
                tree = self.TreeView.model()
                json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
                flattened_frame = {}
                flattened_frame = jsonsearch_lib.dict_flatten_dict(json_frame, flattened_frame)
                for i in list(flattened_frame.keys()):
                    if flattened_frame[i] == "":
                        del flattened_frame[i]
                if len(flattened_frame) > 0:
                    result_index = jsonsearch_lib.f_search(result_index, flattened_frame)
                if len(result_index) != 0:
                    result_model = QStandardItemModel()
                    for i in result_index:
                        item = QStandardItem(i)
                        result_model.appendRow(item)
                        self.searchList.searchListView.setModel(result_model)
                        self.searchList.searchListView.activateWindow() # set focus on this widget
                else:
                    lg.warning("[pyJSON.search_Dirs/WARN]: No results found!")
                    QMessageBox.warning(
                        self,
                        "[pyJSON.search_Dirs/WARN]",
                        "No results found! Search result list is not updated."
                    )
        else:
            lg.warning("[pyJSON.search_Dirs/WARN]: No directory for search selected!")
            QMessageBox.warning(
                self,
                "[pyJSON.search_Dirs/WARN]",
                "No directory for search selected!"
            )

    def call_watchdog(self):
        """
        function responsible for executing the re-indexing on a regular basis
        """
        jsonsearch_lib.watchdog(self.script_dir, self.index_dict)
        if self.sender() and isinstance(self.sender(), QtGui.QAction):
            QMessageBox.information(
                self,
                "[pyJSON.call_watchdog/INFO]",
                "Checked indexed directories and reindexed, if needed."
            )


    def call_prefdiag(self):
        if self.prefdiag is None:
            self.prefdiag = ui_preferences(self.script_dir)
        else:
            self.prefdiag.config = self.config.copy()
        self.prefdiag.exec()
        self.config = json.load(open(os.path.join(self.script_dir, "pyJSON_conf.json"), encoding = "utf8"),
                  cls = json.JSONDecoder)


    def closeEvent(self, event):
        """
        a specific handler receiving QCloseEvents of the main window in order
        to not only closing it, but all windows of the app.

        Args:
            event (QCloseEvent): the close event to be processed
        """
        if self.searchList:
            self.searchList.close()


# ----------------------------------------
# Execution
# ----------------------------------------


if __name__ == "__main__":
    import sys
    import argparse
    import inspect

    # initialize the QtWidget
    app = QtWidgets.QApplication(sys.argv)

    # parser arguments
    parser = argparse.ArgumentParser(
        description = "pyJSON Schema Loader and JSON Editor - a tool for editing and generating JSON files utilizing " +
                      "JSON Schema.\n Use the command-line interface to automate interaction with pyJSON. " +
                      "You can provide a schema (based on file name), a JSON file and a directory to use. " +
                      "Note that erroneous CLI input gets omitted."
    )
    parser.add_argument('-d', '--directory',
                        dest = "path",
                        help = "This parameter overwrites the last used directory, if present.")
    parser.add_argument('-f', '--file',
                        dest = "file",
                        help = "Try to open the provided JSON file, if present.")
    parser.add_argument('-s', '--schema',
                        dest = "schema",
                        help = "Try to load the selected schema (filename without \".json\" suffix). " +
                               "Overwrites last used schema, if schema is present in the tool storage.")
    parser.add_argument('-ewd', '--enforce-working-directory',
                        dest = "working_dir",
                        help = "Enforces the location of the working directory to be set to the provided value.")
    args = parser.parse_args()

    # set Script Directory
    invoked_from = os.getcwd()  # relevant if python is called from a direcotry that is not the repo dir
    if args.working_dir and os.path.isdir(os.path.realpath(args.working_dir)):
        script_dir = os.path.abspath(args.working_dir)
    else:
        os.chdir(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        script_dir = os.getcwd()

    # initialize logging
    now = datetime.now()
    lg = logging.getLogger()
    lg.setLevel("DEBUG")
    formatter = logging.Formatter(fmt = u'%(asctime)s: %(message)s')

    # A stream handler for the log. Goes first for occasional messages, especially for the first run.
    stream_handler = logging.StreamHandler(stream = sys.stdout)
    stream_handler.setFormatter(formatter)
    lg.addHandler(stream_handler)

    # check and create or load the config of the tool
    if not os.path.isfile(os.path.join(script_dir, "pyJSON_conf.json")):
        deploy_config(script_dir)
        config = json.load(open(os.path.join(script_dir, "pyJSON_conf.json"), encoding = "utf8"),
                           cls = json.JSONDecoder)
        if QMessageBox.question(
            QWidget(),
            "[pyJSON.main]",
            "It seems like pyJSON is started for the first time. Do you want to enable logging to a file?"
        ):
            config["verbose_logging"] = True
            save_config(script_dir, config)
    else:
        config = json.load(open(os.path.join(script_dir, "pyJSON_conf.json"), encoding = "utf8"), cls = json.JSONDecoder)

    # If logging is set to be in file, checkups have to be done
    if config["verbose_logging"]:
        if not os.path.isdir(os.path.join(script_dir, "Logs")):
            lg.info("[pyJSON.main/INFO]: Logs Directory is missing! Creating...")
            try:
                os.makedirs(os.path.join(script_dir, "Logs"), exist_ok = True)
            except OSError as err:
                print(err)
                str_message = "[pyJSON.main/FATAL]: Cannot create directory. Please check permissions!"
                QMessageBox.critical(
                    QWidget(),
                    "[pyJSON.main/FATAL]",
                    str_message
                )

        print(os.path.join(os.getcwd(), "Logs", (now.strftime('%Y%m%d_%H_%M_%S') + ".log")))
        file_handler = logging.FileHandler(
            os.path.join(os.getcwd(), "Logs", (now.strftime('%Y%m%d_%H_%M_%S') + ".log")))
        file_handler.setFormatter(formatter)
        lg.addHandler(file_handler)

    # init proper file logging
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
    lg.info("==============================")
    lg.info("Python Version: " + platform.python_version())
    lg.info("Python Implementation: " + platform.python_implementation())
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        lg.info("Frozen Environment (e.g. PyInstaller) : Yes")
    else:
        lg.info("Frozen Environment (e.g. PyInstaller) : No")
    lg.info("==============================")
    lg.info("Invoked from: " + invoked_from)
    lg.info("Current working directory: " + script_dir)
    lg.info("Script directory: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    lg.info("==============================")

    # Do some checkups on the directory structure.
    if not os.path.isdir(os.path.join(script_dir, "Schemas")):
        lg.info("[pyJSON.main/INFO]: Schemas Directory is missing! Creating...")
        try:
            os.makedirs(os.path.join(script_dir, "Schemas"), exist_ok = True)
        except OSError as err:
            lg.error(err)
            str_message = "[pyJSON.main/FATAL]: Cannot create directory. Please check permissions!"
            QMessageBox.critical(
                QWidget(),
                "[pyJSON.main/FATAL]",
                str_message
            )
            sys.exit(1)
    if not os.path.isfile(os.path.join(script_dir, "Schemas/default.json")):
        lg.info("[pyJSON.main/INFO]: Default File is missing! Deploying...")
        deploy_schema(os.path.join(script_dir, "Schemas"))

    if not os.path.isdir(os.path.join(script_dir, "Default")):
        lg.info("[pyJSON.main/INFO]: Defaults Directory is missing! Creating...")
        try:
            os.makedirs(os.path.join(script_dir, "Default"), exist_ok = True)
        except OSError as err:
            lg.error(err)
            str_message = "[pyJSON.main/FATAL]: Cannot create directory. Please check permissions!"
            QMessageBox.critical(
                QWidget(),
                "[pyJSON.main/FATAL]",
                str_message
            )
            sys.exit(1)

# Load or create and save the main index file
    index_dict = {
        "cur_index": 0
    }
    if not (os.path.isfile(os.path.join(script_dir, "Indexes/pyJSON_S_index.json"))):
        lg.warning("[pyJSON.main/WARN]: Index file is missing. Create index from scratch.")
        try:
            os.mkdir(os.path.join(script_dir, "Indexes"))
        except FileExistsError as err:
            pass
        save_main_index(script_dir, index_dict)
    else:
        try:
            index_dict = json.load(open(
                os.path.join(script_dir, "Indexes/pyJSON_S_index.json"),
                encoding = "utf8"),
                cls = json.JSONDecoder
            )
        except OSError as err:
            lg.error(err)
            lg.error("[pyJSON.main/ERROR]: Cannot read or access Index file. Defaulting to blank Index.")

    # overwrites config with command line parameters
    if args.path:
        if os.path.isdir(args.path):
            config["last_dir"] = args.path
            if config["last_dir"] not in index_dict and os.path.isdir(config["last_dir"]):
                lg.info("[pyJSON.main/INFO]: Last directory currently not indexed - indexing now.")
                jsonsearch_lib.start_index(script_dir, config["last_dir"], index_dict, show_boxes = False)
                index_dict = json.load(open(
                    os.path.join(script_dir, "Indexes/pyJSON_S_index.json"),
                    encoding = "utf8"),
                    cls = json.JSONDecoder
                )
        else:
            lg.error("[pyJSON.main/ERROR]: Provided path is erroneous. Omitted parameter -d.")

    if args.schema:
        if os.path.isfile(os.path.join(script_dir, "Schemas", args.schema + ".json")):
            config["last_schema"] = args.schema + ".json"
        else:
            lg.error("[pyJSON.main/ERROR]: Provided schema seems to not exist. Omitted parameter -s.")

    if args.file:
        if os.path.isfile(args.file):
            config["last_JSON"] = args.file
        else:
            lg.error("[pyJSON.main/ERROR]: Provided JSON document seems to not exist. Omitted parameter -f.")

    save_config(script_dir, config)

    # Checks whetever JSON and Schema retrieved from the config exist.
    if not os.path.isfile(os.path.join(script_dir, "Schemas", config["last_schema"])):
        lg.warning("[pyJSON.main/WARN]: Schema in config is missing. Falling back to default.")
        config["last_schema"] = "default.json"
        save_config(script_dir, config)
    if config["last_JSON"] is None:
        lg.info("\n----------\nNo last JSON set in config. Defaulting to blank.\n----------")
    else:
        if not os.path.isfile(config["last_JSON"]):
            lg.warning("\n----------\nLast JSON not found!!\nDefaulting to blank.\n----------")
            QMessageBox.warning(
                QWidget(),
                "[pyJSON.main/WARN]",
                "Last JSON not found. Defaulting to blank."
            )
            config["last_JSON"] = None
            save_config(script_dir, config)

    # set MainWindow and UI
    MainWindow = QtWidgets.QMainWindow()
    ui = UiRunnerInstance(config = config, index_dict = index_dict, script_dir = script_dir)

    jsonsearch_lib.watchdog(script_dir, index_dict)

    # enter main loop
    sys.exit(app.exec())