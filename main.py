# ----------------------------------------
# pyJSON Converter GUI
# author: N. Plathe
# ----------------------------------------
# Music recommendation:
# Feuerschwanz - Memento Mori
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


# ----------------------------------------
# Execution
# ----------------------------------------

print(validator_function("C:\\Users\\plathe\\Desktop\\Franke_Orga\\wrong.json", "C:\\Users\\plathe\\Desktop\\Franke_Orga\\UBER.JSON"))
