# ----------------------------------------
# pyJSON Converter + GUI jsonio_lib module
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

# The validator function shall wrap around json.load and validate a JSON file against a Schema file
def validator_files(json_path, json_schema_path):
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path)
        loaded_json = open(json_path)
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


# Similarly to validator_files, but instead with a string representation of the JSON
def validator_vars(json_str, json_schema_path):
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path)
        ds_json = json.loads(json_str)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        lg.error("[jsonio_lib.validator_vars/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        lg.error("[jsonio_lib.validator_vars/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        lg.error("[jsonio_lib.validator_vars/ERROR]: Schema is not accessible anymore!")
        return -999
    lg.info("[jsonio_lib.validator_vars/INFO]: Validation of JSON successful!")
    return 0


# Wrapper for the JSONDecoder function
def decode_function(json_path):
    lg.info("\n----------\nReading " + json_path + "\n----------")
    try:
        loaded_json = open(json_path)
        result = json.load(loaded_json, cls=json.JSONDecoder)
    except json.JSONDecodeError as err:
        lg.error("[jsonio_lib.decode_function/ERROR]: JSON could not be parsed into Python representation!")
        return {"Error": "Something has gone wrong, the JSON was not parsed properly!"}
    except OSError:
        lg.error("[jsonio_lib.decode_function/ERROR]: JSON is not accessible anymore!")
        return -999
    return result


# A function generating a blank JSON-like python structure from the schema.
def schema_to_py_gen(decoded_schema):
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "string":
                    return_dict[element] = ""
                case "array":
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
            lg.critical("[jsonio_lib.schema_to_py_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag"+
                  ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


# generates a reference containing the description of every field in the schema
def schema_to_ref_gen(decoded_schema):
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":
                    return_dict[element] = schema_to_ref_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["description"]
        except KeyError as err:
            lg.critical("[jsonio_lib.schema_to_ref_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag"+
                  ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict

def schema_to_type_gen(decoded_schema):
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":
                    return_dict[element] = schema_to_type_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["type"]
        except KeyError as err:
            lg.critical(
                "[jsonio_lib.schema_to_type_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag" +
                ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict

def schema_to_title_gen(decoded_schema):
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":
                    return_dict[element] = schema_to_title_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["title"]
        except KeyError as err:
            lg.critical(
                "[jsonio_lib.schema_to_title_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag" +
                ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict

# py_to_tree takes a dict generated either from a schema or a JSON and a reference dict from a schema and builds the
# tree model needed for the TreeView
def py_to_tree(input_dict: dict, type_dict: dict, title_dict: dict, reference_dict: dict, return_tree) -> TreeClass:
    incrementor = 0
    for element in input_dict:
        try:
            if not element in reference_dict:
                raise KeyError("[jsonio_lib.py_to_tree/INFO]: Element not in Schema Definition.")
            if type(input_dict[element]) is not dict:
                return_tree.add_node(parent = return_tree.root_node, data =
                [
                    element,
                    title_dict[element],
                    str(input_dict[element]),
                    type_dict[element],
                    reference_dict[element]
                ])
            else:
                return_tree.add_node(parent=return_tree.root_node,
                                     data=[element, '', '', '', ''])
                part_tree = py_to_tree(input_dict[element], type_dict[element], title_dict[element], reference_dict[element],
                                       return_tree=TreeClass(data=["K","Ti", "V", "Ty", "D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieveChildbyIndex(incrementor)
                    return_tree.root_node.retrieveChildbyIndex(incrementor).appendChild(node)
            incrementor += 1
        except KeyError as err:
            lg.warning("[jsonio_lib.py_to_tree/INFO]: Key " + element +" may not be present in Schema. Switch to erroneous description")
            if type(input_dict[element]) is not dict:
                return_tree.add_node(parent = return_tree.root_node, data = [element, 'Erroneous Title', str(input_dict[element]), 'string', 'Schema does not match JSON structure! Type Validation will not work!'])
            else:
                return_tree.add_node(parent=return_tree.root_node,
                                     data=[element, '', '', '',''])
                part_tree = py_to_tree(input_dict[element], {}, {}, {},
                                       return_tree=TreeClass(data=["K","Ti", "V", "Ty", "D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieveChildbyIndex(incrementor)
                    return_tree.root_node.retrieveChildbyIndex(incrementor).appendChild(node)
            incrementor += 1
    return return_tree


# converts the tree back to a nested dict. Descriptions get omitted.
def tree_to_py(array_of_tree_nodes):
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
                    case "array":
                        return_dict[element.getData(0)] = value
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
    lg.info("Ping") # TODO: Remove Breaker Print for Debug

