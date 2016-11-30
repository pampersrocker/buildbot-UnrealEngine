# buildbot-UnrealEngine
Buildbot Plugin to run Commands using the Unreal Automation Tool

[![PyPI version](https://badge.fury.io/py/buildbot-UnrealEngine.svg)](https://badge.fury.io/py/buildbot-UnrealEngine) [![Build Status](https://travis-ci.org/pampersrocker/buildbot-UnrealEngine.svg?branch=master)](https://travis-ci.org/pampersrocker/buildbot-UnrealEngine)

# Installation

```
pip install buildbot_UnrealEngine
```

This enables the additional step commands as plugins inside buildbot (which are imported via `from buildbot.plugins import steps`)

# Usage

```py
from buildbot.plugins import steps

factory = util.BuildFactory()

factory.addStep(
  steps.UEBuild(
    "Engine_Location",
    "Path_To_Project.uproject",
    "TargetName",
    # Additional Parameters, see below
  )
)

factory.addStep(
  steps.BuildCookRun(
    "Engine_Location",
    "Path_To_Project.uproject",
    # Additional Parameters, see below
  )
)
```

# Parameters

All commands share the following base parameters:

| Parameter | Type/Options | Description |
| --- | --- | --- |
| engine_path |string (required) | The location to the used engine, the path needs to point to the root folder of the engine (in this folder are at least the `Engine`, `FeaturePacks`, `Samples` and `Templates` folders) |
| project_path | string (required) | The absolute location to the uproject file to be used. (Usually a `Interpolate("...")` to build the path using the current builddir) |
| build_platform | string (default `"Windows"`), Options: `"Windows"` `"Linux"` `"Mac"` | The platform on which the build itself will run, used to determine which scripts to run |
| engine_type | string (default `"Rocket"`), Options: `"Source"` `"Installed"` `"Rocket"` | <p><ul><li>`Source`: Engine is built from GitHub Source</li><li>`Installed`: Engine is self build from GitHub source and made a binary build via the BuildGraph tool</li><li>`Rocket`: Pre-built engine from Epic Games via EpicGamesLauncher</li></ul></p> |


# Development Setup under Windows

* Download and install [Python 2.7](https://www.python.org/downloads/)

* Install virtualenv
  ```
  pip install virtualenv
  ```
* Create a virtualenv in `.workspace\venv`
  ```
  mkdir .workspace
  cd workspace
  C:\Python27\Scripts\virtualenv.exe venv
  cd ..\..\
  .workspace\venv\Scripts\activate.bat
  pip install -r requirements.txt
  ```

* Download [PyWin32](https://sourceforge.net/projects/pywin32/files/pywin32/) (for twisted) and install it in your venv
  ```
  easy_install <PATH_TO_pywin32-220.win32-py2.7.exe>
  ```

* Clone Buildbot (in Version 0.9.1) somewhere and install it and its test setup
  ```
  git clone https://github.com/buildbot/buildbot.git -b v0.9.1
  cd buildbot\master
  pip install -e .
  python setup.py test
  ```

* Install buildbot-UnrealEngine (inside your buildbot-UnrealEngine repo)
  ```
  pip install -e .
  ```

* Now you can run the tests by writing
  ```
  trial buildbot_UnrealEngine.test
  ```

* For code coverage install txcovreport:
  ```
  easy_install http://darcs.idyll.org/~t/projects/figleaf-latest.tar.gz
  pip install git+https://github.com/jrydberg/txcovreport.git
  ```

  Now you can run code coverage using
  ```
  trial --reporter=tree-coverage buildbot_UnrealEngine.test
  ```
