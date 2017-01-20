# -*- test-case-name: buildbot_UnrealEngine.test.test_BuildCookRun -*-
from ..UnrealCommand import BaseUnrealCommand
from buildbot import config

from twisted.python import failure
from twisted.python import log

from os import path


class BuildCookRun(BaseUnrealCommand):

    """
    Creates a command like
    <Path to Engine>\Engine\Build\BatchFiles\RunUAT.bat BuildCookRun
    -project=<ProjectPath> -noP4 -nocompileeditor
    -targetplatform=<Platform> -platform=<Platform>
    -clientconfig=<TargetConfig> -serverconfig=<TargetConfig>
    -cook -allmaps -compile -stage -pak -archive
    -archivedirectory=<ArchivePath> -Build -prereqs -package
    """

    name = "BuildCookRun"

    renderables = [
        "target_platform",
        "target_config",
        "build_platform"
    ]

    def __init__(self,
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
                 # maps=True,
                 **kwargs):
        self.target_platform = target_platform
        self.target_config = target_config
        self.no_compile_editor = no_compile_editor
        self.compile = compile
        self.cook = cook
        self.cook_on_the_fly = cook_on_the_fly
        # self.build is apparently used somhwere internally for something else
        self.build_step = build
        self.clean = clean
        BaseUnrealCommand.__init__(self, engine_path, project_path, **kwargs)

    def doSanityChecks(self):
        BaseUnrealCommand.doSanityChecks(self)
        if self.target_config not in self.supported_target_config:
            config.error("target_config '{0}' is not supported".format(
                self.target_config))
        if self.target_platform not in self.supported_target_platforms:
            config.error("target_platform '{0}' is not supported".format(
                self.target_platform))

    def start(self):
        def addArgIfSet(flag, commandList, ifTrue, ifFalse):
            if flag is True:
                commandList.append(ifTrue)
            elif flag is False:
                commandList.append(ifFalse)
        command = [self.getEngineBatchFilesPath("RunUAT")]
        command.append("BuildCookRun")
        command.append("-project={0}".format(self.project_path))
        command.append("-targetplatform={0}".format(self.target_platform))
        command.append("-platform={0}".format(self.target_platform))
        command.append("-clientconfig={0}".format(self.target_config))
        command.append("-serverconfig={0}".format(self.target_config))
        addArgIfSet(self.compile, command, "-Compile", "-NoCompile")
        addArgIfSet(self.cook, command, "-Cook", "-SkipCook")
        addArgIfSet(self.cook_on_the_fly, command,
                    "-CookOnTheFly", "-SkipCookOnTheFly")
        if self.engine_type != "Source":
            command.append("-{0}".format(self.engine_type))
        if self.no_compile_editor:
            command.append("-NoCompileEditor")
        if self.build_step:
            command.append("-Build")
        if self.clean:
            command.append("-Clean")
        self.setCommand(command)
        return BaseUnrealCommand.start(self)
