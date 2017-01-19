from buildbot.steps.shell import ShellCommand
from buildbot import config

from os import path


class BaseUnrealCommand(ShellCommand):

    """
    Base class for all unreal related commands, holds basic parameters:
    - engine_path: Path to the root folder of the used engine
    - project_path: Path to the uproject file of the project used in the build

    In addition some utility functions are provided
    to help ensure the build parameters are valid
    """

    renderables = [
        "project_path",
        "engine_path",
    ]

    supported_target_platforms = [
        "Win32",
        "Win64",
        "Mac",
        "XboxOne",
        "PS4",
        "IOS",
        "Android",
        "HTML5",
        "Linux",
        "TVOS"
    ]
    supported_target_config = [
        "Debug",
        "DebugGame",
        "Development",
        "Test",
        "Shipping"
    ]
    supported_build_platforms = ["Windows", "Linux", "Mac"]
    supported_engine_types = ["Source", "Installed", "Rocket"]

    name = "BaseUnrealCommand"

    def __init__(
            self,
            engine_path,
            project_path,
            do_sanity_checks=True,
            engine_type="Rocket",
            build_platform="Windows",
            **kwargs):
        self.engine_path = engine_path
        self.project_path = project_path
        self.build_platform = build_platform
        self.do_sanity_checks = do_sanity_checks
        self.engine_type = engine_type
        ShellCommand.__init__(self, **kwargs)
        self.runSanityChecks()

    def getPlatformScriptExtension(self):
        if self.build_platform == "Windows":
            return "bat"
        elif self.build_platform == "Linux":
            return "sh"
        elif self.build_platform == "Mac":
            return "command"

    def runSanityChecks(self):
        if self.do_sanity_checks:
            self.doSanityChecks()

    def getEngineBatchFilesPath(self, script):
        return path.join(
            self.engine_path,
            "Engine",
            "Build",
            "BatchFiles",
            "{0}.{1}".format(script, self.getPlatformScriptExtension()))

    def doSanityChecks(self):
        if (isinstance(self.build_platform, str) and
                self.build_platform not in self.supported_build_platforms):
            config.error("build_platform '{0}' is not supported".format(
                self.build_platform))
        if (isinstance(self.engine_type, str) and
                self.engine_type not in self.supported_engine_types):
            config.error(
                "engine_type '{0}' is not supported".format(self.engine_type))
