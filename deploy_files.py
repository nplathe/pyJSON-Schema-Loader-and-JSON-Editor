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
import logging

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

lg = logging.getLogger(__name__)


def deploy_schema(path):
    """
    deploys the default example schema that is hardcoded here into a path

    Args:
        path: the path the schema shall be deployed to.

    Returns:
        bool: True, if deployment was successful, False otherwise.
    """
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
			    	},\
        			"Example_Number":{\
    	    			"title": "Example Number/Float Value",\
    		    		"description": "I am an example Floating Point Number, test the input validation with me.",\
    			    	"type": "number"\
    			    },\
                    "Example_Int":{\
                        "title": "Example Integer Value",\
                        "description": "I am an example integer, test the input validation with me.",\
                        "type": "integer"\
                    }\
			    }\
		    }\
	    }\
    }'
    try:
        with open(os.path.join(path, "default.json"), "w") as out:
            json.dump(json.loads(schema), out, indent=4)
    except OSError as err:
        lg.error("[deploy_files.deploy_schema/ERROR]: Could not write file to directory!")
        return False
    return True


# main config

def deploy_config(path):
    """
    deploys the config file, which retains last used file, schema and directory

    Args:
        path (str): the path, in which the config shall be deployed

    Returns:
    """
    config = {
        "last_dir": os.getcwd(),
        "last_schema": "default.json",
        "last_JSON": None
    }
    try:
        with open(os.path.join(path, "pyJSON_conf.json"), "w") as out:
            json.dump(config, out, indent=4)
    except OSError as err:
        lg.error("[deploy_files.deploy_config/ERROR]: Could not set default config.")


def save_config(path, config):
    """
    Writes the config to the harddrive

    Args:
        path (str): the path, in which the config shall be saved or overwritten
        config (dict): the config dictionary

    Returns:
    """
    try:
        with open(os.path.join(path, "pyJSON_conf.json"), "w") as out:
            json.dump(config, out, indent=4)
    except OSError as err:
        lg.error("[deploy_files.save_config/ERROR]: Could not save config.")


# indexes
def saveMainIndex(path, index_dict):
    """
    Writes the main index containing information about all indexed directories to the harddrive

    Args:
        path (str): the path, in which the main index shall be saved or overwritten
        index_dict (dict): the main index dictionary

    Returns:
    """
    try:
        with open(os.path.join(path, "Indexes/pyJSON_S_index.json"), "w") as out:
            json.dump(index_dict, out, indent=4)
    except OSError as err:
        lg.error("[deploy_files.saveMainIndex/ERROR]: Could not save config.")


def saveIndex(path, index, count):
    """
    Writes the index of a directory to the harddrive

    Args:
        path (str): the path the index shall be written or overwritten to
        index (dict): the directory index
        count (int): the current index number, since the indexes are numbered

    Returns:
    """
    index_d = {"files": index}
    try:
        with open(os.path.join(path, "Indexes/index" + str(count) + ".json"), "w") as out:
            json.dump(index_d, out, indent=4)
    except OSError as err:
        lg.error("[deploy_files.saveIndex/ERROR]: Could not save index for " + path + ".")


# ----------------------------------------
# Execution
# ----------------------------------------

if __name__ == "__main__":
    lg.info("Please don't run me directly, I just provide some files and functions.")
    lg.info("Deploying files in the current working directory.")
    deploy_config(os.getcwd())
