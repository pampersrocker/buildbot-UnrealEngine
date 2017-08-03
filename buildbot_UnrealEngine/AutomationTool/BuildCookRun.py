# -*- test-case-name: buildbot_UnrealEngine.test.test_BuildCookRun -*-
from buildbot.steps.shell import ShellCommand
from ..UnrealCommand import BaseUnrealCommand, UnrealLogLineObserver
from buildbot import config

from twisted.python import failure
from twisted.python import log

from os import path
import re


class BuildCookRunLogLineObserver(UnrealLogLineObserver):

    _re_uat_warning = re.compile(r':Warning:')
    _re_cook = re.compile(r'LogCook:')
    _re_cook_file = re.compile(r'LogCook:Display: Cooking')

    nbCook = 0

    isBuilding = False
    isCooking = False
    isPackaging = False

    logcook = None

    def __init__(self, logwarnings, logerrors, logcook, **kwargs):
        self.logcook = logcook
        UnrealLogLineObserver.__init__(self, logwarnings, logerrors, **kwargs)

    def outLineReceived(self, line):
        if self._re_uat_warning.search(line):
            self.nbWarnings += 1
            self.logwarnings.addStdout("{0}\n".format(line))
            self.step.setProgress('warnings', self.nbWarnings)
        if self._re_cook_file.search(line):
            self.nbCook += 1
            self.step.setProgress('cook', self.nbCook)
        if self._re_cook.search(line):
            self.logcook.addStdout("{0}\n".format(line))
        UnrealLogLineObserver.outLineReceived(self, line)


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
        "build_platform",
        "archive_directory",
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
        self.archive = archive
        self.archive_directory = archive_directory
        self.p4 = p4
        self.unversioned_cooked_content = unversioned_cooked_content
        self.encrypt_ini_files = encrypt_ini_files
        self.release_version = release_version
        self.base_version = base_version
        self.compressed = compressed
        self.distribution = distribution
        self.iterate = iterate
        self.run_step = run
        self.devices = devices
        self.null_rhi = null_rhi
        self.nativize = nativize
        self.stage = stage
        self.map = map
        self.pak = pak
        self.prereqs = prereqs
        self.package = package
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
        command = [self.getEngineBatchFilesPath(
            "RunUAT", inside_platform_dir=False)]
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
        addArgIfSet(self.p4, command, "-P4", "-NoP4")
        if self.no_compile_editor:
            command.append("-NoCompileEditor")
        if self.build_step:
            command.append("-Build")
        if self.clean:
            command.append("-Clean")
        if self.archive:
            command.append("-Archive")
        if self.archive_directory is not None:
            command.append(
                "-ArchiveDirectory={0}".format(self.archive_directory))
        if self.unversioned_cooked_content:
            command.append("-UnversionedCookedContent")
        if self.encrypt_ini_files:
            command.append("-EncryptIniFiles")
        if self.release_version is not None:
            command.append(
                "-CreateReleaseVersion={0}".format(self.release_version))
        if self.base_version:
            command.append(
                "-BasedOnReleaseVersion={0}".format(self.base_version))
        if self.compressed:
            command.append("-Compressed")
        if self.distribution:
            command.append("-Distribution")
        if self.iterate:
            command.append("-Iterate")
        if self.run_step:
            command.append("-Run")
        if self.devices is not None:
            command.append(
                "-Device={0}".format("+".join(self.devices)))
        if self.null_rhi:
            command.append("-NullRHI")
        if self.nativize:
            command.append("-NativizeAssets")
        if self.stage:
            command.append("-Stage")
        if self.map is not None:
            command.append(
                "-Map={0}".format("+".join(self.map)))
        if self.pak:
            command.append("-Pak")
        if self.prereqs:
            command.append("-Prereqs")
        if self.package:
            command.append("-Package")
        self.setCommand(command)
        return BaseUnrealCommand.start(self)

    def setupLogfiles(self, cmd, logfiles):
        logwarnings = self.addLog("warnings")
        logerrors = self.addLog("errors")
        logcook = self.addLog("cook")
        self.logobserver = BuildCookRunLogLineObserver(
            logwarnings, logerrors, logcook)
        self.addLogObserver('stdio', self.logobserver)
        ShellCommand.setupLogfiles(self, cmd, logfiles)

    def createSummary(self, log):
        self.setStatistic('cook', self.logobserver.nbCook)
        BaseUnrealCommand.createSummary(self, log)

    def finished(self, result):
        self.getLog("cook").finish()
        BaseUnrealCommand.finished(self, result)

    def describe(self, done=False):
        if done is False:
            self.setStatistic('cook', self.logobserver.nbCook)
            self.setStatistic('warnings', self.logobserver.nbWarnings)
            self.setStatistic('errors', self.logobserver.nbErrors)

        description = [self.name]
        description.append('built' if done else 'is building')
        description.extend([
            self.getProjectFileName(),
            'for',
            self.target_config,
            self.target_platform])
        cook = self.getStatistic('cook', 0)
        if cook > 0:
            description.append("{0} files cooked")
        if done:
            description.extend(self.getDescriptionDetails())
        return description
