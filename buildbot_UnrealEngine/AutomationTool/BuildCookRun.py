# -*- test-case-name: buildbot_UnrealEngine.test.test_BuildCookRun -*-
from ..UnrealCommand import BaseUnrealCommand, UnrealLogLineObserver
from buildbot import config
from twisted.internet import defer
import re


class BuildCookRunLogLineObserver(UnrealLogLineObserver):

    _re_uat_warning = re.compile(r':\s*Warning:')
    _re_cook = re.compile(r'LogCook:')
    _re_cook_file = re.compile(r'LogCook:\s*Display: Cooking')

    nbCook = 0

    isBuilding = False
    isCooking = False
    isPackaging = False

    logcook = None

    def __init__(self, **kwargs):
        UnrealLogLineObserver.__init__(self, **kwargs)

    @defer.inlineCallbacks
    def outLineReceived(self, line):
        if self._re_uat_warning.search(line):
            self.nbWarnings += 1
            self.logwarnings = yield self.getOrCreateLog("warnings")
            self.logwarnings.addStdout(u"{0}\n".format(line))
            self.step.setProgress('warnings', self.nbWarnings)
            self.step.updateSummary()
        if self._re_cook_file.search(line):
            self.nbCook += 1
            self.step.setProgress('cook', self.nbCook)
            self.step.updateSummary()
        if self._re_cook.search(line):
            self.logcook = yield self.getOrCreateLog("cook")
            self.logcook.addStdout(u"{0}\n".format(line))
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
        "release_version",
        "base_version",
        "no_compile_editor",
        "compile",
        "cook",
        "cook_on_the_fly",
        "build_step",
        "clean",
        "archive",
        "archive_directory",
        "p4",
        "unversioned_cooked_content",
        "encrypt_ini_files",
        "release_version",
        "base_version",
        "compressed",
        "distribution",
        "iterate",
        "run_step",
        "devices",
        "null_rhi",
        "nativize",
        "stage",
        "map",
        "pak",
        "prereqs",
        "package",
        "crash_reporter",
        "title_id",
        "verbose",
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
                 crash_reporter=False,
                 title_id=None,
                 verbose=False,
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
        self.title_id = title_id
        self.crash_reporter = crash_reporter
        self.verbose = verbose
        BaseUnrealCommand.__init__(self, engine_path, project_path, **kwargs)

    def doSanityChecks(self):
        BaseUnrealCommand.doSanityChecks(self)
        if isinstance(self.target_config, (str, list)) and self.target_config not in self.supported_target_config:
            config.error("target_config '{0}' is not supported".format(
                self.target_config))
        if isinstance(self.target_platform, (str, list)) and self.target_platform not in self.supported_target_platforms:
            config.error("target_platform '{0}' is not supported".format(
                self.target_platform))

    @defer.inlineCallbacks
    def run(self):
        def addArgIfSet(flag, commandList, ifTrue, ifFalse):
            if flag is True:
                commandList.append(ifTrue)
            elif flag is False:
                commandList.append(ifFalse)
        command = [self.getEngineBatchFilesPath(
            "RunUAT", inside_platform_dir=False)]
        command.append("BuildCookRun")
        command.append("-project={0}".format(self.project_path))
        platform = "+".join(self.target_platform) if isinstance(self.target_platform, list) else self.target_platform
        config = "+".join(self.target_config) if isinstance(self.target_config, list) else self.target_config
        command.append("-targetplatform={0}".format(platform))
        command.append("-platform={0}".format(platform))
        command.append("-clientconfig={0}".format(config))
        command.append("-serverconfig={0}".format(config))
        if self.engine_type != "Source":
            command.append("-{0}".format(self.engine_type))
        addArgIfSet(self.compile, command, "-Compile", "-NoCompile")
        addArgIfSet(self.cook, command, "-Cook", "-SkipCook")
        addArgIfSet(self.cook_on_the_fly, command,
                    "-CookOnTheFly", "-SkipCookOnTheFly")
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
        if self.crash_reporter:
            command.append("-CrashReporter")
        if self.verbose:
            command.append("-Verbose")

        if type(self.title_id) is list:
            command.append("-TitleID={0}".format("+".join(self.title_id)))
        elif self.title_id is not None:
            command.append("-TitleID={0}".format(self.title_id))
        self.setupLogfiles()
        cmd = yield self.makeRemoteShellCommand(command=command)
        yield self.runCommand(cmd)
        defer.returnValue(self.evaluateCommand(cmd))

    def setupLogfiles(self):
        self.logobserver = BuildCookRunLogLineObserver()
        self.addLogObserver('stdio', self.logobserver)

    def getCurrentSummary(self):
        return {"step": " ".join(self.getDescription(False))}

    def getResultSummary(self):
        return {"step": " ".join(self.getDescription(True))}

    def getDescription(self, done=False):
        description = [self.name]
        description.append('built' if done else 'is building')
        description.extend([
            self.getProjectFileName(),
            'for',
            str(self.target_config),
            str(self.target_platform)])
        cook = self.getStatistic('cook', 0)
        if cook > 0:
            description.append("{0} files cooked".format(cook))
        if done:
            description.extend(self.getDescriptionDetails())
        return description
