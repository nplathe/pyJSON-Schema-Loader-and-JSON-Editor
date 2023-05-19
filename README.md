# pyJSON Schema Loader and JSON Editor

***Note: this tool is in development and everything including the README and the documentation is "under construction"!***

This is the repository for the pyJSON Schema Loader and JSON Editor - a JSON schema based JSON Editor and Validator.


## About
This is the pyJSON Schema Loader and JSON Editor - a JSON Schema based JSON editor capable of creating valid JSON from 
JSON schema. With pyJSON, one can create, edit, validate and save JSON documents. Furthermore, a simple search function 
helps keeping track of filesystem-based repositories filled with metadata.

 For a JSON schema creating software that is capable of being integrated in network workflow structures, please have a 
 look at [the ADAMANT web tool](https://github.com/INP-PM/adamant) ([Publication in F1000Research](https://doi.org/10.12688/f1000research.110875.1)). 


## Quick Start

* Make sure python 3.10 is installed and operational.
* Clone this repository.
* In a terminal, navigate to the cloned repository.
* (Recommended) Create a new virtual environment. Check your python distribution for details.
* Run `pip install -r requirements.txt` and wait for the command to finish.
* Execute `python ./pyJSON.py`


## Requirements

In short, pyJSON requires Python 3.10 or newer, PySide6 bindings for Qt6, the regex, the future and the jsonschema 
package. Furthermore, the PyInstaller package is needed to freeze the environment and distribute it along an executable 
for the platform of choice. Additional packages are needed for building the documentation. A virtual environment is 
highly advised.
Head over to the [installation section of the documentation](https://nplathe.github.io/pyJSON-Schema-Loader-and-JSON-Editor/installation.html)
for more details.

## Featueres

### Reading, Validating and Writing JSON files

The pyJSON Schema Loader and JSON Editor is capable of opening and saving JSON files. It supports editing the values and, 
given the proper schema, provides a title and description for each key-value-pair. Every operation shall be validated 
against the schema in the future to prevent falsely entered information.


### Working with Schemas

A JSON schema can be used to validate information stored in JSON files. The tool uses this fact to generate JSON barebone
files from schemas. Additional schemas can be added via `Files -> Add Schema...` and selected via the combobox for the 
currently selected schema. Defaults for the current schema can be stored and loaded.


### Organising Schemas on a file system

pyJSON can index directories for a search functionality based on the validation against a schema and on keywords entered
into a blank schema. Search results open in a separate window and can be opened in pyJSON, another editing software or 
in the file system viewer (currently only on Microsoft Windows).


## Technical information

### Current support of JSON schema keywords

pyJSON extracts the sturcture and additional information from a JSON schema recursively in order to create or enrich a 
table-like representation of the currently opened JSON document. Currently, pyJSON can create a JSON compliant to its 
schema or validate input utilising the following common keywords of JSON schema:

| field type | implemented keywords                       | note |
|------------|--------------------------------------------|------|
| String     | `title`, `description`, `enum`, `default`  |      |
| Number     | `title`, `description`, `default`          |      |
| Integer    | `title`, `description`, `default`          |      |
| Boolean    | `title`, `description`, `default`          |      |
| Array      | `title`, `description`                     |      |
| Object     | `title`, `description`, `type`, `required` |      |

Note that a JSON document always gets fully validated against the selected schema utilising the `jsonschema` package, regardless of the currently supported keywords of pyJSON. This can currently lead to the JSON still being invalid, despite no interception occured when invalid information was entered. The amount of supported keywords will be extended in the future.  


### Structure of the tool

Below a list of the repository and an explanation of important files:

```
Repository Directory
├── Default                  Storage for templates and defaults created by pyJSON.
├── Indexes                  Storage for search indexes.
    └── pyJSON_S_index.json  The main index file containing pairs of indexes and the path to the corresponding directory.
├── Logs                     Log directory. Gets created when the first log is written.
├── Modules                  Directory of the source code for modules of pyJSON.
├── Schemas                  The storage for the schemas.
    └── default.json         The default schema, which doubles as a small test case.
...
├── pyJSON.py                The main python file of pyJSON.
├── pyJSON_conf.json         The config file of pyJSON.
└── pyJSON_interface.py      Converted python file of the UI of pyJSON
```