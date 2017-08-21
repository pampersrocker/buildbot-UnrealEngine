from buildbot.steps.shell import ShellCommand
from buildbot.process.buildstep import LogLineObserver
from buildbot.steps.vstudio import MSLogLineObserver
from buildbot.process.results import FAILURE
from buildbot.process.results import SUCCESS
from buildbot.process.results import WARNINGS
from buildbot import config
from os import path
import re


class UnrealLogLineObserver(MSLogLineObserver):

    _re_file = re.compile(r'^\[\d+/\d+\].*\.(cpp|c)$')
    _re_ubt_error = re.compile(r' ?[Ee]rror\s*: ')
    _re_clang_warning = re.compile(r':\s*warning\s*:')
    _re_clang_error = re.compile(r':\s*error\s*: ')

    def parseLine(self, line):
        if (self._re_ubt_error.search(line) or
           self._re_clang_error.search(line)):
            self.nbErrors += 1
            self.logerrors.addStderr(u"{0}\n".format(line))
            return True
        elif self._re_clang_warning.search(line):
            self.nbWarnings += 1
            self.logwarnings.addStdout(u"{0}\n".format(line))
            self.step.setProgress('warnings', self.nbWarnings)
            return True
        return False

    def outLineReceived(self, line):
        if(self._re_file.search(line)):
            self.nbFiles += 1
        if self.parseLine(line) is False:
            super(UnrealLogLineObserver, self).outLineReceived(line)

    def errLineReceived(self, line):
        if self.parseLine(line) is False:
            super(UnrealLogLineObserver, self).errLineReceived(line)


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

    def getPlatformScriptExtension(self, inside_platform_dir=False):
        if self.build_platform == "Windows":
            return "bat"
        # Mac scripts use shell for scripts other than
        # UAT and the Project level scripts
        elif self.build_platform == "Linux" or inside_platform_dir:
            return "sh"
        elif self.build_platform == "Mac":
            return "command"

    def runSanityChecks(self):
        if self.do_sanity_checks:
            self.doSanityChecks()

    def getEngineBatchFilesPath(self, script, inside_platform_dir=False):
        platform_dir = ""
        # Windows is the main platform and has no platform specific dir
        if inside_platform_dir and self.build_platform != "Windows":
            platform_dir = self.build_platform
        return path.join(
            self.engine_path,
            "Engine",
            "Build",
            "BatchFiles",
            platform_dir,
            "{0}.{1}".format(
                script, self.getPlatformScriptExtension(inside_platform_dir)))

    def getProjectFileName(self):
        projectName = self.project_path
        projectName = projectName.replace("\\", "/")
        splittedName = projectName.split("/")
        if len(splittedName) >= 2:
            projectName = splittedName[-1]
        return projectName

    def doSanityChecks(self):
        if (isinstance(self.build_platform, str) and
                self.build_platform not in self.supported_build_platforms):
            config.error("build_platform '{0}' is not supported".format(
                self.build_platform))
        if (isinstance(self.engine_type, str) and
                self.engine_type not in self.supported_engine_types):
            config.error(
                "engine_type '{0}' is not supported".format(self.engine_type))

    def setupLogfiles(self, cmd, logfiles):
        logwarnings = self.addLog("warnings")
        logerrors = self.addLog("errors")
        self.logobserver = UnrealLogLineObserver(logwarnings, logerrors)
        self.addLogObserver('stdio', self.logobserver)
        ShellCommand.setupLogfiles(self, cmd, logfiles)

    def getDescriptionDetails(self):
        details = []
        files = self.getStatistic('files', 0)
        if files > 0:
            details.append('{0} files'.format())
        warnings = self.getStatistic('warnings', 0)
        if warnings > 0:
            details.append('{0} warnings'.format(warnings))
        errors = self.getStatistic('errors', 0)
        if errors > 0:
            details.append('{0} errors'.format(errors))
        return details

    def createSummary(self, log):
        self.setStatistic('files', self.logobserver.nbFiles)
        self.setStatistic('warnings', self.logobserver.nbWarnings)
        self.setStatistic('errors', self.logobserver.nbErrors)

    def evaluateCommand(self, cmd):
        if cmd.didFail():
            return FAILURE
        if self.logobserver.nbErrors > 0:
            return FAILURE
        if self.logobserver.nbWarnings > 0:
            return WARNINGS
        else:
            return SUCCESS

    def finished(self, result):
        self.getLog("warnings").finish()
        self.getLog("errors").finish()
        ShellCommand.finished(self, result)
