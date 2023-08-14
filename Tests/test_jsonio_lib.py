# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - IO and Conversion Test Module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# ----------------------------------------
# Libraries
# ----------------------------------------

import Modules.jsonio_lib, Modules.ModifiedTreeModel, json

# ----------------------------------------
# Variables and Functions
# ----------------------------------------

class Test_Validation:
    """
    Testing class for the small wrappers around the jsonschema library - if this does not work, data cannot be reliably
    validated against a schema.
    """
    def setup_class(self):
        self.json_path = "./Tests/Files/valid.json"
        self.schema_path = "./Tests/Files/schema.json"
        self.invalid_json = "./Tests/Files/invalid.json"
        self.invalid_schema = "./Tests/Files/invalid_schema.json"

    # Test - Validator with files
    def test_validator_files_success(self):
        # Should return 0.
        assert 0 == Modules.jsonio_lib.validator_files(self.json_path, self.schema_path)

    def test_validator_files_invalidj(self):
        # Should return 1, because one required entry is missing.
        assert 1 == Modules.jsonio_lib.validator_files(self.invalid_json, self.schema_path)

    def test_validator_files_invalids(self):
        # Should return 2, because the type set in the schema for the base object is not "object".
        assert 2 == Modules.jsonio_lib.validator_files(self.json_path, self.invalid_schema)

    def test_validator_files_fnf(self):
        # Because these paths are invalid, the return value should be -999.
        assert -999 == Modules.jsonio_lib.validator_files("", "")

    # Test - Validator with strings
    def test_decode_into_val_success(self):
        # Should return 0, if the json is correctly parsed, then dumped.
        decoded_json = json.dumps(Modules.jsonio_lib.decode_function(self.json_path))
        assert 0 == Modules.jsonio_lib.validator_vars(decoded_json, self.schema_path)

    def test_decode_into_val_invalidj(self):
        # Should return 1, for the same reason as in test_validator_files_invalidj.
        decoded_json = json.dumps(Modules.jsonio_lib.decode_function(self.invalid_json))
        assert 1 == Modules.jsonio_lib.validator_vars(decoded_json, self.schema_path)

    def test_decode_into_val_emptystring(self):
        # There is no JSON in the string. We expect a JSONDecoderError, which lets the function return -1.
        assert -1 == Modules.jsonio_lib.validator_vars("", self.schema_path)

    def test_decode_into_val_fnf(self):
        # Because the path of the schema is invalid, the return value should be -999.
        decoded_json = json.dumps(Modules.jsonio_lib.decode_function(self.json_path))
        assert -999 == Modules.jsonio_lib.validator_vars(decoded_json, "")


class Test_Decode:
    """
    A very small class of tests to test the JSON decoder wrapper.
    """
    def setup_class(self):
        self.json_path = "./Tests/Files/valid.json"

    def test_decode_success(self):
        # because of the current return values, we just check for the class
        assert isinstance(Modules.jsonio_lib.decode_function(self.json_path), dict)

    def test_decode_failure(self):
        # when sth is faulty, an integer instead of a dict gets returned
        assert isinstance(Modules.jsonio_lib.decode_function(""), int)


class Test_Schema_To_Py:
    """
    A class testing functionality of the schema_to_py function.
    """

    def setup_class(self):
        self.schema_path = "./Tests/Files/schema.json"

    def test_schema_to_py_key_success(self):
        # checking on the to expected structure via the keys.
        #TODO: When implementing any-of, this needs to be changed!
        decoded_schema = Modules.jsonio_lib.decode_function(self.schema_path)
        blank_json = Modules.jsonio_lib.schema_to_py_gen(decoded_schema)
        assert blank_json.keys() == {"@id", "@type", "misc", "user_info", "project"}
        assert blank_json["misc"].keys() == {"type_of_file", "identifier", "description", "working_dir", "start_date"}
        assert blank_json["user_info"].keys() == {"constructor", "engineer", "tags"}
        assert blank_json["project"].keys() == {"title", "department", "cost_unit", "revision_number"}


class Test_Py_To_Tree:
    """
    Test the conversion to the tree model for the QTreeView, setting data and converting it back to a dict, which has
    to be valid against the schema.
    """

    def setup_class(self):
        schema_path = "./Tests/Files/schema.json"
        decoded_schema = Modules.jsonio_lib.decode_function(schema_path)
        self.blank_json = Modules.jsonio_lib.schema_to_py_gen(decoded_schema)
        self.schema_metadata = Modules.jsonio_lib.schema_to_py_gen(decoded_schema, mode = "meta")


    def setup_method(self):
        self.tree = Modules.jsonio_lib.py_to_tree(
            self.blank_json,
            self.schema_metadata,
            return_tree = Modules.ModifiedTreeModel.ModifiedTreeClass(data = ["K", "Ti", "V", "Ty", "D"])
        )

    def teardown_method(self):
        del self.tree

    def test_py_conversion_success(self):
        # set data must comply to a specific key - one which is an enumerator
        self.tree.root_node.retrieve_child_by_index(2).retrieve_child_by_index(0).set_data(
            "Autodesk Inventor (.ipt, .iam, .ipn, .dwg, .idw)", 2)
        # check if the data is properly set and if it is in the right place
        assert self.tree.root_node.retrieve_child_by_index(2).retrieve_child_by_index(0).get_data(0) == "type_of_file"
        assert self.tree.root_node.retrieve_child_by_index(2).retrieve_child_by_index(0).get_data(2) == "Autodesk Inventor (.ipt, .iam, .ipn, .dwg, .idw)"
        assert self.tree.root_node.retrieve_child_by_index(2).get_data(0) == "misc"
        assert self.tree.root_node.retrieve_child_by_index(2).get_data(3) == "object"
        assert self.tree.root_node.retrieve_child_by_index(3).retrieve_child_by_index(2).get_data(0) == "tags"
        assert self.tree.root_node.retrieve_child_by_index(3).retrieve_child_by_index(2).get_data(3) == "array"

    def test_py_conversion_errors(self):
        tree2 = Modules.jsonio_lib.py_to_tree(
            {"misc": "", "test": "", "other": {"other_2":'', "other_3": []}},
            self.schema_metadata,
            return_tree = Modules.ModifiedTreeModel.ModifiedTreeClass(data = ["K", "Ti", "V", "Ty", "D"])
        )
        assert tree2.root_node.retrieve_child_by_index(0).get_data(0) == "misc"
        assert tree2.root_node.retrieve_child_by_index(0).get_data(1) == "KeyError"
        assert tree2.root_node.retrieve_child_by_index(1).get_data(0) == "test"
        assert tree2.root_node.retrieve_child_by_index(1).get_data(1) == "KeyError"
        assert tree2.root_node.retrieve_child_by_index(2).get_data(0) == "other"
        assert tree2.root_node.retrieve_child_by_index(2).get_data(3) == "object"

    def test_py_reverse_success(self):
        # set data must comply to a specific key - one which is an enumerator
        self.tree.root_node.retrieve_child_by_index(2).retrieve_child_by_index(0).set_data(
            "Autodesk Inventor (.ipt, .iam, .ipn, .dwg, .idw)", 2)
        jsonFrame = Modules.jsonio_lib.tree_to_py(self.tree.root_node.childItems)
        assert Modules.jsonio_lib.validator_vars(json.dumps(jsonFrame), "./Tests/Files/schema.json") == 0