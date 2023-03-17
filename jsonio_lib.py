# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - IO and Conversion Module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------
import logging
import os
import sys
import regex as re

import json
import jsonschema
from jsonschema import validate

from schema_model import TreeClass, TreeItem

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

# logger config
lg = logging.getLogger(__name__)
lg.setLevel("DEBUG")


def validator_files(json_path, json_schema_path):
    """
    The validator function shall wrap around json.load and validate a JSON file against a Schema file.

    Args:
        json_path (str): path to the JSON document
        json_schema_path (str): path to the JSON schema

    Returns:
        int: 0 for success, 1 for failed validation, 2 for invalid schema, -999 for IO issues.
    """
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path, encoding = "utf8")
        loaded_json = open(json_path, encoding = "utf8")
        ds_json = json.load(loaded_json)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        lg.error("[jsonio_lib.validator_files/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        lg.error("[jsonio_lib.validator_files/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        lg.error("[jsonio_lib.validator_files/ERROR]: Either JSON or Schema is not accessible anymore!")
        return -999
    lg.info("[jsonio_lib.validator_files/INFO]: Validation of JSON successful!")
    return 0


def validator_vars(json_str, json_schema_path):
    """
    Similarly to validator_files, but instead with a string representation of the JSON

    Args:
        json_str (str): String representation of a JSON document
        json_schema_path (str): path to the JSON schema

    Returns:
        int: 0 for success, 1 for failed validation, 2 for invalid schema, -999 for IO issues.
    """
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path, encoding = "utf8")
        ds_json = json.loads(json_str)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        lg.error("[jsonio_lib.validator_vars/ERROR]: JSON is not valid against selected Schema!")
        lg.error(err)
        return 1
    except jsonschema.exceptions.SchemaError as err:
        lg.error("[jsonio_lib.validator_vars/ERROR]: The JSON schema is not valid against its selected meta schema!")
        lg.error(err)
        return 2
    except OSError as err:
        lg.error("[jsonio_lib.validator_vars/ERROR]: Schema is not accessible anymore!")
        lg.error(err)
        return -999
    lg.info("[jsonio_lib.validator_vars/INFO]: Validation of JSON successful!")
    return 0


#
def decode_function(json_path):
    """
    Wrapper for the JSONDecoder function.
    TODO: PROPERLY IMPLEMENT ERROR HANDLING

    Args:
        json_path (str): Path to the JSON document

    Returns:
        dict: the parsed JSON document
    """
    lg.info("\n----------\nReading " + json_path + "\n----------")
    try:
        loaded_json = open(json_path, encoding = "utf8")
        result = json.load(loaded_json, cls=json.JSONDecoder)
    except json.JSONDecodeError as err:
        lg.error("[jsonio_lib.decode_function/ERROR]: JSON could not be parsed into Python representation!")
        return -1
    except OSError:
        lg.error("[jsonio_lib.decode_function/ERROR]: JSON is not accessible anymore!")
        return -999
    return result


def schema_to_py_gen(decoded_schema):
    """
    A function generating a blank JSON-like python structure from the schema.

    Args:
        decoded_schema (dict): a parsed JSON schema, represented as a nested dictionary

    Returns:
        dict: a nested dictionary representation of a JSON document, generated from the schema
    """
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "string":
                    if "default" in decoded_schema["properties"][element]:
                        return_dict[element] = decoded_schema["properties"][element]["default"]
                    else:
                        return_dict[element] = ""
                case "array":  # TODO: ARRAYS NEED TO BE HANDLED DIFFERENTLY, E.G. ARRAYS WITH OBJECTS
                    return_dict[element] = []
                case "number":
                    return_dict[element] = float("0.0")
                case "integer":
                    return_dict[element] = 0
                case "boolean":
                    return_dict[element] = False
                case "object":
                    return_dict[element] = schema_to_py_gen(decoded_schema["properties"][element])
        except KeyError as err:
            lg.critical("[jsonio_lib.schema_to_py_gen/CRITICAL]: Skipping element: " + element + ", because of missing"
                        + " \"type\"-tag. JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


# generates a reference containing the description of every field in the schema
def schema_to_ref_gen(decoded_schema):
    """
    Similar to schema_to_py_gen, but return value is a nested dict containing descriptions for
    each key present in the schema.

    Args:
        decoded_schema (dict): a parsed JSON schema, represented as a nested dictionary

    Returns:
        dict: a nested dictionary containing descriptions for utilised keys inside the schema
    """
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":  # TODO: ARRAYS NEED TO BE HANDLED DIFFERENTLY, E.G. ARRAYS WITH OBJECTS
                    return_dict[element] = schema_to_ref_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["description"]
        except KeyError as err:
            lg.critical("[jsonio_lib.schema_to_ref_gen/CRITICAL]: Skipping element: " + element +
                        ", because of missing \"type\"-tag" +
                        ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


def schema_to_type_gen(decoded_schema):
    """
    Similar to schema_to_py_gen, but return value is a nested dict containing the type of
    each key present in the schema.

    Args:
        decoded_schema (dict): a parsed JSON schema, represented as a nested dictionary

    Returns:
        dict: a nested dictionary containing types of utilised keys inside the schema
    """
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":  # TODO: ARRAYS NEED TO BE HANDLED DIFFERENTLY, E.G. ARRAYS WITH OBJECTS
                    return_dict[element] = schema_to_type_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["type"]
        except KeyError as err:
            lg.critical(
                "[jsonio_lib.schema_to_type_gen/CRITICAL]: Skipping element: " + element +
                ", because of missing \"type\"-tag" +
                ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


def schema_to_title_gen(decoded_schema):
    """
    Similar to schema_to_py_gen, but return value is a nested dict containing the title of
    each key present in the schema.

    Args:
        decoded_schema (dict): a parsed JSON schema, represented as a nested dictionary

    Returns:
        dict: a nested dictionary containing title of utilised keys inside the schema
    """
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":  # TODO: ARRAYS NEED TO BE HANDLED DIFFERENTLY, E.G. ARRAYS WITH OBJECTS
                    return_dict[element] = schema_to_title_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["title"]
        except KeyError as err:
            lg.critical(
                "[jsonio_lib.schema_to_title_gen/CRITICAL]: Skipping element: " + element +
                ", because of missing \"type\"-tag" +
                ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


def py_to_tree(input_dict: dict, type_dict: dict, title_dict: dict, reference_dict: dict, return_tree) -> TreeClass:
    """
    takes a dict generated either from a schema or a JSON and a reference dict from a schema and builds the
    tree model needed for the TreeView. Inserts errors, if schema does not fit JSON document.

    Args:
        input_dict (dict): the parsed JSON document. If a new JSON is created, this shall be empty.
        type_dict (dict): a dict containing the type for each key
        title_dict (dict): a dict containing the title for each key
        reference_dict (dict): a dict containing the description for each key
        return_tree (TreeClass): An empty QAbstractItemModel-based tree

    Returns:
        TreeClass: An QAbstractItemModel-based tree containing all needed information for the UI
    """
    incrementor = 0
    for element in input_dict:
        try:
            if element not in reference_dict:
                raise KeyError("[jsonio_lib.py_to_tree/ERROR]: Element not in Schema Definition.")
            if type(input_dict[element]) is not dict:
                temp_value = str(input_dict[element])
                if type(input_dict[element]) is list:
                    temp_value = temp_value.replace("'", "")
                return_tree.add_node(parent = return_tree.root_node, data = [
                    element,
                    title_dict[element],
                    temp_value,
                    type_dict[element],
                    reference_dict[element]
                ])
            else:
                return_tree.add_node(parent = return_tree.root_node,
                                     data = [element, '', '', '', ''])
                part_tree = py_to_tree(input_dict[element],
                                       type_dict[element],
                                       title_dict[element],
                                       reference_dict[element],
                                       return_tree = TreeClass(data = ["K", "Ti", "V", "Ty", "D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieveChildbyIndex(incrementor)
                    return_tree.root_node.retrieveChildbyIndex(incrementor).appendChild(node)
            incrementor += 1
        except (KeyError, TypeError) as err:

            titleStr = ""
            descrStr = ""
            if isinstance(err, KeyError):
                lg.error("[jsonio_lib.py_to_tree/ERROR]: KeyError: Key " + element +
                         " may not be present in Schema. Switch to erroneous description.")
                titleStr = "KeyError"
                descrStr = "The key is not present in the current hiearchy level of the schema."
            if isinstance(err, TypeError):
                lg.error("[jsonio_lib.py_to_tree/ERROR]: " + str(err))
                lg.error("[jsonio_lib.py_to_tree/ERROR]: TypeError: Structural missmatch detected. " +
                         "Switch to erroneous description.")
                titleStr = "ValueError"
                descrStr = "Because of a structural missmatch, data that was read from the schema " +\
                           "is invalid."
            if type(input_dict[element]) is not dict:
                return_tree.add_node(parent = return_tree.root_node,
                                     data = [element, titleStr,
                                             str(input_dict[element]), 'string',
                                             descrStr])
            else:
                return_tree.add_node(parent = return_tree.root_node,
                                     data = [element, '', '', '', ''])
                part_tree = py_to_tree(input_dict[element], {}, {}, {},
                                       return_tree=TreeClass(data=["K", "Ti", "V", "Ty", "D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieveChildbyIndex(incrementor)
                    return_tree.root_node.retrieveChildbyIndex(incrementor).appendChild(node)
            incrementor += 1
    return return_tree


def tree_to_py(array_of_tree_nodes):
    """
    converts the tree back to a nested dict. Only keys and values are retained.

    Args:
        array_of_tree_nodes (iterable): An iterable list of Nodes based on QAbstractItem. Use the childItems of the root
            node for the entire tree...

    Returns:
        dict: a nested directory representation of the JSON document.
    """
    return_dict = {}
    for element in array_of_tree_nodes:
        if len(element.childItems) == 0:
            value = element.getData(2)
            value_type = element.getData(3)
            if value == '':
                return_dict[element.getData(0)] = value
            else:
                match value_type:
                    case "integer":
                        return_dict[element.getData(0)] = int(value)
                    case "number":
                        return_dict[element.getData(0)] = float(value)
                    case "boolean":
                        return_dict[element.getData(0)] = bool(value)
                    case "array":  # TODO: ARRAYS NEED TO BE HANDLED DIFFERENTLY, E.G. ARRAYS WITH OBJECTS
                        temp_value = value.replace("[", "")
                        temp_value = temp_value.replace("]", "")
                        temp_value = temp_value.replace(" ", "")
                        temp_arr = re.split(",", temp_value)
                        return_dict[element.getData(0)] = temp_arr
                    case _:
                        return_dict[element.getData(0)] = value
        else:
            return_dict[element.getData(0)] = tree_to_py(element.childItems)
    return return_dict
# ----------------------------------------
# Execution
# ----------------------------------------


if __name__ == "__main__":

    lg.info("Don't run me directly, I just provide some functions.")
    schema = decode_function("Schemas/default.json")
    blank_frame = schema_to_py_gen(schema)
    type_frame = schema_to_type_gen(schema)
    descr_frame = schema_to_ref_gen(schema)
    title_frame = schema_to_title_gen(schema)
