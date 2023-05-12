# pyJSON Schema Loader and JSON Editor

***Note: this tool is in development and everything including the README and the documentation is "under construction"!***

This is the repository for the pyJSON Schema Loader and JSON Editor - a limited feature set editor for JSON files, that utilises JSON Schema to create and validate JSON files.

## Purpose

The tool shall be used for storing important metadata within a filesystem-based approach. It doubles as a restricted JSON editor with the capability to read JSON and generate
them from a schema, but neither to generate JSONs or schemas from scratch, in order to maintain the flow "Schema -> JSON". If you need to create a schema from scratch, you may
use [the ADAMANT web tool](https://plasma-mds.github.io/adamant/) developed by the [QPTdat project](https://www.forschungsdaten.org/index.php/QPTDat). It shall be noted that
the capabilities of this tool are subject to change.

# Requirements

In short, pyJSON requires Python 3.10 or newer, PySide6 bindings for Qt6, the regex, the future and the jsonschema package.
Furthermore, the PyInstaller package is needed to freeze the environment and distribute it along an executable for the platform
of choice. Additional packages are needed for building the documentation. A virtual environment is highly advised.
Head over to the [installation section of the documentation](https://nplathe.github.io/pyJSON-Schema-Loader-and-JSON-Editor/installation.html) for details.

### Build a distributable package with PyInstaller

Information about this will be added in the [documentation](https://nplathe.github.io/pyJSON-Schema-Loader-and-JSON-Editor/index.html) in the future.

## Technical information

### Structure of the tool

Depending on the build process and the console parameters, the diectory structure will vary. This will be roughly the structure, when built on a Microsoft Windows OS via PyInstaller:
```
Script Directory
├── Logs                    Log directory. Gets created when the first log is written.
├── Schemas                 The storage for the schemas.
    └── default.json        The default schema, which doubles as a small test case
├── Default                 Storage for templates and defaults created by pyJSON
...
├── pyJSON.exe              The binary of pyJSON.              
├── pyJSON_conf.json        The config file of pyJSON.
└── pyJSON_interface.ui     The Qt GUI file of pyJSON.
```

## Featueres

### Reading, Validating and Writing JSON files

The pyJSON Schema Loader and JSON Editor is capable of opening and saving JSON files. It supports editing the values and, given the proper schema, provides a title and description for each key-value-pair. Every operation shall be validated against the schema in the future to prevent falsely entered information.

### Working with Schemas

A JSON schema can be used to validate information stored in JSON files. The tool uses this fact to generate JSON barebone files from schemas. Additional schemas can be added via `Files -> Add Schema...` and selected via the combobox for the currently selected schema. Defaults for the current schema can be stored and loaded.
