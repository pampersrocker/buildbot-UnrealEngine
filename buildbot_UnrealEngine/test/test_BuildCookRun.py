# -*- coding: utf-8 -*-

from buildbot_UnrealEngine import AutomationTool as UAT
from buildbot.process.properties import Properties, Property, IRenderable

from os import path


from mock import Mock

from twisted.internet import defer
from twisted.trial import unittest

from buildbot.test.util import config
from buildbot.test.util import gpo
from buildbot.test.util import logging
from buildbot.test.util import steps
from buildbot.test.util import config as configmixin
from buildbot.test.util.properties import ConstantRenderable

from buildbot.test.fake.remotecommand import ExpectShell
from buildbot.test.fake.remotecommand import Expect
from buildbot.process.results import EXCEPTION
from buildbot.process.results import FAILURE
from buildbot.process.results import SKIPPED
from buildbot.process.results import SUCCESS
from buildbot.process.results import WARNINGS

constant_true = ConstantRenderable(True)
constant_false = ConstantRenderable(False)


class TestBuildCookRunLogLineObserver(unittest.TestCase):

    def setUp(self):
        self.warnings = []
        mocked_warnings = Mock()
        mocked_warnings.addStdout = lambda l: self.warnings.append(l.rstrip())

        self.cook = []
        mocked_cook = Mock()
        mocked_cook.addStdout = lambda l: self.cook.append(l.rstrip())

        self.errors = []
        self.errors_stderr = []
        mocked_errors = Mock()
        mocked_errors.addStdout = \
            lambda l: self.errors.append(('o', l.rstrip()))
        mocked_errors.addStderr = \
            lambda l: self.errors.append(('e', l.rstrip()))

        self.unreal_log_observer = \
            UAT.BuildCookRunLogLineObserver()

        self.progress = {}
        self.unreal_log_observer.step = Mock()
        mockedLogs = {
            "warnings": mocked_warnings,
            "errors": mocked_errors,
            "cook": mocked_cook
        }

        def logReturner(logName):
            return mockedLogs.get(logName)
        self.unreal_log_observer.step.getLog = logReturner

        self.unreal_log_observer.step.setProgress = \
            lambda n, prog: self.progress.__setitem__(n, prog)
        self.maxDiff = None

    def receiveLines(self, *lines):
        for line in lines:
            self.unreal_log_observer.outLineReceived(line)

    def assertResult(self, nbCook=0, nbWarnings=0, nbErrors=0,
                     errors=[], warnings=[], cook=[], progress={}):
        self.assertEqual(
            dict(
                nbCook=self.unreal_log_observer.nbCook,
                nbWarnings=self.unreal_log_observer.nbWarnings,
                nbErrors=self.unreal_log_observer.nbErrors,
                errors=self.errors,
                warnings=self.warnings,
                progress=self.progress,
                cook=self.cook),
            dict(
                nbCook=nbCook,
                nbWarnings=nbWarnings,
                nbErrors=nbErrors,
                errors=errors,
                warnings=warnings,
                progress=progress,
                cook=cook))

    def test_NoLinesReceived(self):
        self.unreal_log_observer.outLineReceived("random text\r\n")
        self.assertResult()

    def test_OtherWarningReceived_4_15_(self):
        lines = [
            u"UE4Editor-Cmd: [2017.08.02-13.26.13:327][  0]LogLinker:Warning: Can't find file '/Game/Test/Some/Asset'",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbWarnings=1,
            nbCook=0,
            warnings=lines,
            progress=dict(warnings=1))

    def test_OtherWarningReceived_4_17_(self):
        lines = [
            u"Cook: LogScriptCore: Warning: Script Msg: Attempted to set an invalid index on array MaterialInstances [0/0]!",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbWarnings=1,
            nbCook=0,
            warnings=lines,
            progress=dict(warnings=1))

    def test_CookWarningReceived_4_15(self):
        lines = [
            u"UE4Editor-Cmd: [2017.08.02-13.27.51:616][  0]LogCook:Warning: Unable to find cached package name for package /Game/Some/Asset/Reference",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbWarnings=1,
            warnings=lines,
            cook=lines,
            progress=dict(warnings=1))

    def test_CookReceived_4_15_(self):
        lines = [
            u"UE4Editor-Cmd: [2017.08.02-02.00.00:394][  0]LogCook:Display: Cooking /Game/SomeAssetReference -> C:/Path/To/Saved/Cooked/Win64/Project/Content/SomeAssetReference.uasset",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbCook=1,
            cook=lines,
            progress=dict(cook=1))

    def test_CookReceived_4_17_(self):
        lines = [
            u"Cook: LogCook: Display: Cooking /Game/SomeAssetReference -> C:/Path/To/Saved/Cooked/Win64/Project/Content/SomeAssetReference.uasset",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbCook=1,
            cook=lines,
            progress=dict(cook=1))

    def test_UnicodeReceived(self):
        lines = [
            u"UE4Editor-Cmd: [2017.08.05-22.28.46:306][  0]LogCook:Display: Cooking /Game/stahlträger_LOW_N -> C:/Path/To/Saved/Cooked/Win64/Project/Content/stahlträger_LOW_N.uasset",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbCook=1,
            cook=lines,
            progress=dict(cook=1))

    def test_UnicodeErrorReceived(self):
        lines = [
            r"C:\Path\ToRepo\Source\Component.cpp(45): error C4003: ää not enough actual parameters for macro 'ensureAlwaysMsgf'",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbErrors=1,
            errors=[('e', l) for l in lines]
        )

    def test_ErrorReceived(self):
        lines = [
            r"C:\Path\ToRepo\Source\Component.cpp(45): error C4003: not enough actual parameters for macro 'ensureAlwaysMsgf'",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbErrors=1,
            errors=[('e', l) for l in lines]
        )

    def test_ErrorReceived_4_17(self):
        lines = [
            u"Cook: LogBlueprint: Error: [Compiler SomeGameAsset] The property associated with  SomeComponent  could not be found from Source: /Game/Props/SomeAssetReference/",
        ]
        self.receiveLines(*lines)
        self.assertResult(
            nbErrors=1,
            errors=[('e', l) for l in lines]
        )


def renderableIsValue(renderable, value):
    try:
        return renderable.getRenderingFor(None) == value
    except AttributeError:
        return False


def getRenderableOrValue(renderable):
    try:
        return renderable.getRenderingFor(None)
    except:
        return renderable


def createExpectedShell(
        engine_path="Here",
        project_path="There/Project.uproject",
        target_config="Development",
        extra_arguments=None,
        target_platform="Win64",
        ending="bat",
        engine_type="Rocket",
        compile=None,
        cook=None,
        cook_on_the_fly=None,
        **kwargs):
    target_platform = getRenderableOrValue(target_platform)
    target_platform = "+".join(target_platform) if isinstance(target_platform, list) else target_platform
    target_config = getRenderableOrValue(target_config)
    target_config = "+".join(target_config) if isinstance(target_config, list) else target_config
    commands = [
        path.join(
            engine_path,
            "Engine",
            "Build",
            "BatchFiles",
            "RunUAT.{0}".format(ending)),
        "BuildCookRun",
        "-project={0}".format(project_path),
        "-targetplatform={0}".format(target_platform),
        "-platform={0}".format(target_platform),
        "-clientconfig={0}".format(target_config),
        "-serverconfig={0}".format(target_config)
    ]
    if(engine_type != "Source"):
        commands.append("-{0}".format(engine_type))
    if(compile is True or renderableIsValue(compile, True)):
        commands.append("-Compile")
    elif(compile is False or renderableIsValue(compile, False)):
        commands.append("-NoCompile")
    if(cook is True or renderableIsValue(cook, True)):
        commands.append("-Cook")
    elif(cook is False or renderableIsValue(cook, False)):
        commands.append("-SkipCook")
    if(cook_on_the_fly is True or renderableIsValue(cook_on_the_fly, True)):
        commands.append("-CookOnTheFly")
    elif(cook_on_the_fly is False or
         renderableIsValue(cook_on_the_fly, False)):
        commands.append("-SkipCookOnTheFly")
    if(extra_arguments is not None):
        commands.extend(extra_arguments)
    return ExpectShell(
        workdir="wkdir",
        command=commands
    ) + 0


def createBuildCommand(
        engine_path="Here", project_path="There/Project.uproject", **kwargs):
    return UAT.BuildCookRun(engine_path, project_path, **kwargs)


class TestBuildCookRun(
        steps.BuildStepMixin,
        unittest.TestCase,
        configmixin.ConfigErrorsMixin):
    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def createTest(
            self,
            extra_arguments=None,
            expected=SUCCESS,
            ending="bat",
            **kwargs):
        self.setupStep(
            UAT.BuildCookRun("Here", "There/Project.uproject", **kwargs)
        )
        self.expectCommands(
            createExpectedShell(
                extra_arguments=extra_arguments,
                ending=ending,
                **kwargs)
        )
        self.expectOutcome(result=expected)
        return self.runStep()

    def createConfigErrorTest(self, message, **kwargs):
        return self.assertRaisesConfigError(
            message,
            lambda: createBuildCommand(**kwargs)
        )

    def test_Command(self):
        return self.createTest()

    def test_InvalidCommand_NoSanityChecks(self):
        return self.createTest(engine_type="Foo", do_sanity_checks=False)

    def test_BuildPlatformInvalid(self):
        return self.createConfigErrorTest(
            "build_platform 'Foo' is not supported",
            build_platform="Foo"
        )

    def test_TargetConfigInvalid(self):
        return self.createConfigErrorTest(
            "target_config 'Foo' is not supported",
            target_config="Foo"
        )

    def test_TargetPlatformInvalid(self):
        return self.createConfigErrorTest(
            "target_platform 'Foo' is not supported",
            target_platform="Foo"
        )

    def test_Build(self):
        return self.createTest(build=True, extra_arguments=["-Build"])

    def test_NoBuild(self):
        return self.createTest(build=False)

    def test_Clean(self):
        return self.createTest(clean=True, extra_arguments=["-Clean"])

    def test_NoClean(self):
        return self.createTest(clean=False)

    def test_EngineTypeInvalid(self):
        return self.createConfigErrorTest(
            "engine_type 'Foo' is not supported",
            engine_type="Foo"
        )

    def test_EngineTypeInstalled(self):
        return self.createTest(engine_type="Installed")

    def test_EngineTypeRocket(self):
        return self.createTest(engine_type="Rocket")

    def test_EngineTypeSource(self):
        return self.createTest(engine_type="Source")

    def test_NoCompileEditor(self):
        return self.createTest(
            no_compile_editor=True,
            extra_arguments=["-NoCompileEditor"]
        )

    def test_Compile(self):
        return self.createTest(
            compile=True
        )

    def test_NoCompile(self):
        return self.createTest(
            compile=False
        )

    def test_SkipCook(self):
        return self.createTest(
            cook=False
        )

    def test_Cook(self):
        return self.createTest(
            cook=True
        )

    def test_SkipCookOnTheFly(self):
        return self.createTest(
            cook_on_the_fly=False
        )

    def test_CookOnTheFly(self):
        return self.createTest(
            cook_on_the_fly=True
        )

    def test_Archive(self):
        return self.createTest(archive=True, extra_arguments=["-Archive"])

    def test_NoArchive(self):
        return self.createTest(archive=False)

    def test_ArhiveDirectory(self):
            return self.createTest(
                archive_directory="There/Archive",
                extra_arguments=["-ArchiveDirectory=There/Archive"])

    def test_P4(self):
        return self.createTest(p4=True, extra_arguments=["-P4"])

    def test_NoP4(self):
        return self.createTest(p4=False, extra_arguments=["-NoP4"])

    def test_UnversionedCookedConted(self):
        return self.createTest(
            unversioned_cooked_content=True,
            extra_arguments=["-UnversionedCookedContent"])

    def test_EncryptIniFiles(self):
        return self.createTest(
            encrypt_ini_files=True,
            extra_arguments=["-EncryptIniFiles"]
        )

    def test_CreateReleaseVersion(self):
        return self.createTest(
            release_version="v1.2.3",
            extra_arguments=["-CreateReleaseVersion=v1.2.3"]
        )

    def test_BasedOnReleaseVersion(self):
        return self.createTest(
            base_version="v1.2.3",
            extra_arguments=["-BasedOnReleaseVersion=v1.2.3"]
        )

    def test_Compressed(self):
        return self.createTest(
            compressed=True,
            extra_arguments=["-Compressed"]
        )

    def test_Distribution(self):
        return self.createTest(
            distribution=True,
            extra_arguments=["-Distribution"]
        )

    def test_Iterate(self):
        return self.createTest(
            iterate=True,
            extra_arguments=["-Iterate"]
        )

    def test_Run(self):
        return self.createTest(
            run=True,
            extra_arguments=["-Run"]
        )

    def test_RunDevices(self):
        return self.createTest(
            devices=["PCA", "ConsoleB", "MobileC"],
            extra_arguments=["-Device=PCA+ConsoleB+MobileC"]
        )

    def test_NullRHI(self):
        return self.createTest(
            null_rhi=True,
            extra_arguments=["-NullRHI"]
        )

    def test_Nativize(self):
        return self.createTest(
            nativize=True,
            extra_arguments=["-NativizeAssets"]
        )

    def test_Stage(self):
        return self.createTest(
            stage=True,
            extra_arguments=["-Stage"]
        )

    def test_Map(self):
        return self.createTest(
            map=["MapA", "MapB", "MapC"],
            extra_arguments=["-Map=MapA+MapB+MapC"]
        )

    def test_Pak(self):
        return self.createTest(
            pak=True,
            extra_arguments=["-Pak"]
        )

    def test_Prereqs(self):
        return self.createTest(
            prereqs=True,
            extra_arguments=["-Prereqs"]
        )

    def test_Package(self):
        return self.createTest(
            package=True,
            extra_arguments=["-Package"]
        )

    def test_CrashReporter(self):
        return self.createTest(
            crash_reporter=True,
            extra_arguments=["-CrashReporter"]
        )

    def test_Verbose(self):
        return self.createTest(
            verbose=True,
            extra_arguments=["-Verbose"]
        )

    def test_TitleIdMulti(self):
        return self.createTest(
            title_id=["Title_ID_A", "Title_ID_B", "Title_ID_C"],
            extra_arguments=["-TitleID=Title_ID_A+Title_ID_B+Title_ID_C"],
        )

    def test_TitleId(self):
        return self.createTest(
            title_id="Title_ID_A",
            extra_arguments=["-TitleID=Title_ID_A"],
        )

    # Renderables
    def test_Build_Renderable(self):
        return self.createTest(build=constant_true, extra_arguments=["-Build"])

    def test_NoBuild_Renderable(self):
        return self.createTest(build=constant_false)

    def test_Clean_Renderable(self):
        return self.createTest(clean=constant_true, extra_arguments=["-Clean"])

    def test_NoClean_Renderable(self):
        return self.createTest(clean=constant_false)

    def test_EngineTypeInstalled_Renderable(self):
        return self.createTest(engine_type=ConstantRenderable("Installed"))

    def test_EngineTypeRocket_Renderable(self):
        return self.createTest(engine_type=ConstantRenderable("Rocket"))

    def test_EngineTypeSource_Renderable(self):
        return self.createTest(engine_type=ConstantRenderable("Source"))

    def test_NoCompileEditor_Renderable(self):
        return self.createTest(
            no_compile_editor=constant_true,
            extra_arguments=["-NoCompileEditor"]
        )

    def test_Compile_Renderable(self):
        return self.createTest(
            compile=constant_true
        )

    def test_NoCompile_Renderable(self):
        return self.createTest(
            compile=constant_false
        )

    def test_SkipCook_Renderable(self):
        return self.createTest(
            cook=constant_false
        )

    def test_Cook_Renderable(self):
        return self.createTest(
            cook=constant_true
        )

    def test_SkipCookOnTheFly_Renderable(self):
        return self.createTest(
            cook_on_the_fly=constant_false
        )

    def test_CookOnTheFly_Renderable(self):
        return self.createTest(
            cook_on_the_fly=constant_true
        )

    def test_Archive_Renderable(self):
        return self.createTest(
            archive=constant_true, extra_arguments=["-Archive"])

    def test_NoArchive_Renderable(self):
        return self.createTest(archive=constant_false)

    def test_ArhiveDirectory_Renderable(self):
            return self.createTest(
                archive_directory=ConstantRenderable("There/Archive"),
                extra_arguments=["-ArchiveDirectory=There/Archive"])

    def test_P4_Renderable(self):
        return self.createTest(p4=constant_true, extra_arguments=["-P4"])

    def test_NoP4_Renderable(self):
        return self.createTest(p4=constant_false, extra_arguments=["-NoP4"])

    def test_UnversionedCookedConted_Renderable(self):
        return self.createTest(
            unversioned_cooked_content=constant_true,
            extra_arguments=["-UnversionedCookedContent"])

    def test_EncryptIniFiles_Renderable(self):
        return self.createTest(
            encrypt_ini_files=constant_true,
            extra_arguments=["-EncryptIniFiles"]
        )

    def test_CreateReleaseVersion_Renderable(self):
        return self.createTest(
            release_version=ConstantRenderable("v1.2.3"),
            extra_arguments=["-CreateReleaseVersion=v1.2.3"]
        )

    def test_BasedOnReleaseVersion_Renderable(self):
        return self.createTest(
            base_version=ConstantRenderable("v1.2.3"),
            extra_arguments=["-BasedOnReleaseVersion=v1.2.3"]
        )

    def test_Compressed_Renderable(self):
        return self.createTest(
            compressed=constant_true,
            extra_arguments=["-Compressed"]
        )

    def test_Distribution_Renderable(self):
        return self.createTest(
            distribution=constant_true,
            extra_arguments=["-Distribution"]
        )

    def test_Iterate_Renderable(self):
        return self.createTest(
            iterate=constant_true,
            extra_arguments=["-Iterate"]
        )

    def test_Run_Renderable(self):
        return self.createTest(
            run=constant_true,
            extra_arguments=["-Run"]
        )

    def test_RunDevices_Renderable(self):
        return self.createTest(
            devices=ConstantRenderable(["PCA", "ConsoleB", "MobileC"]),
            extra_arguments=["-Device=PCA+ConsoleB+MobileC"]
        )

    def test_NullRHI_Renderable(self):
        return self.createTest(
            null_rhi=constant_true,
            extra_arguments=["-NullRHI"]
        )

    def test_Nativize_Renderable(self):
        return self.createTest(
            nativize=constant_true,
            extra_arguments=["-NativizeAssets"]
        )

    def test_Stage_Renderable(self):
        return self.createTest(
            stage=constant_true,
            extra_arguments=["-Stage"]
        )

    def test_Map_Renderable(self):
        return self.createTest(
            map=ConstantRenderable(["MapA", "MapB", "MapC"]),
            extra_arguments=["-Map=MapA+MapB+MapC"]
        )

    def test_Pak_Renderable(self):
        return self.createTest(
            pak=constant_true,
            extra_arguments=["-Pak"]
        )

    def test_Prereqs_Renderable(self):
        return self.createTest(
            prereqs=constant_true,
            extra_arguments=["-Prereqs"]
        )

    def test_Package_Renderable(self):
        return self.createTest(
            package=constant_true,
            extra_arguments=["-Package"]
        )

    def test_CrashReporter_Renderable(self):
        return self.createTest(
            crash_reporter=constant_true,
            extra_arguments=["-CrashReporter"]
        )

    def test_TitleIdMulti_Renderable(self):
        return self.createTest(
            title_id=ConstantRenderable(
                ["Title_ID_A", "Title_ID_B", "Title_ID_C"]),
            extra_arguments=["-TitleID=Title_ID_A+Title_ID_B+Title_ID_C"],
        )

    def test_TitleId_Renderable(self):
        return self.createTest(
            title_id=ConstantRenderable("Title_ID_A"),
            extra_arguments=["-TitleID=Title_ID_A"],
        )

    def test_TargetPlatformMulti_Renderable(self):
        return self.createTest(
            target_platform=ConstantRenderable(["Win64", "PS4"]),
        )
    def test_TargetConfigMulti_Renderable(self):
        return self.createTest(
            target_config=ConstantRenderable(["Development", "Shipping"]),
        )


def targetPlatformTemplate(target_platform):
    """
    Creates a test function to test if the client
    and serverconfig is correctly set for the given platform
    """

    def targetPlatformImplementation(self):
        return self.createTest(
            target_platform=target_platform
        )
    return targetPlatformImplementation


# Create test functions for all supported platforms
for platform in UAT.BuildCookRun.supported_target_platforms:
    setattr(TestBuildCookRun, "test_TargetPlatform_{0}".format(
        platform), targetPlatformTemplate(platform))

def targetPlatformTemplateRenderable(target_platform):
    """
    Creates a test function to test if the client
    and serverconfig is correctly set for the given platform using a renderable
    """

    def targetPlatformImplementation(self):
        return self.createTest(
            target_platform=ConstantRenderable(target_platform)
        )
    return targetPlatformImplementation

# Create test functions for all supported platforms
for platform in UAT.BuildCookRun.supported_target_platforms:
    setattr(TestBuildCookRun, "test_TargetPlatformRenderable_{0}".format(
        platform), targetPlatformTemplateRenderable(platform))


def generateTargetConfigurationTest(target_config):
    def targetConfigurationImplementation(self):
        return self.createTest(
            target_config=target_config
        )
    return targetConfigurationImplementation


for config in UAT.BuildCookRun.supported_target_config:
    setattr(TestBuildCookRun, "test_TargetConfiguration_{0}".format(
        config), generateTargetConfigurationTest(config))

def generateTargetConfigurationTestRenderable(target_config):
    def targetConfigurationImplementation(self):
        return self.createTest(
            target_config=ConstantRenderable(target_config)
        )
    return targetConfigurationImplementation


for config in UAT.BuildCookRun.supported_target_config:
    setattr(TestBuildCookRun, "test_TargetConfigurationRenderable_{0}".format(
        config), generateTargetConfigurationTestRenderable(config))


def generateBuildPlatformTest(build_platform, ending):
    def BuildPlatformImplementation(self):
        return self.createTest(
            build_platform=build_platform,
            ending=ending
        )
    return BuildPlatformImplementation


for platform, ending in [
        ("Windows", "bat"), ("Linux", "sh"), ("Mac", "command")]:
    setattr(TestBuildCookRun, "test_BuildPlatform{0}".format(
        platform), generateBuildPlatformTest(platform, ending))
