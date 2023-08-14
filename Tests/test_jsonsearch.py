# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - Search Functions and Components Test Module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# ----------------------------------------
# Libraries
# ----------------------------------------

import Modules.jsonio_lib, Modules.jsonsearch_lib
import json

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

class Test_flatten_nested_dicts:
    def setup_class(self):
        self.json_path = "./Tests/Files/valid.json"
        self.schema_path = "./Tests/Files/schema.json"
        self.invalid_json = "./Tests/Files/invalid.json"
        self.invalid_schema = "./Tests/Files/invalid_schema.json"

    def test_flatter_success(self):
        json_dict = Modules.jsonio_lib.decode_function(self.json_path)
        flatted_dict = Modules.jsonsearch_lib.dict_flatten_dict(json_dict)
        print(flatted_dict)
        assert flatted_dict.keys() == {'@id', '@type', 'type_of_file' , 'identifier', 'description', 'working_dir',
                                       'start_date', 'constructor', 'engineer', 'tags0', 'tags1', 'tags2', 'title',
                                       'department', 'cost_unit', 'revision_number'}

