# buildbot-UnrealEngine
Buildbot Plugin to run Commands using the Unreal Automation Tool

[![PyPI version](https://badge.fury.io/py/buildbot-UnrealEngine.svg)](https://badge.fury.io/py/buildbot-UnrealEngine) [![Build Status](https://travis-ci.org/pampersrocker/buildbot-UnrealEngine.svg?branch=master)](https://travis-ci.org/pampersrocker/buildbot-UnrealEngine) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/pampersrocker/buildbot-UnrealEngine/master/LICENSE)

# Installation

```
pip install buildbot_UnrealEngine
```

This enables the additional step commands as plugins inside buildbot (which are imported via `from buildbot.plugins import steps`)

# Usage

```py
from buildbot.plugins import steps

factory = util.BuildFactory()

###### Build commands

factory.addStep(
    steps.UEBuild(
        "Engine_Location",
        "Path_To_Project.uproject",
        "TargetName",
        # Additional Parameters, see below
    )
)

factory.addStep(
    steps.UERebuild(
        "Engine_Location",
        "Path_To_Project.uproject",
        "TargetName",
        # Additional Parameters, see below
    )
)

factory.addStep(
    steps.UEClean(
        "Engine_Location",
        "Path_To_Project.uproject",
        "TargetName",
        # Additional Parameters, see below
    )
)

###### BuildCookRun

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

# Build Cook Run Parameters

```py
factory.addStep(
    steps.BuildCookRun(
        engine_path,
        project_path,
        target_platform="Win64",
        target_config="Development",
        no_compile_editor=False,
        compile=None,
        cook=None,
        cook_on_the_fly=None,
        build=False,
        clean=False,
        archive=False,
        archive_directory=None,
        p4=None,
        unversioned_cooked_content=False,
        encrypt_ini_files=False,
        release_version=None,
        base_version=None,
        compressed=False,
        distribution=False,
        iterate=False,
        run=False,
        devices=None,
        null_rhi=False,
        nativize=False,
        stage=False,
        map=None,
        pak=False,
        prereqs=False,
        package=False,
        crash_reporter=False,
        title_id=None,
        dlc_name=None,
        dlc_include_engine=False,
        generate_patch=False,
        add_patch_level=False,
        generate_remaster=False,
        extra_args=None,
    )
)
```

| Parameter | Type/Options | Description |
| --- | --- | --- |
| no_compile_editor | bool | If true adds `-NoCompileEditor` to the command line. Skip compiling the editor target for game (needed for cooking), useful if already done before. |
| compile | bool | If true adds `-Compile` to the command line. `-NoCompile` if false. This switch is usually required on source builds. It tells the UAT to compile itself before running any commandlets, however on Installed/Rocket builds this will result in an error as the sources for UAT are not part of those engine distributions. |
| cook | bool | If true adds `-Cook` to the command line. `-SkipCook` if false. Enables or disables the cook step. |
| cook_on_the_fly | bool | If true adds `-CookOnTheFly` to the command line. `-SkipCookOnTheFly` if false. Does not cook the content, but starts the cook process in servermode, where a game can connect to using the `-FileHostIP=<IP>` parameter to connect to this server. The server will then cook requested content on the fly. |
| build | bool | If true adds `-Build` to the command line. Enables the build step, compiling the game for the target platform. |
| clean | bool | If true adds `-Clean` to the command line. Perform a clean build |
| archive | bool | If true adds `-Archive` to the command line. Archive the build after completion. |
| archive_directory | string | If true adds `-ArchiveDirectory=<TheString>` to the command line. Specify the archive directory. If omitted, the path in the configuration file will be used. |
| p4 | bool | If true adds `-P4` to the command line, `-NoP4` if false. Enables disabled interaction with Perforce. |
| unversioned_cooked_content | bool | If true adds `-UnversionedCookedContent` to the command line. This writes no version into the cooked assets. |
| encrypt_ini_files | bool | If true adds `-EncryptIniFiles` to the command line. Encrypts the packaged ini files. |
| release_version | string | If set adds `-CreateReleaseVersion=<TheString>` to the command line. This creates a releasee version of the game for later patching (see BasedOnReleaseVersion) |
| base_version | string | If set adds `-BasedOnReleaseVersion=<TheString>` to the command line. This creates a patch or dlc based on the given release version, containing only changes that differ from the release version. |
| compressed | bool | If true adds `-Compressed` to the command line. This compressed your pak files to be to use fewer disk space, but increased loading times. |
| distribution | bool | If true adds `-Distribution` to the command line. Creates a distribution build (used for mobile) |
| iterate | bool | If true adds `-Iterate` to the command line. Only cooks changed files if run on the same directory as before |
| run | bool | If true adds `-Run` to the command line. Runs the packaged game after completion. |
| devices | string array | If set adds `-Device=<The+String+Array>` to the command line. Specifies on which devices the game will be run upon completion. |
| null_rhi | bool | If true adds `-NullRHI` to the command line. Runs the packaged games with no renderer. |
| nativize | bool | If true adds `-NativizeAssets` to the command line. Runs blueprint nativization during the cook process |
| stage | bool | If true adds `-Stage` to the command line. Save the cooked result in a staging directory |
| map | string array | If set adds `-Map=<The+String+Array> to the command line. Sets the map to include for the cook process. If omitted, used the one specified on the project documentation. |
| pak | bool | If true adds `-Pak` to the command line. Use pak files for packaging, if omitted uassets file will be directly in the content directory. |
| prereqs | bool | If true adds `-Prereqs` to the command line. Include prerequisites in the packaged game. |
| package | bool | If true adds `-Package` to the command line. Package the game for the target platform (app file on Mac, apk on Android or ipa on iPhone) |
| crash_reporter | bool | If true adds `-CrashReporter` to the command line. Includes the crash reporter during packaging. |
| dlc_name | string | If set adds -DLCName=<DLCName> to the command line. This will cook the specified Plugin as DLC. |
| dlc_include_engine | bool | If true adds `-DLCIncludEngineContent` to the command line. DLC should include Engine content. |
| generate_patch | bool | If true adds `-GeneratePatch` to the command line. Create a patch, requires `base_version` to be set. |
| add_patch_level | bool | If true adds `-AddPatchLevel` to the command line. Adds a patch pak level, when creating a patch. |
| generate_remaster | bool | If true adds `-GenerateRemaster` to the command line. PS4 specific patch option. |
| title_id | string or list of strings | If true adds `-TitleId=<Title+Id+Separated>` to the command line. PS4 specific title id command. |
| extra_args | string or list of strings | If set adds the given arguments to the command line. Can be used for custom or missing command line parameters. |


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
