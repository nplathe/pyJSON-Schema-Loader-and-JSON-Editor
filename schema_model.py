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

# The Tree Leaf
class TreeItem(object):
    def __init__(self, parent = None, data = []):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    # child functions

    def appendChild(self, child):
        self.childItems.append(child)

    def retrieveChildbyIndex(self, child_index):
        try:
            return self.childItems[child_index]
        except IndexError:
            return None

    def ChildIndexSelf(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0

    def countChildren(self):
        return len(self.childItems)

    # data functions

    def setDataArray(self, data):
        self.itemData = data

    def setData(self, data: str, column: int):
        if column < 0 or column > len(self.itemData):
            return False
        self.itemData[column] = data
        return True

    def getData(self, column):
        if column < 0 or column >= len(self.itemData):
            return None
        return self.itemData[column]

    def getDataArray(self):
        return self.itemData

    def DataLength(self): # aka the columns of our TreeView
        return len(self.itemData)

    def getParent(self):
        return self.parentItem

# The Tree-like Model
class TreeClass(QtCore.QAbstractItemModel):
    def __init__(self, parent = None, data = []):
        super(TreeClass, self).__init__(parent)
        self.root_node = TreeItem(data = data)

    def getItem(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
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
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.getParent()

        if parentItem == self.root_node:
            return QModelIndex()

        return self.createIndex(parentItem.ChildIndexSelf(), 0, parentItem)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.root_node
        else:
            parentItem = parent.internalPointer()

        return parentItem.countChildren()

    def columnCount(self, parent = QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().DataLength()
        else:
            return self.root_node.DataLength()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_node.getData(section)
        return None

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        node = self.getItem(index)
        return node.getData(index.column())

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
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
        node = TreeItem(data = data, parent = parent)
        parent.appendChild(node)

    def flags(self, index):
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