# ----------------------------------------
# Class file for the TreeItem class, which holds data in the TreeModel.
# Mostly feature complete implementation of examples found in the Qt documentation
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Harpyie - Blutban
# ----------------------------------------
# Libraries
# ----------------------------------------
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
    def __init__(self, parent = None, data = None):
        if data is None:
            data = []
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

    def lastChild(self):
        """
        retrieves the last child of a node.

        Returns:
            TreeItem: the last child of the child items.
        """
        return self.childItems[-1] if self.childItems else None

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

    def insertChildren(self, position: int, count: int, columns: int) -> bool:
        """
        Inserts child nodes into the nodes child list.

        Args:
            position (int): position at which children get inserted
            count (int): amount of children to be inserted
            columns (int): amount of columns in the model

        Returns:
            boolean: A value representing whetever insertion was a success.
        """
        if position < 0 or position > len(self.childItems):
            return False

        for row in range(count):
            data = [None] * columns
            item = TreeItem(data.copy(), self)
            self.childItems.insert(position, item)
        return True

    def insertColumns(self, position: int, columns: int) -> bool:
        """
        Recursively inserts new columns into the model

        Args:
            position (int): current position to insert
            columns (int): amount of columns to insert

        Returns:
            boolean: A value representing whetever insertion was a success.
        """
        if position < 0 or position > len(self.childItems):
            return False

        for column in range(columns):
            self.itemData.insert(position, None)

        for child in self.childItems:
            child.insertColumns(position, columns)

        return True

    def removeChildren(self, position: int, count: int) -> bool:
        """
        Removes child nodes from the given position

        Args:
            position (int): the position given at where nodes shall be removed
            count (int): amount of nodes that shall be removed

        Returns:
            boolean: A value representing whetever removal was a success.
        """
        if position < 0 or position + count > len(self.childItems):
            return False

        for row in range(count):
            self.childItems.pop(position)

        return True

    def removeColumns(self, position: int, columns: int) -> bool:
        """
        Recursively removes columns from the model

        Args:
            position (int): The position of the first column to be removed
            columns (int): Amount of columns to be removed

        Returns:
            boolean: A value representing whetever removal was a success.
        """
        if position < 0 or position + columns > len(self.itemData):
            return False

        for column in range(columns):
            self.itemData.pop(position)

        for child in self.childItems:
            child.removeColumns(position, columns)

        return True

    def __repr__(self) -> str:
        """
        get a representation of the instance when called directly

        Returns:
            str: information about the instance
        """
        result = f"<treeitem.TreeItem at 0x{id(self):x}"
        for d in self.itemData:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self.childItems)} children>"
        return result