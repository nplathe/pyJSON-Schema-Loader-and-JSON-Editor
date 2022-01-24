# ----------------------------------------
# pyJSON Converter + GUI
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
# The validator function shall wrap around json.load and validate

def validator_function(json_path, json_schema_path):
    try:  # open JSON and schema, deserialize both and validate
        loaded_schema = open(json_schema_path)
        loaded_json = open(json_path)
        ds_json = json.load(loaded_json)
        ds_schema = json.load(loaded_schema)
        validate(instance = ds_json, schema = ds_schema)
    except jsonschema.exceptions.ValidationError as err:
        print("[validator_function/ERROR]: JSON is not valid against selected Schema!")
        return 1
    except jsonschema.exceptions.SchemaError as err:
        print("[validator_function/ERROR]: The JSON schema is not valid against its selected meta schema!")
        return 2
    except OSError:
        print("[validator_function/ERROR]: Either JSON or Schema is not accessible anymore!")
        return -999
    return 0


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


def schema_to_py_gen(decoded_schema):
    return_dict = {}
    for element in decoded_schema["properties"]:
        #print(element)
        #print(decoded_schema["properties"][element])
        #print("-------------------------------")
        match decoded_schema["properties"][element]["type"]:
            case "string":
                return_dict[element] = ""
            case "array":
                return_dict[element] = []
            case "number":
                return_dict[element] = float("NaN")
            case "object":
                return_dict[element] = schema_to_py_gen(decoded_schema["properties"][element])
    return return_dict


# ----------------------------------------
# Execution
# ----------------------------------------

print(validator_function('C:\\Users\\plathe\\Desktop\\Franke_Orga\\wrong.json',
                         'C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON'))

frame = decode_function('C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON')
pre_json = schema_to_py_gen(frame)
print("Ping")