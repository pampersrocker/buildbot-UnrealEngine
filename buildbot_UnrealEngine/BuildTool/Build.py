# -*- test-case-name: buildbot_UnrealEngine.test.test_Build -*-

from ..UnrealCommand import BaseUnrealCommand
from buildbot import config

from twisted.internet import defer


class Build(BaseUnrealCommand):
    """Runs the UnrealBuildTool (UBT)"""

    name = "UEBuild"

    supported_build_types = ["Build", "Rebuild", "Clean"]

    def __init__(
            self,
            engine_path,
            project_path,
            target,
            build_type="Build",
            target_config="Development",
            target_platform="Win64",
            wait_mutex=True,
            **kwargs):
        self.target = target
        self.target_config = target_config
        self.target_platform = target_platform
        self.build_type = build_type
        self.wait_mutex = wait_mutex
        super(Build, self).__init__(engine_path, project_path, **kwargs)

    @defer.inlineCallbacks
    def run(self):
        command = [
            self.getEngineBatchFilesPath(
                self.build_type, inside_platform_dir=True),
            self.target,
            self.target_platform,
            self.target_config,
            self.project_path]
        if self.wait_mutex:
            command.append("-WaitMutex")

        self.setupLogfiles()
        cmd = yield self.makeRemoteShellCommand(command=command)
        yield self.runCommand(cmd)
        defer.returnValue(cmd.results())

    def getCurrentSummary(self):
        return {"step": " ".join(self.getDescription(False))}

    def getResultSummary(self):
        return {"step": " ".join(self.getDescription(True))}

    def getDescription(self, done=False):
        description = [self.name]
        description.append("built" if done else "is building")
        description.extend([
            self.getProjectFileName(),
            "for",
            self.target_config,
            self.target_platform
        ])
        if done:
            description.extend(self.getDescriptionDetails())
        return description

    def doSanityChecks(self):
        if (isinstance(self.build_type, str) and
                self.build_type not in self.supported_build_types):
            config.error(
                "build_type '{0}' is not supported".format(self.build_type))
        if (isinstance(self.target_config, str) and
                self.target_config not in self.supported_target_config):
            config.error("target_config '{0}' is not supported".format(
                self.target_config))
        if (isinstance(self.target_platform, str) and
                self.target_platform not in self.supported_target_platforms):
            config.error("target_platform '{0}' is not supported".format(
                self.target_platform))

        super(Build, self).doSanityChecks()


class Rebuild(Build):
    def __init__(
        self,
        engine_path,
        project_path,
        target,
        **kwargs
    ):
        super(Rebuild, self).__init__(engine_path, project_path,
                                      target, build_type="Rebuild", **kwargs)

    name = "UERebuild"


class Clean(Build):
    def __init__(
        self,
        engine_path,
        project_path,
        target,
        **kwargs
    ):
        super(Clean, self).__init__(engine_path, project_path,
                                    target, build_type="Clean", **kwargs)

    name = "UEClean"
