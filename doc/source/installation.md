# Installation

## Requirements

In order to use pyJSON, at least Python 3.10 is required.

```{warning}
Due to match cases being used in several parts, pyJSON is explicitly not compatible with versions
prior to python 3.10! See [PEP 636](https://peps.python.org/pep-0636/) for details.
```

For running pyJSON, the following packages are needed:

* jsonvalidate (~=4.17.3)
* PyQt5 (~=5.15.7)
* regex (~=2022.7.9)
* future (~=0.18.2)

Furthermore, in order to build the documentation

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

After creation of the new environment, packages can be added with

```bash
conda install -n <yourenvname> [package-name]
```

```{warning}
Some packages are not located in the standard conda repository, but e.g. in the conda-forge repository.
Use `conda install -c conda-forge -n <yourenvname> [package-name]` for installation then.
```

## Building a distributable package