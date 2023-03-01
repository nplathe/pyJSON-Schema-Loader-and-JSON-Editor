# The pyJSON Schema Loader and Editor Documentation

## Purpose

The tool shall be used for storing important metadata within a filesystem-based approach. It doubles as a restricted JSON editor with the capability to read JSON and generate
them from a schema, but neither to generate JSONs or schemas from scratch, in order to maintain the flow "Schema -> JSON". If you need to create a schema from scratch, you may
use [the ADAMANT web tool](https://plasma-mds.github.io/adamant/) developed by the [QPTdat project](https://www.forschungsdaten.org/index.php/QPTDat). It shall be noted that
the capabilities of this tool are subject to change.

## Requirements
Head over to the [installation](installation) section of the documentation.
In short, pyJSON requires Python 3.10 or newer, PyQt bindings for Qt5, the regex, the future and the jsonschema package.
Furthermore, the PyInstaller package is needed to freeze the environment and distribute it along an executable for the platform
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
modules
```

# Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`