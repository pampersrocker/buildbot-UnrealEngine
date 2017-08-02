
from buildbot_UnrealEngine import AutomationTool as UAT
from buildbot.process.properties import Properties, Property

from os import path


import mock

from twisted.internet import defer
from twisted.trial import unittest

from buildbot.test.util import config
from buildbot.test.util import gpo
from buildbot.test.util import logging
from buildbot.test.util import steps
from buildbot.test.util import config as configmixin

from buildbot.test.fake.remotecommand import ExpectShell
from buildbot.test.fake.remotecommand import Expect
from buildbot.process.results import EXCEPTION
from buildbot.process.results import FAILURE
from buildbot.process.results import SKIPPED
from buildbot.process.results import SUCCESS
from buildbot.process.results import WARNINGS


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
    if(compile is True):
        commands.append("-Compile")
    elif(compile is False):
        commands.append("-NoCompile")
    if(cook is True):
        commands.append("-Cook")
    elif(cook is False):
        commands.append("-SkipCook")
    if(cook_on_the_fly is True):
        commands.append("-CookOnTheFly")
    elif(cook_on_the_fly is False):
        commands.append("-SkipCookOnTheFly")
    if(engine_type != "Source"):
        commands.append("-{0}".format(engine_type))
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
    setattr(TestBuildCookRun, "test_TargetPlatform{0}".format(
        platform), targetPlatformTemplate(platform))


def generateTargetConfigurationTest(target_config):
    def targetConfigurationImplementation(self):
        return self.createTest(
            target_config=target_config
        )
    return targetConfigurationImplementation


for config in UAT.BuildCookRun.supported_target_config:
    setattr(TestBuildCookRun, "test_TargetConfiguration{0}".format(
        config), generateTargetConfigurationTest(config))


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
