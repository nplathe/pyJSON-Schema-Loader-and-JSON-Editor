# Installation

## Requirements

In order to use pyJSON, at least Python 3.10 is required, alongside a few third-party modules.

```{warning}
Due to match cases being used in several parts, pyJSON is explicitly not compatible with versions
prior to python 3.10! See [PEP 636](https://peps.python.org/pep-0636/) for details.
```

For running pyJSON, the following packages are needed (also stored in the requirements.txt):

* jsonvalidate (~=4.17.3)
* PySide6 (~=6.5.0)
* regex (~=2022.7.9)
* future (~=0.18.3)

Furthermore, in order to build the documentation, 

* sphinx (~=5.0.2)
* myst-parser (~=0.18.1)
* furo (~=2022.12)

should be installed as well.

In order to provide frozen environment builds, PyInstaller is recommended.

## Prerequisites

It is highly recommended to create a virtual environment for installation and building an executable.

With an [Anaconda installation](https://www.anaconda.com/), a new environment is created via

```bash
conda create -n <yourenvname> python=3.10.9
```
with `<yourenvname>` being replaced by a name of your choosing.
You can then switch into your environment with

```bash
conda activate <yourenvname>
```

```{note}
Leave your environment with `conda deactivate`.
```
After creation of the new environment, packages can be added. For **PySide6**, it is advised to install it via pip. In your environment, run:

```bash
pip install PySide6
```

Afterwards, you can install packages with:

```bash
conda install -n <yourenvname> [package-name]
```

```{warning}
Some packages are not located in the standard conda repository, but e.g. in the conda-forge repository.
Use `conda install -c conda-forge -n <yourenvname> [package-name]` for installation then.
```

Alternatively, if you are not using Anaconda, you might install all requirements with

```bash
pip -r requirements.txt
```

## Running pyJSON
In your python environment in the command line, after installing the prerequisites, navigate to the directory pyJSON is located in and execute 

```bash
python pyJSON.py
```

## Building a distributable package
First, install [PyInstaller](https://pyinstaller.org/en/stable/) into your environement. Make sure to activate your environment, then navigate to the source directory and run

```bash
pyinstaller --clean --icon=icon.ico .\pyJSON.py
```

to generate a distributable frozen environment containing everything for pyJSON in order to run it without a local python installation.
You can add the `--onefile` parameter to create an one-file executable instead of a directory tree. 