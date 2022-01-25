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
import os
import sys


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
        print("[validator_files/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        print("[validator_files/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        print("[validator_files/ERROR]: Either JSON or Schema is not accessible anymore!")
        return -999
    print("[validator_files/INFO]: Validation of JSON successful!")
    return 0


# Similarly to validator_files, but instead with a string representation of the JSON
def validator_vars(json_str, json_schema_path):
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path)
        ds_json = json.loads(json_str)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        print("[validator_vars/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        print("[validator_vars/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        print("[validator_vars/ERROR]: Schema is not accessible anymore!")
        return -999
    print("[validator_vars/INFO]: Validation of JSON successful!")
    return 0


# Wrapper for the JSONDecoder function
def decode_function(json_path):
    try:
        loaded_json = open(json_path)
        result = json.load(loaded_json, cls=json.JSONDecoder)
    except json.JSONDecodeError as err:
        print("[decode_function/ERROR]: JSON could not be parsed into Python representation!")
        return 2
    except OSError:
        print("[decode_function/ERROR]: JSON is not accessible anymore!")
        return -999
    return result


# A function generating a JSON-like python structure from the schema.
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
                    return_dict[element] = float("NaN")
                case "object":
                    return_dict[element] = schema_to_py_gen(decoded_schema["properties"][element])
        except KeyError as err:
            print("[schema_to_py_gen/CRITICAL]: Skipping element: " + element + ", because of missing \"type\"-tag"+
                  ". JSON may be not valid against corresponding schema anymore.")
            continue
    return return_dict


# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":

    os.chdir('C:\\Users\\plathe\\Desktop\\Franke_Orga\\') # TODO: Replace with variable

    print(validator_files('C:\\Users\\plathe\\Desktop\\Franke_Orga\\test.json',
                         'C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON'))

    frame = decode_function('C:\\Users\\plathe\\Desktop\\Franke_Orga\\plasma-mds.json')

    pre_json = schema_to_py_gen(frame)
    print(validator_vars(json.dumps(pre_json), 'C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON'))
    with open("out_json.json", "w") as out:
        json.dump(pre_json, out, indent = 4)

    print("Ping") # TODO: Remove Breaker Print for Debug

