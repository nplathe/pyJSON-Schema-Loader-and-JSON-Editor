# Installation

## Pyinstaller builds

In order to simplify distribution, you can find packaged one-file builds created with [Pyinstaller](https://pyinstaller.org/en/stable/) via GitHub Actions
on [the releases page](https://github.com/nplathe/pyJSON-Schema-Loader-and-JSON-Editor/releases).
If you just want to use pyJSON without looking into the code or dealing with Python, the prebuilt files are the better choice.
Note that Pyinstaller builds are not extensively tested. If you encounter unusual behaviour, please open [an issue](https://github.com/nplathe/pyJSON-Schema-Loader-and-JSON-Editor/issues).

## Working with the code

In order to use pyJSON, at least Python 3.10 is required, alongside a few third-party modules.

```{warning}
Due to match cases being used in several parts, pyJSON is explicitly not compatible with versions
prior to python 3.10! See [PEP 636](https://peps.python.org/pep-0636/) for details.
```

Currently, in order to use pyJSON, it is necessary to download the source code. Either use
```bash
git clone https://github.com/nplathe/pyJSON-Schema-Loader-and-JSON-Editor
```
or use the "Code" -> "Download ZIP" button on the repository page to download the source code.

For running pyJSON, the following packages are needed:

| package    | version     | purpose                              |
|------------|-------------|--------------------------------------|
| jsonschema | ~=4.19.2    | JSON validation via JSON schema      |
| PySide6    | ~=6.5.1.1   | python bindings for the QT framework |
| regex      | ~=2023.10.3 | regular expressions                  |

## Prerequisites

It is highly recommended to create a virtual environment for installation and building an executable. Virtual environments 
keep your main installation free from unneeded packages and introduce a separation of the several packages used, which heavily
benefits development and avoids unnecessary issues, e.g. package conflicts.

### A: installing packages via pip

In order to run pyJSON, run the following command in the repository directory to install the dependencies.

```bash
pip install -r requirements.txt
```

```{warning}
As of [PEP 668](https://peps.python.org/pep-0668/), if your base environment is marked as externally managed, you **must**
use a virtual environment.
```

### B: conda managed environment

[conda](https://docs.conda.io/en/latest/) is an alternative package manager for python. It is capable of creating and managing
several sources for packages, creating virtual environments and solving dependencies for packages.

First create a new virtual environment and enter it.
```bash
conda create -n <yourenvname> python=3.10.9
conda activate <yourenvname>
```

You can always leave your environment with `conda deactivate`.

Install the dependencies. Note, that, dependent on your settings and distribution of the conda package manager, you might have
to specify the channel with the `-c` argument, e.g. `-c conda-forge` for the community-driven [conda-forge repository](https://conda-forge.org/),
which contains all of the needed packages.

```bash
conda install -c conda-forge jsonschema regex pyside6
```

## Building the documentation

If you are interested in building the documentation yourself, you need the following packages:

| package     | version    | purpose                            |
|-------------|------------|------------------------------------|
| sphinx      | ~=7.7.7    | documentation generation framework |
| myst-parser | ~=3.0.1    | Markdown parser for sphinx         |
| furo        | ~=2024.5.6 | alternative HTML theme for sphinx  |

## Running pyJSON
In your python environment in the command line, after installing the prerequisites, navigate to the directory pyJSON is located in and execute 

```bash
python pyJSON.py
```

## Building a distributable package
First, install [PyInstaller](https://pyinstaller.org/en/stable/) into your environment. Make sure to activate your environment, then navigate to the source directory and run

```bash
pyinstaller --clean --icon=icon.ico ./pyJSON.py
```

to generate a distributable frozen environment containing everything for pyJSON in order to run it without a local python installation.
You can add the `--onefile` parameter to create an one-file executable instead of a directory tree. 