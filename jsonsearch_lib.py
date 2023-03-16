# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Search Functions and Components
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Knorkator - Sieg der Vernunft
# ----------------------------------------
# Libraries
# ----------------------------------------
# system imports
import logging as lg
import tkinter as tk
import tkinter.messagebox
import regex as re
import os
import json
import jsonschema
from jsonschema import validate

# custom imports
from deploy_files import saveIndex, saveMainIndex

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

# WATCHDOG FUNCTION
def watchdog(script_dir, mainIndex):
    """
    The watchdog function is supposed to be called every other intervall of time to check all indexes of the tool

    Args:
        script_dir (str): The directory in which the tool is executed
        mainIndex (dict): The dictionary holding all indexes

    Returns:

    """
    selection_list = list(mainIndex.keys())
    selection_list.remove("cur_index")
    for i in selection_list:
        checkIndex(script_dir, i, mainIndex)

# SCHEMA MATCHER FUNCTIONS
def schemaMatchingSearch(index, schema, script_dir):
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
            lg.error("[jsonsearch_lib.schemaMatchingSearch/ERROR]: The JSON file cannot be decoded properly" +
                     " because it seems to use a different charset than expected.")
            lg.error("----------")
        except json.decoder.JSONDecodeError as err:
            lg.error(i)
            lg.error(err)
            lg.error("[jsonsearch_lib.schemaMatchingSearch/ERROR]: Invalid JSON structure. Skipping!")
            lg.error("----------")
        except jsonschema.ValidationError as err:
            lg.info(i)
            lg.info(err.message)
            lg.info(err.schema_path)
            lg.info("[jsonsearch_lib.schemaMatchingSearch/INFO]: JSON not valid against schema.")
            lg.info("----------")
        except jsonschema.SchemaError as err:
            lg.critical(err)
            lg.critical("[jsonsearch_lib.schemaMatchingSearch/CRITICAL]: The schema is invalid!")
            tk.messagebox.showerror(
                title="[jsonsearch_lib.schemaMatchingSearch/CRITICAL]",
                message="[jsonsearch_lib.schemaMatchingSearch/CRITICAL]: The schema does not validate against ." +
                        "its metaschema. Please check your selected schema!"
            )
            break
    return return_index


# VALUE SEARCH
def fSearch(index, searchDict):
    """
    A flat search algorithm for values on a regular expression basis

    Args:
        index: the list of the index that shall be searched within
        searchDict: a dictionary containing key-value-pairs to be searched for

    Returns:
        list: the new index containing all retained entries
    """
    resultList = []
    lg.info("==========\nFLAT SEARCH\n==========")
    try:
        for j in searchDict.keys():
            lg.info("----------")
            lg.info("Current Search Key: " + j)
            lg.info("Current Search Term: " + str(searchDict[j]))
            lg.info("----------")
            comp_str = re.compile(str(searchDict[j]))
            for i in index:
                lg.info("reading: " + i)
                try:
                    json_file = json.load(open(i, encoding = "utf8"))
                    if json_file is None:
                        raise json.decoder.JSONDecodeError("Content of JSON file is Null.", i, 0)
                except json.decoder.JSONDecodeError as err:
                    lg.error(err)
                    lg.error("[jsonsearch_lib.fSearchValues/ERROR]: JSON file invalid. Skipping!")
                    json_file = {}
                except UnicodeDecodeError as err:
                    lg.error(err)
                    lg.error("[jsonsearch_lib.fSearchValues/ERROR]: The JSON file cannot be decoded properly" +
                             " because it seems to use a different charset than expected. Skipping!")
                    json_file = {}
                check_list = {}
                check_list = dictFlattenDict(json_file, check_list)
                hit = False
                for k in list(check_list):
                    if re.search(comp_str, str(check_list[k])) and hit is False:
                        if i not in resultList:
                            resultList.append(i)
                            lg.info("Added " + i + " to the result list.")
                        hit = True
    except re.error as err:
        lg.error(err)
        tk.messagebox.showerror(
            title="[jsonsearch_lib.flatSearchIndex/ERROR]",
            message="[jsonsearch_lib.flatSearchIndex/ERROR]: Your regex pattern seems to be invalid."
        )
    except OSError as err:
        lg.error(err)
        tk.messagebox.showerror(
            title="[jsonsearch_lib.flatSearchIndex/ERROR]",
            message="[jsonsearch_lib.flatSearchIndex/ERROR]: JSON could not be inspected for Keyword search."
        )
    except AttributeError as err:
        lg.error(err)
        tk.messagebox.showerror(
            title="[jsonsearch_lib.flatSearchIndex/ERROR]",
            message="[jsonsearch_lib.flatSearchIndex/ERROR]: Please select an index for search first."
        )
    return resultList


def dictFlattenDict(target_dict, flat_dict={}):
    """
    a recursive structural flattener to simplify a search
    TODO: ISSUE WITH ARRAYS

    Args:
        target_dict (dict): the dictionary to be flattened
        flat_dict (dict): the flat dictionary to use. Might be filled already.

    Returns:
        dict: the (partly) flattened dictionary
    """
    if type(target_dict) is dict:
        for pair in list(target_dict):
            str_name = pair
            if type(target_dict[str_name]) is not dict:
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
                flat_dict = dictFlattenDict(target_dict[str_name], flat_dict)
                del target_dict[str_name]
    return flat_dict

# INDEXER FUNCTION
def StartIndex(script_dir, path, index_dict, showBoxes = True):
    """
    Creates or overwrites an index file for a given path, containing only paths to JSON documents.

    Args:
        script_dir (str): The directory in which the tool is executed
        path (str): the path to be indexed
        index_dict (dict): the main index
        showBoxes (bool): a parameter to control whetever errors and warnings shall be displayed as message services.

    Returns:
    """
    lg.info("==========\nINDEXER\n==========")
    indexed_files = []
    try:
        if not os.path.exists(path):
            raise OSError
        lg.info("jsonsearch_lib.StartIndex/INFO] start indexing at:")
        lg.info(path)
        if showBoxes:
            tk.messagebox.showinfo(
                title ="[jsonsearch_lib.StartIndex/INFO]",
                message = "Start indexing. This can take a while..."
            )
        for root, dirs, files in os.walk(path, topdown = False):
            for name in files:
                if re.match("^.*\.json$", name):
                    indexed_files.append(os.path.normpath(os.path.join(root, name)))
        if len(indexed_files) == 0:
            lg.info("[jsonsearch_lib.StartIndex/INFO]: No JSON files found. Index is empty.")
            if showBoxes:
                tk.messagebox.showinfo(
                    title="[jsonsearch_lib.StartIndex/INFO]",
                    message="No JSON files found. Index is empty."
                )
        else:
            if path in index_dict:
                cur_index = index_dict[path]
            else:
                index_dict["cur_index"] += 1
                cur_index = index_dict["cur_index"]
                index_dict[path] = cur_index
                saveMainIndex(script_dir, index_dict)
            saveIndex(script_dir, indexed_files, cur_index)
        lg.info("jsonsearch_lib.StartIndex/INFO] Indexing finished.")
        if showBoxes:
            tk.messagebox.showinfo(
                title ="[jsonsearch_lib.StartIndex/INFO]",
                message = "Indexing finished"
            )
    except OSError as err:
        message2 = "[jsonsearch_lib.StartIndex/ERROR] Directory (or one of its subdirectories) is not accessible!"
        lg.error(err)
        lg.error(message2)
        if showBoxes:
            tk.messagebox.showerror(
                title = "[jsonsearch_lib.StartIndex/ERROR]",
                message = message2
            )

def checkIndex(script_dir, path, index_dict):
    """
    checks a path for recent changes and updates the index accordingly

    Args:
        script_dir (str): The directory in which the tool is executed
        path (str): the path to be indexed
        index_dict (dict): the main index

    Returns:
    """
    try:
        if os.path.isdir(os.path.normpath(path)) and index_dict[path]:
            index_nr = str(index_dict[path])
            index_path = os.path.join(script_dir, "Indexes", "index" + index_nr + ".json")

            lastChangeJSON = os.path.getmtime(index_path)
            lastChangeDir = os.path.getmtime(path)
            changed = False
            if lastChangeJSON < lastChangeDir:
                changed = True

            index = json.load(open(index_path, encoding = "utf8"))
            lg.info("[jsonsearch_lib.checkIndex/INFO]: Retrieved index of " + path + ".")
            i = 0
            while not changed:
                i = i + 1
                if i >= len(index["files"]):
                    break
                if not os.path.isfile(index["files"][i]):
                    changed = True
                    break
            if changed:
                message = "[jsonsearch_lib.checkIndex/WARN]: One or more indexed files are missing or changed."
                lg.warning(message)
                StartIndex(script_dir, path, index_dict, False)
            else:
                message = "[jsonsearch_lib.checkIndex/INFO]: No changes of already existing files detected."
                lg.info(message)
    except OSError as err:
        lg.error(err)
        lg.error("[jsonsearch_lib.checkIndex/ERROR] Index file missing oder inaccessible.")
    except KeyError as err:
        lg.error("[jsonsearch_lib.checkIndex/ERROR]: No valid index from list selected!")

# ----------------------------------------
# Execution
# ----------------------------------------
if __name__ == "__main__":
    lg.info("Don't run me directly, I'm just a module providing search functions.")
