# ----------------------------------------
# pyJSON Converter + GUI main module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------

import json
import jsonschema
from jsonschema import validate
from schema_model import TreeClass, TreeItem
import os


# ----------------------------------------
# Variables and Functions
# ----------------------------------------
# The validator function shall wrap around json.load and validate a JSON file against a Schema file

def validator_files(json_path, json_schema_path):
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path)
        loaded_json = open(json_path)
        ds_json = json.load(loaded_json)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        print("[main.validator_files/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        print("[main.validator_files/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        print("[main.validator_files/ERROR]: Either JSON or Schema is not accessible anymore!")
        return -999
    print("[main.validator_files/INFO]: Validation of JSON successful!")
    return 0


# Similarly to validator_files, but instead with a string representation of the JSON
def validator_vars(json_str, json_schema_path):
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path)
        ds_json = json.loads(json_str)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        print("[main.validator_vars/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        print("[main.validator_vars/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        print("[main.validator_vars/ERROR]: Schema is not accessible anymore!")
        return -999
    print("[main.validator_vars/INFO]: Validation of JSON successful!")
    return 0


# Wrapper for the JSONDecoder function
def decode_function(json_path):
    print("----------\nReading " + json_path + "\n----------")
    try:
        loaded_json = open(json_path)
        result = json.load(loaded_json, cls=json.JSONDecoder)
    except json.JSONDecodeError as err:
        print("[main.decode_function/ERROR]: JSON could not be parsed into Python representation!")
        return 2
    except OSError:
        print("[main.decode_function/ERROR]: JSON is not accessible anymore!")
        return -999
    return result


# A function generating a JSON-like python structure from the schema.
def schema_to_py_gen(decoded_schema):
    if decoded_schema == -999 or decoded_schema == 2:
        return {}
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "string":
                    return_dict[element] = ""
                case "array":
                    return_dict[element] = []
                case "number":
                    return_dict[element] = float("NaN")
                case "object":
                    return_dict[element] = schema_to_py_gen(decoded_schema["properties"][element])
        except KeyError as err:
            print("[main.schema_to_py_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag"+
                  ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict

def schema_to_ref_gen(decoded_schema):
    if decoded_schema == -999 or decoded_schema == 2:
        return {}
    return_dict = {}
    for element in decoded_schema["properties"]:
        try:
            match decoded_schema["properties"][element]["type"]:
                case "object":
                    return_dict[element] = schema_to_ref_gen(decoded_schema["properties"][element])
                case _:
                    return_dict[element] = decoded_schema["properties"][element]["description"]
        except KeyError as err:
            print("[main.schema_to_ref_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag"+
                  ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict

def py_to_tree(input_dict: dict, reference_dict: dict, return_tree) -> TreeClass:
    incrementor = 0
    for element in input_dict:
        try:
            if not element in reference_dict:
                raise KeyError("[main.py_to_tree/INFO]: Element not in Schema Definition.")
            if type(input_dict[element]) is str:
                return_tree.add_node(parent = return_tree.root_node, data = [element, str(input_dict[element]), reference_dict[element]])
            else:
                return_tree.add_node(parent=return_tree.root_node,
                                     data=[element, '', ''])
                part_tree = py_to_tree(input_dict[element], reference_dict[element], return_tree = TreeClass(data = ["K","V","D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieveChildbyIndex(incrementor)
                    return_tree.root_node.retrieveChildbyIndex(incrementor).appendChild(node)
            incrementor += 1
        except KeyError as err:
            print("Key " + element +" may not be present in Schema. Switch to empty description")
            if type(input_dict[element]) is str:
                return_tree.add_node(parent = return_tree.root_node, data = [element, str(input_dict[element]), 'Description not found'])
            else:
                return_tree.add_node(parent=return_tree.root_node,
                                     data=[element, '', ''])
                part_tree = py_to_tree(input_dict[element], {}, return_tree = TreeClass(data = ["K","V","D"]))
                for node in part_tree.root_node.childItems:
                    node.parentItem = return_tree.root_node.retrieveChildbyIndex(incrementor)
                    return_tree.root_node.retrieveChildbyIndex(incrementor).appendChild(node)
            incrementor += 1
    return return_tree


# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":
    import sys

    os.chdir('C:\\Users\\plathe\\Desktop\\Franke_Orga\\') # TODO: Replace with variable

    print(validator_files('C:\\Users\\plathe\\Desktop\\Franke_Orga\\test.json',
                         'C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON'))

    frame = decode_function('C:\\Users\\plathe\\Desktop\\Franke_Orga\\plasma-mds.json')

    pre_json = schema_to_py_gen(frame)
    pre_descr = schema_to_ref_gen(frame)
    baum = py_to_tree(pre_json, pre_descr)
    print(validator_vars(json.dumps(pre_json), 'C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON'))
    with open("out_json.json", "w") as out:
        json.dump(pre_json, out, indent = 4)

    print("Ping") # TODO: Remove Breaker Print for Debug

