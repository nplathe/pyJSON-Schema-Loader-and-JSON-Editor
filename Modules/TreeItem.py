# ----------------------------------------
# Class file for the TreeItem class, which holds data in the TreeModel.
# Mostly feature complete implementation of examples found in the Qt documentation
# author: N. Plathe
# ----------------------------------------
"""
This class is a simple data structuring class retaining needed information for TreeModel.
"""
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
    def __init__(self, parent = None, data = None, metadata = None):
        if data is None:
            data = []
        if metadata is None:
            metadata = {}
        self.parentItem = parent
        self.itemData = data
        self.itemMetadata = metadata
        self.childItems = []

    # child functions

    def append_child(self, child):
        """
        Adds a child to childItems

        Args:
            child: the child to be added
        """
        self.childItems.append(child)

    def retrieve_child_by_index(self, child_index):
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

    def last_child(self):
        """
        retrieves the last child of a node.

        Returns:
            TreeItem: the last child of the child items.
        """
        return self.childItems[-1] if self.childItems else None

    def child_index_self(self):
        """
        returns the own index if being a child of another node

        Returns:
            int: the own index. Returns 0 if parentItem is None
        """
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0

    def count_children(self):
        """
        returns the length of the list storing the child items

        Returns:
            int: child item count
        """
        return len(self.childItems)

    # data functions

    def set_data_array(self, data):
        """
        Sets or overwrites the entire data list

        Args:
            data (list): the new data to be written
        """
        self.itemData = data

    def set_data(self, data: str, column: int):
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

    def get_data(self, column):
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

    def get_data_array(self):
        """
        fetches the full data of an item

        Returns:
            list: the full data list of the item
        """
        return self.itemData

    def data_length(self):
        """
        retrieves the data length

        Returns:
            int: length of the data list - which equals the amount of columns in the TreeView later
        """
        return len(self.itemData)

    def get_parent(self):
        """
        retrieves the parent

        Returns:
            TreeItem: the parent node
        """
        return self.parentItem

    def insert_children(self, position: int, count: int, columns: int) -> bool:
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

    def insert_columns(self, position: int, columns: int) -> bool:
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
            child.insert_columns(position, columns)

        return True

    def remove_children(self, position: int, count: int) -> bool:
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

    def remove_columns(self, position: int, columns: int) -> bool:
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
            child.remove_columns(position, columns)

        return True

    # metadata functions
    def add_mdata_pair(self, key, value):
        """
        A setter for a key-value pair for metadata.

        Args:
            key (str): the key to set
            value(object): any given value
        """
        self.itemMetadata[key] = value

    def add_metadata(self, dictionary = None):
        """
        Sets or overwrites the metadata dictionary with a copy of the passed dictionary.

        Args:
            dictionary(dict): a dictionary containing all metadata needed for operation
        """
        if dictionary is None:
            self.itemMetadata = {}
        else:
            self.itemMetadata = dictionary.copy()
    def all_metadata(self):
        """
        A helper function to get the full metadata dictionary based on the schema

        Returns: The metadata dictionary.
        """
        return self.itemMetadata

    def get_metadata(self, key = ''):
        """
        Retrieves metadata.

        Args:
            key(str): a key present in the attached metadata

        Returns: Either value, if present or None.

        """
        try:
            if key == '':
                return None
            return self.itemMetadata[key]
        except KeyError as err:
            lg.error("[TreeItem.get_metadata/ERROR]: No key " + key + "present. Returning None.")
            return None

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