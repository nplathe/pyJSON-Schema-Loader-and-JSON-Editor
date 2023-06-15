# ----------------------------------------
# A tree-like model that implements QAbstractModel.
# Implementation based on examples of the Qt Documentation.
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QModelIndex, Qt

import logging

from Modules.TreeItem import TreeItem

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

lg = logging.getLogger(__name__)
lg.setLevel("DEBUG")

# The Tree-like Model
class TreeClass(QtCore.QAbstractItemModel):
    """
    Inhereting QAbstractItemModel, this TreeClass implements the needed functions and elements to be presented
    to the user in the TreeView in the user interface.
    """
    def __init__(self, parent = None, data = None):
        """
        Constructor

        Args:
            parent: the parent object. Most of the time, this will be None.
            data: the list of data that shall be used by the root node and determine the column count
        """
        super(TreeClass, self).__init__(parent)
        if data is None:
            data = []
        self.root_node = TreeItem(data = data)

    def getItem(self, index):
        """
        gets an item by its model index.

        Args:
            index (QModelIndex): A QModelIndex holding the position of the item to get from the model

        Returns:
            TreeItem: the item or node in the tree model
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        """
        returns a valid model index based on row and column of the grid-based coordinate system in the TreeView
        Note: The signature differs from the base method for reasons?

        Args:
            row (int): the row of the item thats model index is to be retrieved
            column (int): the column of the item
            parent (QModelIndex): the model index of the parent node. Most of the time, this is used with the root node.

        Returns:
            QModelIndex: a valid index, if an item is present at that row and column, an empty index otherwise
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_node
        else:
            parent_item = parent.internalPointer()

        childItem = parent_item.retrieve_child_by_index(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex: # function is overloaded in QAbstractItemModel
        """
        returns the parent of a child node

        Args:
            child (QModelIndex): the index of a child node

        Returns:
            QModelIndex: the index of a parent. Returns an invalid index, if childs index is not valid or the root node.
        """
        if not child.isValid():
            return QModelIndex()

        child_item = child.internalPointer()
        parent_item = child_item.get_parent()

        if parent_item == self.root_node:
            return QModelIndex()

        return self.createIndex(parent_item.child_index_self(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        returns the row count based on the parent

        Args:
            parent (QModelIndex): the QModelIndex of a parent node.

        Returns:
            int: row count
        """
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item = self.root_node
        else:
            parent_item = parent.internalPointer()

        return parent_item.count_children()

    def columnCount(self, parent = QModelIndex()):
        """
        returns the column count based on the parent

        Args:
            parent (QModelIndex): the QModelIndex of a parent node.

        Returns:
            int: column count
        """
        if parent.isValid():
            return parent.internalPointer().data_length()
        else:
            return self.root_node.data_length()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        """
        accesses the header data, which is stored in the root node.

        Args:
            section (int): the column
            orientation(Qt.Orientation): the orientation of the widget
            role(int): the item role of the header

        Returns:
            object: the column header, if orientation is horizontal and role is DisplayRole. Is a string, probably. None otherwise.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_node.get_data(section)
        return None

    def data(self, index: QModelIndex, role: int = ...):
        """
        returns the data of an item at a given QModelIndex

        Args:
            index (QModelIndex): the index of the item to be fetched the data from
            role (int): the item role of the item located at the index

        Returns:
            the data value at given index. None if the index is non-valid or the role is not DisplyRole or EditRole
        """
        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        node = self.getItem(index)
        return node.get_data(index.column())

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        """
        sets or overwrites data. Checks Qts item flags before actually doing so.
        Args:
            index (QModelIndex): the index of the data to edit.
            value (str): the new data to be set.
            role (int): the role of that node.

        Returns:
            bool: whetever setting the data was successful
        """
        if role != Qt.EditRole:
            return False
        item = self.getItem(index)
        result = item.set_data(column = index.column(), data = value)
        if result:
            self.dataChanged.emit(index, index)
            lg.info("\n----------\n[TreeModel.TreeClass.setData/INFO]: Data got replaced! New Data is:\n" +
            str(item.get_data_array()) + "\n----------")
        return result

    def add_node(self, parent, data, metadata = None):
        """
        Adds a node as a child to a given parent

        Args:
            parent (TreeItem): the parent node the new node is attached to
            data (list): a list of the data of the new node
            metadata (dict): metadata from the schema
        Returns:
        """
        node = TreeItem(data = data, parent = parent, metadata = metadata)
        parent.append_child(node)

    def flags(self, index):
        """
        returns the flags of an item at a given QModelIndex.

        Args:
            index (QModelIndex): the index of an item in the TreeView

        Returns:
            int: a non-zero value for the item roles used by Qt. 0, if the index is not valid.
        """
        if not index.isValid():
            return 0

        return Qt.ItemIsEditable | super(TreeClass, self).flags(index)

    def insertColumns(self, position: int, columns: int, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Inserts columns into the model via calling the respective function of the root node.
        Args:
            position (int): position from which the insertion should start
            columns (int): amount of columns to be added
            parent (QModelIndex): The parent for... uh... eh...

        Returns:
            bool: a boolean value whetever the insertion was a success
        """
        self.beginInsertColumns(parent, position, position + columns - 1)
        success: bool = self.root_node.insert_columns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """
        inserts rows at the given position
        Args:
            position (int): position of where to enter the rows
            rows (int): amount of rows to add
            parent (QModelIndex): parent node

        Returns:
            bool: a boolean value whetever the insertion was a success
        """
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success: bool = parentItem.insert_children(position, rows, self.root_node.data_length())
        self.endInsertRows()

        return success

    def removeColumns(self, position: int, columns: int, parent: QModelIndex = QModelIndex())  -> bool:
        """
        Removes columns and, if no columns are present anymore, all rows.

        Args:
            position (int): position from which to start the removal
            columns (int): amount of columns to be removed
            parent (QModelIndex): parent node.

        Returns:
            bool: a boolean value whetever removal was a success
        """
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success: bool = self.root_node.remove_columns(position, columns)
        self.endRemoveColumns()

        if self.root_node.data_length() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Removes rows in the model.

        Args:
            position (int): position from which the removal starts
            rows (int): amount of rows to be removed
            parent (QModelIndex): parent node

        Returns:
            bool: a boolean value whetever removal was a success
        """
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success: bool = parentItem.remove_children(position, rows)
        self.endRemoveRows()

        return success

    def _repr_recursion(self, item: TreeItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        for child in item.childItems:
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_node)

# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":

    # Just a toy example
    import sys

    print("Running functional toy example:")

    app = QtWidgets.QApplication(sys.argv)
    ui = QtWidgets.QTreeView()

    model = TreeClass(data=["Key", "Value", "Descr"])
    model.add_node(parent = model.root_node, data = ["Name","Charizard","The Pokémon name"])
    model.add_node(parent = model.root_node.retrieve_child_by_index(0), data = ["Attack Move 1", "Flamethrower", "Powerful Fire Attack with chance of inflicting burns."])

    model.add_node(parent = model.root_node.retrieve_child_by_index(0).retrieve_child_by_index(0),
                   data = ["Damage Class", "Special", "Determines whetever using Atk and Def or Sp. Atk and Sp. Def for Damage calculation"])
    model.add_node(parent=model.root_node.retrieve_child_by_index(0).retrieve_child_by_index(0),
                   data=["Element Type", "Fire", "Determines effectiveness against Foes Element Type"])
    model.add_node(parent=model.root_node.retrieve_child_by_index(0).retrieve_child_by_index(0),
                   data=["Power", "90", "Determines the Power of the Attack"])

    model.add_node(parent=model.root_node.retrieve_child_by_index(0), data=["Attack Move 2", "Fly", "Flies up in Round 1, Attacks in Round 2."])
    model.add_node(parent=model.root_node.retrieve_child_by_index(0).retrieve_child_by_index(1),
                   data=["Damage Class", "Physical", "Determines whetever using Atk and Def or Sp. Atk and Sp. Def for Damage calculation"])
    model.add_node(parent=model.root_node.retrieve_child_by_index(0).retrieve_child_by_index(1),
                   data=["Element Type", "Flying", "Determines effectiveness against Foes Element Type"])
    model.add_node(parent=model.root_node.retrieve_child_by_index(0).retrieve_child_by_index(1),
                   data=["Power", "90", "Determines the Power of the Attack"])

    ui.setModel(model)
    ui.show()

    sys.exit(app.exec())