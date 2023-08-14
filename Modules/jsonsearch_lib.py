# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Search Functions and Components
# author: N. Plathe
# ----------------------------------------
"""
Provides functionality around indexing directories and searching inside JSON documents.
"""
# ----------------------------------------
# Music recommendation (albums):
# Knorkator - Sieg der Vernunft
# ----------------------------------------
# Libraries
# ----------------------------------------
# system imports
import logging as lg
import regex
import os
import json
import jsonschema
from jsonschema import validate
from PySide6.QtWidgets import QMessageBox, QWidget

# custom imports
from Modules.deploy_files import save_index, save_main_index

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

# WATCHDOG FUNCTION
def watchdog(script_dir, main_index):
    """
    The watchdog function is supposed to be called every other intervall of time to check all indexes of the tool

    Args:
        script_dir (str): The directory in which the tool is executed
        main_index (dict): The dictionary holding all indexes
    """
    selection_list = list(main_index.keys())
    selection_list.remove("cur_index")
    for i in selection_list:
        check_index(script_dir, i, main_index)

# SCHEMA MATCHER FUNCTIONS
def schema_matching_search(index, schema, script_dir):
    """
    Takes an index and matches all entries against the selected schema. Non-compliant entries are omitted.

    Args:
        index (list): the index list holding all paths of JSON documents
        schema (str): the file name of the schema.
        script_dir (str): The directory in which the tool is executed

    Returns:
        list: the new index containing all retained entries
    """
    lg.info("==========\nSCHEMA MATCHING SEARCH INDEX\n==========")
    lg.info("Matching against schema: " + schema)
    lg.info("----------")
    return_index = []
    for i in index:
        try:
            validate(
                instance=json.load(open(i, encoding = "utf8")),
                schema=json.load(open(os.path.join(script_dir, "Schemas", schema), encoding = "utf8"))
            )
            return_index.append(i)
        except UnicodeDecodeError as err:
            lg.error(i)
            lg.error(err)
            lg.error("[jsonsearch_lib.schema_matching_search/ERROR]: The JSON file cannot be decoded properly" +
                     " because it seems to use a different charset than expected.")
            lg.error("----------")
        except json.decoder.JSONDecodeError as err:
            lg.error(i)
            lg.error(err)
            lg.error("[jsonsearch_lib.schema_matching_search/ERROR]: Invalid JSON structure. Skipping!")
            lg.error("----------")
        except jsonschema.ValidationError as err:
            lg.info(i)
            lg.info(err.message)
            lg.info(err.schema_path)
            lg.info("[jsonsearch_lib.schema_matching_search/INFO]: JSON not valid against schema.")
            lg.info("----------")
        except jsonschema.SchemaError as err:
            lg.critical(err)
            lg.critical("[jsonsearch_lib.schema_matching_search/CRITICAL]: The schema is invalid!")
            QMessageBox(
                QWidget(),
                "[jsonsearch_lib.schema_matching_search/CRITICAL]",
                "[jsonsearch_lib.schema_matching_search/CRITICAL]: The schema does not validate against ." +
                "its metaschema. Please check your selected schema!"
            )
            break
    return return_index


# VALUE SEARCH
def f_search(search_index, search_dict):
    """
        A flat search algorithm for values on a regular expression basis

        Args:
            search_index: the list of the index that shall be searched within
            search_dict: a dictionary containing key-value-pairs to be searched for

        Returns:
            list: the new index containing all retained entries
        """
    copy_index = search_index.copy() # because we need to avoid modifying the original list
    result_list = []
    lg.info("==========\nFLAT SEARCH\n==========")
    try:
        for i in search_index: # for each element in the original handed over list...
            lg.info("reading: " + i)
            try: # ... open the file ...
                json_file = json.load(open(i, encoding = "utf8"))
                if json_file is None:
                    raise json.decoder.JSONDecodeError("Content of JSON file is Null.", i, 0)
            except json.decoder.JSONDecodeError as err:
                lg.error(err)
                lg.error("[jsonsearch_lib.f_search/ERROR]: JSON file invalid. Skipping!")
                json_file = {}
            except UnicodeDecodeError as err:
                lg.error(err)
                lg.error("[jsonsearch_lib.f_search/ERROR]: The JSON file cannot be decoded properly" +
                         " because it seems to use a different charset than expected. Skipping!")
                json_file = {}
            check_list = {} # ... flatten it ...
            check_list = dict_flatten_dict(json_file, check_list)
            for j in search_dict.keys(): # ... then match the elements to search against
                if i not in copy_index: # Skip, if already eliminated
                    break
                lg.info("----------")
                lg.info("Current Search Key: " + j)
                lg.info("Current Search Term: " + str(search_dict[j]))
                lg.info("----------")
                comp_str = regex.compile(regex.escape(str(search_dict[j])))
                for k in list(check_list.keys()):
                    if check_list[k] == "":
                        del check_list[k]
                for l in list(check_list.keys()):
                    if l == j and not regex.search(comp_str, str(check_list[l])):
                        copy_index.remove(i)
                        lg.debug("\nValue does not match search value for given key.\nRemoved: " + i)
                if j not in list(check_list.keys()):
                    copy_index.remove(i)
                    lg.debug("\nGiven key not present or value for given key was empty.\nRemoved: " + i)
        result_list = copy_index
    except (regex.error, OSError, AttributeError) as err:
        lg.error(err)
        if isinstance(err, regex.error):
            msg = "Regex Error: At least one search term could not be compiled into a regular expression."
        elif isinstance(err, OSError):
            msg = "Operating System Error: JSON could not be inspected for Keyword search."
        else:
            msg = "Please select an index for search first."
        QMessageBox.critical(
            QWidget(),
            "[jsonsearch_lib.f_search/ERROR]",
            msg
        )
    return result_list


def dict_flatten_dict(target_dict, flat_dict = None):
    """
    a recursive structural flattener to simplify a search

    Args:
        target_dict (dict): the dictionary to be flattened
        flat_dict (dict): the flat dictionary to use. Might be filled already.

    Returns:
        dict: the (partly) flattened dictionary
    """
    if flat_dict is None:
        flat_dict = {}
    if type(target_dict) is dict:
        for pair in list(target_dict):
            str_name = pair
            if type(target_dict[str_name]) is not dict and type(target_dict[str_name]) is not list:
                alt_name = str_name
                iterator = 0
                try:
                    while flat_dict[alt_name]:
                        alt_name = str_name + str(iterator)
                        iterator += 1
                    flat_dict[alt_name] = target_dict[str_name]
                    del target_dict[str_name]
                except KeyError as err:
                    flat_dict[alt_name] = target_dict[str_name]
                    del target_dict[str_name]
                    continue
            else:
                iterator = 0
                if type(target_dict[str_name]) is dict:
                    flat_dict = dict_flatten_dict(target_dict[str_name], flat_dict)
                else:
                    for element in target_dict[str_name]:
                        if type(element) is not dict:
                            alt_name = str_name + str(iterator)
                            iterator += 1
                            flat_dict[alt_name] = element
                del target_dict[str_name]
    return flat_dict

# INDEXER FUNCTION
def start_index(script_dir, path, index_dict, show_boxes = True):
    """
    Creates or overwrites an index file for a given path, containing only paths to JSON documents.

    Args:
        script_dir (str): The directory in which the tool is executed
        path (str): the path to be indexed
        index_dict (dict): the main index
        show_boxes (bool): a parameter to control whetever errors and warnings shall be displayed as message services.
    """
    lg.info("==========\nINDEXER\n==========")
    indexed_files = []
    try:
        if not os.path.exists(path):
            raise OSError
        lg.info("jsonsearch_lib.start_index/INFO] start indexing at:")
        lg.info(path)
        if show_boxes:
            QMessageBox.information(
                QWidget(),
                "[jsonsearch_lib.start_index/INFO]",
                "Start indexing. This can take a while..."
            )
        for root, dirs, files in os.walk(path, topdown = False):
            for name in files:
                if regex.match(r"^.*\.json$", name):
                    indexed_files.append(os.path.normpath(os.path.join(root, name)))
        if len(indexed_files) == 0:
            lg.info("[jsonsearch_lib.start_index/INFO]: No JSON files found. Index is empty.")
            if show_boxes:
                QMessageBox.information(
                    QWidget(),
                    "[jsonsearch_lib.start_index/INFO]",
                    "No JSON files found. Index is empty."
                )
        else:
            if path in index_dict:
                cur_index = index_dict[path]
            else:
                index_dict["cur_index"] += 1
                cur_index = index_dict["cur_index"]
                index_dict[path] = cur_index
                save_main_index(script_dir, index_dict)
            save_index(script_dir, indexed_files, cur_index)
        lg.info("jsonsearch_lib.start_index/INFO] Indexing finished.")
        if show_boxes:
            QMessageBox.information(
                QWidget(),
                "[jsonsearch_lib.start_index/INFO]",
                "Indexing finished!"
            )
    except OSError as err:
        message2 = "[jsonsearch_lib.start_index/ERROR] Directory (or one of its subdirectories) is not accessible!"
        lg.debug(err)
        lg.error(message2)
        if show_boxes:
            QMessageBox.information(
                QWidget(),
                "[jsonsearch_lib.start_index/ERROR]",
                message2
            )

def check_index(script_dir, path, index_dict):
    """
    checks a path for recent changes and updates the index accordingly

    Args:
        script_dir (str): The directory in which the tool is executed
        path (str): the path to be indexed
        index_dict (dict): the main index
    """
    try:
        if os.path.isdir(os.path.normpath(path)) and index_dict[path]:
            index_nr = str(index_dict[path])
            index_path = os.path.join(script_dir, "Indexes", "index" + index_nr + ".json")

            last_change_json = os.path.getmtime(index_path)
            last_change_dir = os.path.getmtime(path)
            changed = False
            if last_change_json < last_change_dir:
                changed = True

            index = json.load(open(index_path, encoding = "utf8"))
            lg.info("[jsonsearch_lib.check_index/INFO]: Retrieved index of " + path + ".")
            i = 0
            while not changed:
                i = i + 1
                if i >= len(index["files"]):
                    break
                if not os.path.isfile(index["files"][i]):
                    changed = True
                    break
            if changed:
                message = "[jsonsearch_lib.check_index/WARN]: One or more indexed files are missing or changed."
                lg.warning(message)
                start_index(script_dir, path, index_dict, False)
            else:
                message = "[jsonsearch_lib.check_index/INFO]: No changes of already existing files detected."
                lg.info(message)
    except OSError as err:
        lg.debug(err)
        lg.error("[jsonsearch_lib.check_index/ERROR] Index file missing oder inaccessible.")
    except KeyError as err:
        lg.debug(err)
        lg.error("[jsonsearch_lib.checkIndex/ERROR]: No valid index from list selected!")