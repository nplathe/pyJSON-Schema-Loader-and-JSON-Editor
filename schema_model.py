# ----------------------------------------
# a model for the json schema that implements QAbstractModel
# almost feature complete implementation from examples of the Qt Documentation...
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QModelIndex, Qt
import logging
# ----------------------------------------
# Variables and Functions
# ----------------------------------------

lg = logging.getLogger(__name__)
lg.setLevel("DEBUG")


class TreeItem(object):
    """
    The TreeItem Class is a structure implementing the needed node functions for the TreeClass.
    """
    def __init__(self, parent = None, data = []):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    # child functions

    def appendChild(self, child):
        """
        Adds a child to childItems

        Args:
            child: the child to be added

        Returns:

        """
        self.childItems.append(child)

    def retrieveChildbyIndex(self, child_index):
        """
        retrieves a child node by given index

        Args:
            child_index: The index value of the child to be retrieved

        Returns:
            TreeItem: the child item to be returns. Returns none, if there is an IndexError.
        """
        try:
            return self.childItems[child_index]
        except IndexError:
            return None

    def ChildIndexSelf(self):
        """
        returns the own index if being a child of another node

        Returns:
            int: the own index. Returns 0 if parentItem is None
        """
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0

    def countChildren(self):
        """
        returns the length of the list storing the child items
        Returns:
            int: child item count
        """
        return len(self.childItems)

    # data functions

    def setDataArray(self, data):
        """
        Sets or overwrites the entire data list
        Args:
            data (list): the new data to be written

        Returns:
        """
        self.itemData = data

    def setData(self, data: str, column: int):
        """
        Sets a specific value at the given column value
        Args:
            data: value that shall be set
            column: value of the column to be modified

        Returns:
            bool: whetever setting or overwriting was a success
        """
        if column < 0 or column > len(self.itemData):
            return False
        self.itemData[column] = data
        return True

    def getData(self, column):
        """
        retrieves data of a column
        Args:
            column: the value of the column to be retrieved

        Returns:
            object: the object stored inside the column of the data list. Most of the time a string or an int.
        """
        if column < 0 or column >= len(self.itemData):
            return None
        return self.itemData[column]

    def getDataArray(self):
        """
        Returns:
            list: the full data list of the item
        """
        return self.itemData

    def DataLength(self):
        """
        Returns:
            int: length of the data list - which equals the amount of columns in the TreeView later
        """
        return len(self.itemData)

    def getParent(self):
        """
        Returns:
            TreeItem: the parent node
        """
        return self.parentItem

# The Tree-like Model
class TreeClass(QtCore.QAbstractItemModel):
    """
    Inhereting QAbstractItemModel, this TreeClass implements the needed functions and elements to be presented
    to the user in the TreeView in the user interface.
    """
    def __init__(self, parent = None, data = []):
        """
        Constructor

        Args:
            parent: the parent object. Most of the time, this will be None.
            data: the list of data that shall be used by the root node and determine the column count
        """
        super(TreeClass, self).__init__(parent)
        self.root_node = TreeItem(data = data)

    def getItem(self, index):
        """
        gets an item by its model index.

        Args:
            index (QModelIndex): A QModelIndex holding the position of the item to get from the model

        Returns:
            object: the item or node in the tree model
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
            parentItem = self.root_node
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.retrieveChildbyIndex(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        """
        returns the parent of a child node
        Args:
            child (QModelIndex): the index of a child node

        Returns:
            QModelIndex: the index of a parent. Returns an invalid index, if childs index is not valid or the root node.
        """
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.getParent()

        if parentItem == self.root_node:
            return QModelIndex()

        return self.createIndex(parentItem.ChildIndexSelf(), 0, parentItem)

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
            parentItem = self.root_node
        else:
            parentItem = parent.internalPointer()

        return parentItem.countChildren()

    def columnCount(self, parent = QModelIndex()):
        """
        returns the column count based on the parent

        Args:
            parent (QModelIndex): the QModelIndex of a parent node.

        Returns:
            int: column count
        """
        if parent.isValid():
            return parent.internalPointer().DataLength()
        else:
            return self.root_node.DataLength()

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
            return self.root_node.getData(section)
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
        return node.getData(index.column())

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        """
        sets or overwrites data. Checks Qts item flags before actually doing so.
        Args:
            index (QModelIndex): the index of the data to edit.
            value (object): the new data to be set.
            role (int): the role of that node.

        Returns:
            bool: whetever setting the data was successful
        """
        if role != Qt.EditRole:
            return False
        item = self.getItem(index)
        result = item.setData(column = index.column(), data = value)
        if result:
            self.dataChanged.emit(index, index)
            lg.info("\n----------\n[schema_model.TreeClass.setData/INFO]: Data got replaced! New Data is:\n" +
            str(item.getDataArray()) + "\n----------")
        return result

    def add_node(self, parent, data):
        """
        Adds a node as a child to a given parent

        Args:
            parent (TreeItem): the parent node the new node is attached to
            data (list): a list of the data of the new node

        Returns:
        """
        node = TreeItem(data = data, parent = parent)
        parent.appendChild(node)

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
    model.add_node(parent = model.root_node.retrieveChildbyIndex(0), data = ["Attack Move 1", "Flamethrower", "Powerful Fire Attack with chance of inflicting burns."])

    model.add_node(parent = model.root_node.retrieveChildbyIndex(0).retrieveChildbyIndex(0),
        data = ["Damage Class", "Special", "Determines whetever using Atk and Def or Sp. Atk and Sp. Def for Damage calculation"])
    model.add_node(parent=model.root_node.retrieveChildbyIndex(0).retrieveChildbyIndex(0),
        data=["Element Type", "Fire", "Determines effectiveness against Foes Element Type"])
    model.add_node(parent=model.root_node.retrieveChildbyIndex(0).retrieveChildbyIndex(0),
        data=["Power", "90", "Determines the Power of the Attack"])

    model.add_node(parent=model.root_node.retrieveChildbyIndex(0), data=["Attack Move 2", "Fly", "Flies up in Round 1, Attacks in Round 2."])
    model.add_node(parent=model.root_node.retrieveChildbyIndex(0).retrieveChildbyIndex(1),
        data=["Damage Class", "Physical", "Determines whetever using Atk and Def or Sp. Atk and Sp. Def for Damage calculation"])
    model.add_node(parent=model.root_node.retrieveChildbyIndex(0).retrieveChildbyIndex(1),
        data=["Element Type", "Flying", "Determines effectiveness against Foes Element Type"])
    model.add_node(parent=model.root_node.retrieveChildbyIndex(0).retrieveChildbyIndex(1),
        data=["Power", "90", "Determines the Power of the Attack"])

    ui.setModel(model)
    ui.show()

    sys.exit(app.exec_())