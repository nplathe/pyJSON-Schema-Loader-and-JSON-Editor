# ----------------------------------------
# a model for the json schema that implements TreeModel and by extension QAbstractModel
# author: N. Plathe
# ----------------------------------------
"""
This subclass of TreeModel is providing specialised functionality in order to work well with the interface.
"""
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------
import logging

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import QMessageBox, QWidget

from Modules.TreeModel import TreeClass

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

class ModifiedTreeClass(TreeClass):
    """
    This modified TreeClass provides an adapted routine to set data by trying to cast entered information to the
    appropriate data type to prevent accidentially entering wrong information. Furthermore, the flag-function
    gets overwritten in order to provide the proper item roles to prevent users from editing data other than
    the JSON values to be.
    """
    def flags(self, index):
        """
        Adapted flag function to provide the proper flags for our table-like structure in the TreeView

        Args:
            index (QModelIndex): the index of an item to be checked

        Returns:
            int: the role(s) of the cell
        """
        match index.column():
            case 2:
                return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            case _:
                return Qt.ItemIsEnabled

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        """
        An overwritten setData-function to check the data type via type casting.

        Args:
            index (QModelIndex): the index of the data to edit.
            value (object): the new data to be set. Should almost always be a string, except for boolean values.
            role (int): the role of that node.

        Returns:
            bool: whetever setting the data was successful
        """
        if role != Qt.EditRole:
            return False

        item = self.getItem(index)
        item_type = item.get_data_array()[3]

        try:
            if value != '':
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
            else:
                logging.warning("[ModifiedTreeModel.ModifiedTreeClass.setData/WARN]: " +
                           "Empty value set - type validation bypassed.")
            result = item.set_data(column = index.column(), data = value)
            if result:
                self.dataChanged.emit(index, index)
                logging.info("\n----------\n[ModifiedTreeModel.ModifiedTreeClass.setData/INFO]: Data got replaced! New Data is:\n" +
                        str(item.get_data_array()) + "\n----------")
            return result
        except ValueError as err:
            logging.error("[ModifiedTreeModel.ModifiedTreeClass.setData/ERROR]: " +
                     "Input could not be validated against type proposed from Schema!")
            QMessageBox.critical(
                QWidget(),
                "[ModifiedTreeModel.ModifiedTreeClass.setData/ERROR]",
                "Input could not be validated against type proposed from Schema!"
            )
            return False