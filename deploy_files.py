# ----------------------------------------
# pyJSON Converter + GUI deploy_files module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# Feuerschwanz - Memento Mori
# Bullet for my Valentine - Bullet for my Valentine
# ----------------------------------------
# Libraries
# ----------------------------------------

import json
import os

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

def deploy_schema(path):
    schema = '{\
	    "$schema": "https://json-schema.org/draft/2020-12/schema",\
	    "$id": "https://inp-greifswald.de",\
	    "title": "Blank Schema",\
	    "description": "A default Schema for my pyjson converter. Get\'s created by the tool on the fly.",\
	    "type": "object",\
	    "properties": {\
		    "general": {\
			    "title": "general",\
			    "description": "I\'m just a blank test schema. Use me for testing and for trying out functions.",\
			    "type": "string"\
		    },\
		    "hierarch":{\
			    "title": "hierarch",\
			    "description": "Anchor for the rest.",\
			    "type": "object",\
    			"properties": {\
	    			"Stage 1":{\
		    			"title": "Stage 1",\
			    		"description": "Open a Schema from your hard drive and add it to the schema storage. Then select it via the selector.",\
				    	"type": "string"\
    				},\
    				"Stage 2":{\
	    				"title": "Stage 2",\
		    			"description": "You can generate a blank JSON from a schema, load a default for a selected schema or open a JSON and validate it.",\
			    		"type": "string"\
			    	}\
			    }\
		    }\
	    }\
    }'
    try:
        with open(os.path.join(path, "default.json"), "w") as out:
            json.dump(json.loads(schema), out, indent = 4)
    except OSError as err:
        print("[deploy_files.deploy_schema/ERROR]: Could not write file to directory!")
        return False
    return True

def deploy_config(path):
    config = {
            "last_dir": os.getcwd(),
            "last_schema": "default.json",
            "last_JSON": None
        }
    try:
        with open(os.path.join(path, "config.json"), "w") as out:
            json.dump(config, out, indent = 4)
    except OSError as err:
        print("[deploy_files.deploy_config/ERROR]: Could not set default config.")

def save_config(path, config):
    try:
        with open(os.path.join(path, "config.json"), "w") as out:
            json.dump(config, out, indent = 4)
    except OSError as err:
        print("[deploy_files.save_config/ERROR]: Could not save config.")

# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":
    print("Please don't run me directly, I just provide some files and functions.")
    print("Deploying files in the current working directory.")
    deploy_config(os.getcwd())