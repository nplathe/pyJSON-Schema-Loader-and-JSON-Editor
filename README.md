# pyJSON Schema Loader and JSON Editor

***Note: this tool is in development and everything including the README and the documentation is "under construction"!***

This is the repository for the pyJSON Schema Loader and JSON Editor - a JSON schema based JSON Editor and Validator.

## About
This is the pyJSON Schema Loader and JSON Editor - a JSON Schema based JSON editor capable of creating valid JSON from JSON schema. With pyJSON, one can create, 
edit, validate and save JSON documents. Furthermore, a simple search function helps keeping track of filesystem-based repositories filled with metadata.

 For a JSON schema creating software that is capable of being integrated in network workflow structures, please have a look at [the ADAMANT web tool](https://github.com/INP-PM/adamant) ([Publication in F1000Research](https://doi.org/10.12688/f1000research.110875.1)). 

# Requirements

In short, pyJSON requires Python 3.10 or newer, PySide6 bindings for Qt6, the regex, the future and the jsonschema package.
Furthermore, the PyInstaller package is needed to freeze the environment and distribute it along an executable for the platform
of choice. Additional packages are needed for building the documentation. A virtual environment is highly advised.
Head over to the [installation section of the documentation](https://nplathe.github.io/pyJSON-Schema-Loader-and-JSON-Editor/installation.html) for details.

### Build a distributable package with PyInstaller

Information about this will be added in the [documentation](https://nplathe.github.io/pyJSON-Schema-Loader-and-JSON-Editor/index.html) in the future.

## Technical information

### Structure of the tool


```
Repo Directory
├── Logs                    Log directory. Gets created when the first log is written.
├── Schemas                 The storage for the schemas.
    └── default.json        The default schema, which doubles as a small test case.
├── Default                 Storage for templates and defaults created by pyJSON.
├── Indexes                 Storage for search indexes.
...
├── pyJSON.py               The main python file of pyJSON.              
└── pyJSON_conf.json        The config file of pyJSON.
```

## Featueres

### Reading, Validating and Writing JSON files

The pyJSON Schema Loader and JSON Editor is capable of opening and saving JSON files. It supports editing the values and, given the proper schema, provides a title and description for each key-value-pair. Every operation shall be validated against the schema in the future to prevent falsely entered information.

### Working with Schemas

A JSON schema can be used to validate information stored in JSON files. The tool uses this fact to generate JSON barebone files from schemas. Additional schemas can be added via `Files -> Add Schema...` and selected via the combobox for the currently selected schema. Defaults for the current schema can be stored and loaded.
