# pyJSON-Converter-GUI

A repo for the JSON Converter GUI I am creating for Steffen Franke.

## Purpose

The tool shall be used for storing important metadata within a filesystem-based approach. It doubles as a restricted JSON editor with the capability to read JSON and generate them from a schema, but neither to generate JSONs or schemas from scratch, in order to maintain the flow "Schema -> JSON". It shall be noted that the capabilities of this tool are subject to change.

## Requirements

The pyJSON GUI (proper name pending) requires Python >= 3.10. A proper dependency list follows soon-ish.

## Featueres

### Reading, Validating and Writing JSON files

The pyJSON GUI is capable of opening and saving JSON files. It supports editing the keys and the values and, given the proper schema, provides a title and description for each key-value-pair. Every operation shall be validated against the schema in the future to prevent falsely entered information.

### Working with Schemas

A JSON schema can be used to validate information stored in JSON files. The tool uses this fact to generate JSON barebone files from schemas. Additional schemas can be added via `Files -> Add Schema...` and selected via the combobox for the currently selected schema. Defaults for the current schema can be stored and loaded.

### Navigating through folders

In order to make management of several JSON files in the filesystem more affordable, the tool can swap it's working directory and store as well as automagically* load `metadata.json` files, those shall be used in another project later. In a long term goal, the generated and maintained JSON files shall be used with several other tools, including, but not limited to eLabFTW.
