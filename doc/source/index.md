# The pyJSON Schema Loader and Editor Documentation

## About
This is the pyJSON Schema Loader and JSON Editor - a JSON Schema based JSON editor capable of creating valid JSON from JSON schema. With pyJSON, one can create, 
edit, validate and save JSON documents. Furthermore, a simple search function helps keeping track of filesystem-based repositories filled with metadata.

For a JSON schema creating software that is capable of being integrated in network workflow structures, please have a look at [the ADAMANT web tool](https://github.com/INP-PM/adamant) ([Publication in F1000Research](https://doi.org/10.12688/f1000research.110875.1)). 

## Grant information
The work was funded by the Federal Ministry of Education and Research (BMBF) under the grant mark 16QK03A and by "Deutsche Forschungsgemeinschaft (DFG)" - Projektnummer 454848899. 
The responsibility for the content of this repository lies with the authors.

## Requirements
Head over to the [installation](installation) section of the documentation for details.
In short, pyJSON requires Python 3.10 or newer, `PySide6` as bindings for Qt6, the `regex`, the `future` and the `jsonschema` package.
Furthermore, the `PyInstaller` package is needed, if you want to freeze the environment and distribute pyJSON as an executable for the platform
of choice. Additional packages are needed for building the documentation. A virtual environment is highly advised.

```{note}
pyJSON is unter active development
```


```{toctree}
---
maxdepth: 2
caption: Contents
---

installation
usage
modules
```

# Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`