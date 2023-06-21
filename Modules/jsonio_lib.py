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

import json
import jsonschema
from jsonschema import validate

from Modules.ModifiedTreeModel import ModifiedTreeClass as TreeClass
from Modules.TreeItem import TreeItem

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
        lg.error(err)
        return 1
    except jsonschema.exceptions.SchemaError:
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
    except json.decoder.JSONDecodeError as err:
        lg.error("[jsonio_lib.validator_vars/ERROR]: JSON string could not be parsed!")
        lg.error(err)
        return -1
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
    except json.JSONDecodeError:
        lg.error("[jsonio_lib.decode_function/ERROR]: JSON could not be parsed into Python representation!")
        return -1
    except OSError:
        lg.error("[jsonio_lib.decode_function/ERROR]: JSON is not accessible anymore!")
        return -999
    return result


def schema_to_py_gen(decoded_schema, mode: str = "keys"):
    """
    A function generating a blank JSON-like python structure from the schema.

    Args:
        decoded_schema (dict): a parsed JSON schema, represented as a nested dictionary
        mode (str): The mode decides which tree is returned - "keys", "meta"

    Returns:
        dict: a nested dictionary representation of a JSON document, generated from the schema
    """
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "array":  # the value is a stub, is to be handled, when integrated to the model
                    if mode == "keys":
                        return_dict[element] = []
                    elif mode == "meta":
                        return_dict[element] = decoded_schema["properties"][element]
                    else:
                        return_dict[element] = decoded_schema["properties"][element][mode]
                case "object":
                    return_dict[element] = schema_to_py_gen(decoded_schema["properties"][element], mode)
                case _:
                    match mode:
                        case "keys":
                            if "default" in decoded_schema["properties"][element]:
                                return_dict[element] = decoded_schema["properties"][element]["default"]
                            else:
                                return_dict[element] = ""
                        case "meta":
                            return_dict[element] = decoded_schema["properties"][element]
                        case _:
                            return_dict[element] = decoded_schema["properties"][element][mode]
        except KeyError as err:
            lg.debug(err)
            lg.critical("[jsonio_lib.schema_to_py_gen/CRITICAL]: Skipping element: " + element + ", because of missing"
                        + " \"type\"-tag. JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


def py_to_tree(input_dict: dict, meta_dict: dict, return_tree) -> TreeClass:
    """
    takes a dict generated either from a schema or a JSON and a reference dict from a schema and builds the
    tree model needed for the TreeView. Inserts errors, if schema does not fit JSON document.

    Args:
        input_dict (dict): the parsed JSON document. If a new JSON is created, this shall be empty.
        meta_dict(dict): the dictionary holding additional information extracted from the schema
        return_tree (TreeClass): An empty QAbstractItemModel-based tree

    Returns:
        TreeClass: An QAbstractItemModel-based tree containing all needed information for the UI
    """
    incrementor = 0
    for element in input_dict:
        try:
            if element not in meta_dict:
                raise KeyError("[jsonio_lib.py_to_tree/ERROR]: Element not in Schema Definition.")
            if (type(input_dict[element]) is not dict) and (type(input_dict[element]) is not list):
                temp_value = str(input_dict[element])
                if type(input_dict[element]) is list:
                    temp_value = temp_value.replace("'", "")
                return_tree.add_node(parent = return_tree.root_node, data = [
                    element,
                    meta_dict[element]["title"],
                    temp_value,
                    meta_dict[element]["type"],
                    meta_dict[element]["description"]
                ],
                    metadata = meta_dict[element]
                )
            else:
                if type(input_dict[element]) is dict:
                    return_tree.add_node(parent = return_tree.root_node,
                                         data = [element, '', '', 'object', ''])
                    part_tree = py_to_tree(input_dict[element],
                                           meta_dict[element],
                                           return_tree = TreeClass(data = ["K", "Ti", "V", "Ty", "D"]))
                    for node in part_tree.root_node.childItems:
                        node.parentItem = return_tree.root_node.retrieve_child_by_index(incrementor)
                        return_tree.root_node.retrieve_child_by_index(incrementor).append_child(node)
                else:
                    return_tree.add_node(parent = return_tree.root_node,
                                         data = [
                                             element,
                                             meta_dict[element]["title"],
                                             '',
                                             meta_dict[element]["type"],
                                             meta_dict[element]["description"],
                                         ],
                                         metadata = meta_dict[element]
                                         )
                    if len(input_dict[element]) > 0:
                        for item in input_dict[element]:
                            if type(item) is not dict:
                                return_tree.root_node.last_child().append_child(
                                    TreeItem(
                                        parent = return_tree.root_node.last_child(),
                                        data = ['', '', str(item), 'string', 'Array Item']
                                    )
                                )
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
                part_tree = py_to_tree(input_dict[element], {},
                                       return_tree=TreeClass(data=["K", "Ti", "V", "Ty", "D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieve_child_by_index(incrementor)
                    return_tree.root_node.retrieve_child_by_index(incrementor).append_child(node)
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
            value = element.get_data(2)
            value_type = element.get_data(3)
            if value == '' and value_type != 'array':
                return_dict[element.get_data(0)] = value
            elif value == '' and value_type == 'array':
                return_dict[element.get_data(0)] = []
            else:
                match value_type:
                    case "integer":
                        return_dict[element.get_data(0)] = int(value)
                    case "number":
                        return_dict[element.get_data(0)] = float(value)
                    case "boolean":
                        return_dict[element.get_data(0)] = bool(value)
                    case "array":
                        return_dict[element.get_data(0)] = []
                    case _:
                        return_dict[element.get_data(0)] = value
        else:
            if element.get_data(3) == 'object':
                return_dict[element.get_data(0)] = tree_to_py(element.childItems)
            else:
                tempList = []
                for child in element.childItems:
                    if type(child.get_data(3)) != "object":
                        tempList.append(child.get_data(2))
                return_dict[element.get_data(0)] = tempList
    return return_dict
# ----------------------------------------
# Execution
# ----------------------------------------


if __name__ == "__main__":

    lg.info("Don't run me directly, I just provide some functions.")
    schema = decode_function("../Schemas/default.json")
    blank_frame = schema_to_py_gen(schema)
    type_frame = schema_to_py_gen(schema, "type")
    descr_frame = schema_to_py_gen(schema, "description")
    title_frame = schema_to_py_gen(schema, "title")
    meta_frame = schema_to_py_gen(schema, "meta")
    test_tree1 = py_to_tree(blank_frame, type_frame, descr_frame, title_frame, TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))
    test_tree2 = py_to_tree(blank_frame, meta_frame, TreeClass(data=["Schema Key", "Key Title", "Value", "Type", "Description"]))
    print("success!")