# ----------------------------------------
# pyJSON Schema Loader and JSON Editor - IO and Conversion Test Module
# author: N. Plathe
# ----------------------------------------
# Music recommendation (albums):
# ----------------------------------------
# Libraries
# ----------------------------------------

import Modules.jsonio_lib, json

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
        is_correct = False
        decoded_schema = Modules.jsonio_lib.decode_function(self.schema_path)
        blank_json = Modules.jsonio_lib.schema_to_py_gen(decoded_schema)
        if (blank_json.keys() == {"@id", "@type", "misc", "user_info", "project"} and
            blank_json["misc"].keys() == {"type_of_file", "identifier", "description", "working_dir", "start_date"} and
            blank_json["user_info"].keys() == {"constructor", "engineer", "tags"} and
            blank_json["project"].keys() == {"title", "department", "cost_unit", "revision_number"}
        ):
            is_correct = True
        assert is_correct


#class Test_Py_To_Tree:
#    """
#    Test the conversion to the tree model for the QTreeView
#    """
#
#    def setup_class(self):
#        schema_path = "./Tests/Files/schema.json"
#        decoded_schema = Modules.jsonio_lib.decode_function(schema_path)
#        self.blank_json = Modules.jsonio_lib.schema_to_py_gen(decoded_schema)
#        self.schema_metadata = Modules.jsonio_lib.schema_to_py_gen(decoded_schema, mode = "meta")

#    def test_py_conversion_success:
