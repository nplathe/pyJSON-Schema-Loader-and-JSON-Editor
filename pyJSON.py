# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Main Module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------
# import 3rd party and system libraries
import argparse
import json
import logging
import os
import regex as re
import shutil
import logging as lg
from datetime import datetime

# import PyQt libraries
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest, uic
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QLabel, QComboBox, QStyledItemDelegate, QStyle

# import tkinter modules
import tkinter as tk
from tkinter import messagebox, filedialog

# import of modules
import jsonio_lib
from deploy_files import deploy_schema, deploy_config, save_config
from schema_model import TreeClass as TC


# ----------------------------------------
# Variables and Functions
# ----------------------------------------

# We manipulate our TreeClas with a very specific function that blocks editing for all but the second column.
# Furthermore, setData needs to be overwritten in order to do input validation.
class TreeClass(TC):
    def flags(self, index):
        match index.column():
            case 2:
                return Qt.ItemIsEditable | Qt.ItemIsEnabled
            case _:
                return Qt.ItemIsEnabled

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole:
            return False

        item = self.getItem(index)
        item_type = item.getDataArray()[3]

        try:
            match item_type:
                case "integer":
                    int(value)
                case "number":
                    float(value)
                case "boolean":
                    bool(value)
                case "array":
                    pass
                case _:
                    pass
            result = item.setData(column=index.column(), data=value)
            if result:
                self.dataChanged.emit(index, index)
                lg.info("\n----------\n[schema_model.TreeClass.setData/INFO]: Data got replaced! New Data is:\n" +
                        str(item.getDataArray()) + "\n----------")
            return result
        except ValueError as err:
            lg.error("[pyJSON.TreeClass.setData/ERROR]: " +
                     "Input could not be validated against type proposed from Schema!")
            tk.messagebox.showerror(
                title="[pyJSON.TreeClass.setData/ERROR]",
                message="Input could not be validated against type proposed from Schema!"
            )
            return False


# We need a parser of command line arguments:
parser = argparse.ArgumentParser(
    description="pyJSON Schema Loader and JSON Editor - a tool for editing and generating JSON files utilizing " +
                "JSON Schema.\nWhen starting pyJSON va command line, the parameter -i can be used to overwrite the last used " +
                "directory. If a metadata.json file is present, it will be loaded, else, the last schema will be used to generate" +
                " a blank. When using -v, pyJSON will generate a log file."
)
parser.add_argument('-i', '--input-directory',
                    dest="path",
                    help="This parameter overwrites the last used directory.")
parser.add_argument('-v', '--verbose',
                    action="store_true",
                    dest="verbose",
                    help="If set, a log will be generated.")
args = parser.parse_args()


# class extension of my GUI, containing all functions related to the GUI
class Ui_RunnerInstance(QtWidgets.QMainWindow):
    def __init__(self):

        # we first call init from the super class, then load the UI file from designer
        super(Ui_RunnerInstance, self).__init__()
        uic.loadUi('pyJSON_interface.ui', self)

        title = "pyJSON Schema Loader and JSON Editor"
        self.setWindowTitle(title)

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

        self.button_savemdJSON = self.findChild(QtWidgets.QPushButton, 'pushButton_save_md_JSON')
        self.button_savemdJSON.clicked.connect(self.save_md_json)

        self.button_loadmdJSON = self.findChild(QtWidgets.QPushButton, 'pushButton_load_md_JSON')
        self.button_loadmdJSON.clicked.connect(self.load_md_json)

        # adding in the action functions (the menu bar)
        self.openJSON = self.findChild(QtWidgets.QAction, 'actionOpen_JSON')
        self.openJSON.setStatusTip("Open a JSON file for editing.")
        self.openJSON.triggered.connect(self.jsonopener)

        self.openYAML = self.findChild(QtWidgets.QAction, 'actionOpen_YAML')
        self.openYAML.setStatusTip("Open a YAML file for conversion and editing.")
        self.openYAML.triggered.connect(self.yamlopener)

        self.copySchema = self.findChild(QtWidgets.QAction, 'actionAdd_Schema')
        self.copySchema.setStatusTip("Copy a schema into the tool storage.")
        self.copySchema.triggered.connect(self.copy_schema_to_storage)

        self.save_as_json = self.findChild(QtWidgets.QAction, 'actionSave_as')
        self.save_as_json.setStatusTip("Save the current JSON at a specific location of the computer. " +
                                       "Does not overwrite the working directory.")
        self.save_as_json.triggered.connect(self.save_as_function)

        self.save_json = self.findChild(QtWidgets.QAction, 'actionSave')
        self.save_json.setStatusTip("Save the current JSON")
        self.save_json.triggered.connect(self.save_function)

        self.blank_from_schem = self.findChild(QtWidgets.QAction, 'actionCreate_JSON_from_selected_Schema')
        self.blank_from_schem.setStatusTip("Removes the current JSON and loads a blank from the selected schema.")
        self.blank_from_schem.triggered.connect(self.set_blank_from_schema)

        self.edit_from_def = self.findChild(QtWidgets.QAction, 'actionLoad_default_for_selected_schema')
        self.edit_from_def.setStatusTip("Load default values from the Default storage of the tool.")
        self.edit_from_def.triggered.connect(self.load_default)

        self.edit_to_def = self.findChild(QtWidgets.QAction, 'actionSave_as_default')
        self.edit_to_def.setStatusTip("Saves the current values as default for later use. " +
                                      "The default is named after the schema!")
        self.edit_to_def.triggered.connect(self.save_default)

        self.validate_Action = self.findChild(QtWidgets.QAction, 'actionValidate_input_against_selected_schema')
        self.validate_Action.setStatusTip("Validate the current input against the schema.")
        self.validate_Action.triggered.connect(self.validate_Function)

        self.reload_json = self.findChild(QtWidgets.QAction, 'actionReload_JSON_and_drop_Changes')
        self.reload_json.setStatusTip("Reload the JSON from the Drive and ommit all changes.")
        self.reload_json.triggered.connect(self.reloader_function)

        # the heartpiece of the GUI is the TreeView
        self.TreeView = self.findChild(QtWidgets.QTreeView, 'treeView')

        # I need some of the labels to be accessible
        self.cur_json_label = self.findChild(QLabel, "current_JSON_label")

        # Drop-Down Menu
        self.curr_schem_ddm = self.findChild(QComboBox, "current_schema_combo_box")
        self.curr_schem_ddm.currentTextChanged.connect(self.combobox_selected)

        # call the show function
        self.show()

    # Button Function Definitions

    # wdgetter is self-explanatory...
    def wdgetter(self):
        result = os.getcwd()
        self.line.setText(result)

    # scans the TextLine for a dir and sets the wd accordingly
    def wdsetter(self):
        result = os.path.normpath(str(self.line.text()))
        if os.path.isdir(result):
            self.button_1.setText("Success!")
            os.chdir(result)
            QtTest.QTest.qWait(2000)
            self.button_1.setText("Set new directory!")
            config["last_dir"] = os.path.normpath(result)
            save_config(script_dir, config)
        else:
            self.button_1.setText("ERROR: Check the path!")
            QtTest.QTest.qWait(2000)
            self.button_1.setText("Set new directory!")

    # sets the working directory to the selection
    def diropener(self):
        dir_path = os.path.normpath(tk.filedialog.askdirectory())
        try:
            os.chdir(dir_path)
            if dir_path == '' or dir_path == '.':
                raise OSError("[pyJSON.diropener/WARN]: Directory selection aborted!")
            config["last_dir"] = dir_path
            save_config(script_dir, config)
            self.line.setText(dir_path)
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
                lg.error(err)

    # Definition Actions MenuBar

    # Open a JSON and reload the TreeView with the new information
    def jsonopener(self):
        try:
            filepath_str = tk.filedialog.askopenfilename(
                filetypes=(('Java Script Object Notation', '*.json'), ('All Files', '*.*')))
            if filepath_str == '':
                raise OSError("[pyJSON.jsonopener/WARN]: File Selection aborted!")
            if not os.path.isfile(filepath_str):
                raise FileNotFoundError("[pyJSON.jsonopener/ERROR]: Specified file does not exist.")

            filepath = os.path.normpath(filepath_str)
            read_frame = jsonio_lib.decode_function(filepath)
            if type(read_frame) is int and read_frame == -999:
                raise FileNotFoundError("[pyJSON.jsonopener/ERROR]: Specified file does not exist.")
            schema_read = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
            schema_frame = jsonio_lib.schema_to_ref_gen(schema_read)
            schema_title = jsonio_lib.schema_to_title_gen(schema_read)
            schema_type = jsonio_lib.schema_to_type_gen(schema_read)
            new_tree = jsonio_lib.py_to_tree(read_frame, schema_type, schema_title, schema_frame,
                                             TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))
            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
            if new_tree:
                config["last_JSON"] = filepath
                save_config(script_dir, config)
                self.cur_json_label.setText(filepath)

        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.jsonopener/ERROR]",
                message="[pyJSON.jsonopener/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            lg.error(err)

    # opens and converts YAML files according to a schema definition
    def yamlopener(self):
        try:
            filepath = os.path.normpath(tk.filedialog.askopenfilename(
                filetypes=(('YAML Ain\'t Markup Language', '*.yaml'), ('All Files', '*.*'))))
            if filepath == '':
                raise OSError("[pyJSON.yamlopener/WARN]: File Selection aborted!")
            if not os.path.isfile(filepath):
                raise FileNotFoundError("[pyJSON.yamlopener/ERROR]: Specified file does not exist.")
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.yamlopener/ERROR]",
                message="[pyJSON.yamlopener/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            lg.error(err)
        lg.info(filepath)  # TODO fill this with life from jsonio_lib.py

    # reloads the contents of the drop down menu and updates the list with potential new schemas
    def combobox_repopulate(self):
        if self.curr_schem_ddm.count == 0:
            self.curr_schem_ddm.blockSignals(True)
            schema_list = os.listdir(os.path.join(script_dir, "Schemas"))
            for x in schema_list:
                self.curr_schem_ddm.addItem(x)
            self.curr_schem_ddm.blockSignals(False)
        else:
            self.curr_schem_ddm.blockSignals(True)
            self.curr_schem_ddm.clear()
            schema_list = os.listdir(os.path.join(script_dir, "Schemas"))
            for x in schema_list:
                self.curr_schem_ddm.addItem(x)
            self.curr_schem_ddm.update()
            self.curr_schem_ddm.blockSignals(False)

    # gets executed when the user selects or swaps the schema and updates the TreeView
    def combobox_selected(self):
        lg.info("\n----------\nswapped schema!\n----------")
        selected = self.curr_schem_ddm.currentText()
        try:
            schema = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", selected))
            if type(schema) is int and schema == -999:
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.combobox_selected/ERROR]: Schema File is missing!")
            schema_frame = jsonio_lib.schema_to_ref_gen(schema)
            schema_title = jsonio_lib.schema_to_title_gen(schema)
            schema_type = jsonio_lib.schema_to_type_gen(schema)

            if not config["last_JSON"] is None:
                read_frame = jsonio_lib.decode_function(config["last_JSON"])
                new_tree = jsonio_lib.py_to_tree(read_frame, schema_type, schema_title, schema_frame,
                                                 TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))
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
                title="[pyJSON.copy_schema_to_storage/ERROR]",
                message=str(err)
            )

    # copies a schema to the schema storage
    def copy_schema_to_storage(self):
        lg.info("\n----------\nCopying schema to tool storage.\n-----------")
        try:
            filepath = os.path.normpath(tk.filedialog.askopenfilename(
                filetypes=(('Java Script Object Notation', '*.json'), ('All Files', '*.*'))))
            if filepath == '':
                raise OSError("[pyJSON.copy_schema_to_storage/WARN]: File Selection aborted!")
            if not os.path.isfile(filepath):
                raise FileNotFoundError("[pyJSON.copy_schema_to_storage/ERROR]: Specified file does not exist.")
            if filepath == os.path.join(script_dir, "Schemas", os.path.basename(filepath)):
                tk.messagebox.showwarning(
                    title="[pyJSON.copy_schema_to_storage/WARN]",
                    message="[pyJSON.copy_schema_to_storage/WARN]: Source schema seems to be already in the schema " +
                            "folder. It will not be copied."
                )
            else:
                shutil.copyfile(filepath, os.path.join(script_dir, "Schemas", os.path.basename(filepath)))
            self.combobox_repopulate()
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.copy_schema_to_storage/ERROR]",
                message="[pyJSON.copy_schema_to_storage/ERROR]: Specified file does not exist."
            )
        except OSError as err:
            lg.error(err)

    # saves the current JSON as metadata.json in the current working directory
    def save_md_json(self):
        curr_json = os.path.normpath(os.path.join(config["last_dir"], "metadata.json"))
        lg.info("Current metadata.json path: " + curr_json)
        tree = self.TreeView.model()
        json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
        try:
            with open(curr_json, "w") as out:
                json.dump(json_frame, out, indent=4)
                config["last_JSON"] = curr_json
                save_config(script_dir, config)
                self.cur_json_label.setText(curr_json)
        except OSError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.save_curr_json/ERROR]",
                message="[pyJSON.save_curr_json/ERROR]: File seems to neither exist nor writable!"
            )

    # the "Save as..." function
    def save_as_function(self):
        selected_path = os.path.normpath(tk.filedialog.asksaveasfilename(
            filetypes=(('Java Script Object Notation', '*.json'), ('All Files', '*.*'))))
        if selected_path == '' or selected_path == ".":
            lg.info("[pyJSON.save_curr_json/INFO]: Either file selection aborted or you have selected a very odd path.")
        else:
            if re.match(pattern=re.compile(".*\.json$"), string=selected_path) is None:
                selected_path = selected_path + ".json"
            tree = self.TreeView.model()
            json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
            try:
                with open(selected_path, "w") as out:
                    json.dump(json_frame, out, indent=4)
                    config["last_JSON"] = selected_path
                    save_config(script_dir, config)
                    self.cur_json_label.setText(selected_path)
            except OSError as err:
                lg.error(err)
                tk.messagebox.showerror(
                    title="[pyJSON.save_curr_json/ERROR]",
                    message="[pyJSON.save_curr_json/ERROR]: File seems to neither exist nor writable!"
                )

    # the "Save" function.
    def save_function(self):
        if config["last_JSON"] is None:
            self.save_as_function()
        else:
            tree = self.TreeView.model()
            json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
            try:
                with open(config["last_JSON"], "w") as out:
                    json.dump(json_frame, out, indent=4)
            except OSError as err:
                lg.error(err)
                tk.messagebox.showerror(
                    title="[pyJSON.save_curr_json/ERROR]",
                    message="[pyJSON.save_curr_json/ERROR]: File seems to neither exist nor writable!"
                )

    # load_md_json loads a "metadata.json" named file.
    def load_md_json(self):
        lg.info('\n----------\nLoading metadata.json...\n----------')
        try:
            filepath = os.path.normpath(os.path.join(config["last_dir"], "metadata.json"))
            read_frame = jsonio_lib.decode_function(filepath)

            if type(read_frame) is int and read_frame == -999:
                raise FileNotFoundError
            schema_read = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
            schema_frame = jsonio_lib.schema_to_ref_gen(schema_read)
            schema_title = jsonio_lib.schema_to_title_gen(schema_read)
            schema_type = jsonio_lib.schema_to_type_gen(schema_read)
            new_tree = jsonio_lib.py_to_tree(read_frame, schema_type, schema_title, schema_frame,
                                             TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())
            if new_tree:
                config["last_JSON"] = os.path.normpath(filepath)
                save_config(script_dir, config)
                self.cur_json_label.setText(filepath)

        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.load_md_json/ERROR]",
                message="[pyJSON.load_md_json/ERROR]: metadata.json does not exist."
            )
        except OSError as err:
            lg.error(err)

    # set_blank_from_schema sets a JSON from the schema, that is completely blank
    def set_blank_from_schema(self):
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

            pre_json = jsonio_lib.schema_to_py_gen(curr_schem)
            pre_descr = jsonio_lib.schema_to_ref_gen(curr_schem)
            pre_title = jsonio_lib.schema_to_title_gen(curr_schem)
            pre_type = jsonio_lib.schema_to_type_gen(curr_schem)

            new_tree = jsonio_lib.py_to_tree(pre_json, pre_type, pre_title, pre_descr,
                                             TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())

            if new_tree:
                config["last_JSON"] = None
                save_config(script_dir, config)
                self.cur_json_label.setText("None")

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
        lg.info("\n----------\nSaving default for Schema " + config["last_schema"] + "\n----------")
        tree = self.TreeView.model()
        json_frame = jsonio_lib.tree_to_py(tree.root_node.childItems)
        try:
            with open(os.path.join(script_dir, "Default", config["last_schema"]), "w") as out:
                json.dump(json_frame, out, indent=4)
        except OSError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.save_default/ERROR]",
                message="[pyJSON.save_default/ERROR]: File seems to neither exist nor writable!"
            )

    def load_default(self):
        lg.info("\n----------\nLoading default for Schema " + config["last_schema"] + "\n----------")
        try:

            if not os.path.isfile(os.path.join(script_dir, "Default", config["last_schema"])):
                raise FileNotFoundError("[pyJSON.load_default/ERROR]: No default file found!")
            if not os.path.isfile(os.path.join(script_dir, "Schemas", config["last_schema"])):
                self.combobox_repopulate()
                raise FileNotFoundError("[pyJSON.load_default/ERROR]: Selected schema not found!")

            default_values = jsonio_lib.decode_function(os.path.join(script_dir, "Default", config["last_schema"]))

            schema_read = jsonio_lib.decode_function(os.path.join(script_dir, "Schemas", config["last_schema"]))
            schema_descr = jsonio_lib.schema_to_ref_gen(schema_read)
            schema_type = jsonio_lib.schema_to_type_gen(schema_read)
            schema_title = jsonio_lib.schema_to_title_gen(schema_read)

            new_tree = jsonio_lib.py_to_tree(default_values, schema_type, schema_title, schema_descr,
                                             TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))

            self.TreeView.reset()
            self.TreeView.setModel(new_tree)
            self.TreeView.expandAll()
            new_tree.dataChanged.emit(QModelIndex(), QModelIndex())

            if new_tree:
                config["last_JSON"] = None
                save_config(script_dir, config)
                self.cur_json_label.setText("None")
        except FileNotFoundError as err:
            lg.error(err)
            tk.messagebox.showerror(
                title="[pyJSON.load_default/ERROR]",
                message=str(err)
            )

    # The reloader function ... reloads JSON and Schema...
    def reloader_function(self):
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
                    schema_descr = jsonio_lib.schema_to_ref_gen(schema_read)
                    schema_type = jsonio_lib.schema_to_type_gen(schema_read)
                    schema_title = jsonio_lib.schema_to_title_gen(schema_read)

                    new_tree = jsonio_lib.py_to_tree(values, schema_type, schema_title, schema_descr,
                        TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))

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
        tree = self.TreeView.model()
        curr_json_py = jsonio_lib.tree_to_py(tree.root_node.childItems)
        curr_json = json.dumps(curr_json_py)
        result = jsonio_lib.validator_vars(curr_json, os.path.join(script_dir, "Schemas", config["last_schema"]))
        match result:
            case 0:
                tk.messagebox.showinfo(
                    title = "[pyJSON.validate_Function/INFO]",
                    message = "The JSON is valid against the schema!"
                )
            case 1:
                tk.messagebox.showerror(
                    title = "[pyJSON.validate_Function/ERROR]",
                    message = "The JSON is not valid against the schema!"
                )
            case 2:
                tk.messagebox.showerror(
                    title = "[pyJSON.validate_Function/ERROR]",
                    message = "The schema is not valid against its meta schema!"
                )
            case -999:
                tk.messagebox.showerror(
                    title="[pyJSON.validate_Function/ERROR]",
                    message="The schema is not accessible!"
                )

class BackgroundBrushDelegate(QStyledItemDelegate):
    def __init__(self, brush: QBrush, parent):
        super(BackgroundBrushDelegate, self).__init__()
        self.brush = brush

    def initStyleOption(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        super(BackgroundBrushDelegate, self).initStyleOption(option, index)
        option.backgroundBrush = self.brush


# ----------------------------------------
# Execution
# ----------------------------------------


if __name__ == "__main__":
    import sys

    # set Script Directory
    script_dir = os.getcwd()

    # running Tkinter modules to make my life easier
    tk_root = tk.Tk()
    tk_root.withdraw()

    # initialize the QtWidget
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_RunnerInstance()

    # initialize logging
    now = datetime.now()
    print(now)

    lg = logging.getLogger()
    lg.setLevel("DEBUG")
    formatter = logging.Formatter(fmt='%(asctime)s: %(message)s')

    # If -v is used, a log folder is needed.
    if args.verbose:
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

    # check and create or load the config of the tool
    if not os.path.isfile(os.path.join(script_dir, "pyJSON_conf.json")):
        lg.info("[pyJSON.main/INFO]: Config is missing. Creating one for you.")
        deploy_config(script_dir)
    config = json.load(open(os.path.join(script_dir, "pyJSON_conf.json")), cls=json.JSONDecoder)

    # If there was a command line parameter, it gets used here, overwriting the config.
    if args.path is not None:
        if os.path.isdir(args.path):
            config["last_dir"] = args.path
            if os.path.isfile(os.path.join(args.path, "metadata.json")):
                config["last_JSON"] = os.path.join(args.path, "metadata.json")
            else:
                config["last_JSON"] = None
            save_config(script_dir, config)
    os.chdir(config["last_dir"])

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
        st_pre_json = jsonio_lib.schema_to_py_gen(frame)
        ui.cur_json_label.setText("None")
    else:
        if os.path.isfile(config["last_JSON"]):
            st_pre_json = jsonio_lib.decode_function(config["last_JSON"])
            ui.cur_json_label.setText(os.path.normpath(config["last_JSON"]))
        else:
            lg.warning("\n----------\nJSON is missing!!\nGenerating blank from schema\n----------")
            tk.messagebox.showwarning(
                title="[pyJSON/WARN]",
                message="[pyJSON/WARN]: Last JSON not found. Defaulting to blank."
            )
            st_pre_json = jsonio_lib.schema_to_py_gen(frame)
            ui.cur_json_label.setText("None")
            config["last_JSON"] = None
            save_config(script_dir, config)

    lg.info("\n----------\nGenerating reference from schema\n----------")
    st_pre_descr = jsonio_lib.schema_to_ref_gen(frame)
    st_pre_title = jsonio_lib.schema_to_title_gen(frame)
    st_pre_type = jsonio_lib.schema_to_type_gen(frame)
    lg.info("\n----------\nConstructing Tree, please wait.\n---------")
    model = jsonio_lib.py_to_tree(st_pre_json, st_pre_type, st_pre_title, st_pre_descr,
                                  TreeClass(data=["Schema", "Title", "Value", "Type", "Description"]))
    ui.line.setText(config["last_dir"])

    ui.TreeView.setModel(model)

    # setting the column width for each column after setting the model.
    ui.TreeView.setColumnWidth(0, 100)
    ui.TreeView.setColumnWidth(1, 150)
    ui.TreeView.setColumnWidth(2, 500)
    ui.TreeView.setColumnWidth(3, 50)
    ui.TreeView.setColumnWidth(4, 500)

    # column colors using several delegates
    delegate1 = BackgroundBrushDelegate(brush=QBrush(QColor(240, 240, 240, 255)), parent=QBrush(Qt.white))
    delegate2 = BackgroundBrushDelegate(brush=QBrush(QColor(240, 240, 240, 255)), parent=QBrush(Qt.white))
    delegate3 = BackgroundBrushDelegate(brush=QBrush(QColor(240, 240, 240, 255)), parent=QBrush(Qt.white))
    delegate4 = BackgroundBrushDelegate(brush=QBrush(QColor(240, 240, 240, 255)), parent=QBrush(Qt.white))

    ui.TreeView.setItemDelegateForColumn(0, delegate1)
    ui.TreeView.setItemDelegateForColumn(1, delegate2)
    ui.TreeView.setItemDelegateForColumn(3, delegate3)
    ui.TreeView.setItemDelegateForColumn(4, delegate4)
    ui.TreeView.expandAll()

    ui.combobox_repopulate()
    ui.curr_schem_ddm.blockSignals(True)
    ui.curr_schem_ddm.setCurrentText(config["last_schema"])
    ui.curr_schem_ddm.blockSignals(False)

    # enter main loop
    sys.exit(app.exec_())
