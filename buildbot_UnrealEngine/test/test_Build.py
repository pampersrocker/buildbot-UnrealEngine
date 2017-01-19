
from buildbot_UnrealEngine import BuildTool as UBT
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
        project_path="There",
        target="Target",
        target_config="Development",
        extra_arguments=None,
        wait_mutex=True,
        build_type="Build",
        target_platform="Win64",
        ending="bat"):
    commands = [
        path.join(
            engine_path,
            "Engine",
            "Build",
            "BatchFiles",
            "{0}.{1}".format(build_type, ending)),
        target,
        target_platform,
        target_config,
        project_path,
    ]
    if(wait_mutex):
        commands.append("-WaitMutex")
    if(extra_arguments is not None):
        commands.extend(extra_arguments)
    return ExpectShell(
        workdir="wkdir",
        command=commands
    ) + 0


def createBuildCommand(
        engine_path="Here",
        project_path="There",
        target="Target",
        do_sanity_checks=True,
        **kwargs):
    return UBT.Build(
        engine_path,
        project_path,
        target,
        do_sanity_checks=do_sanity_checks,
        **kwargs)


def createBuildCommandLambda(
        engine_path="Here",
        project_path="There",
        target="Target",
        do_sanity_checks=True,
        **kwargs):
    return lambda: createBuildCommand(
        engine_path,
        project_path,
        target,
        do_sanity_checks=do_sanity_checks,
        **kwargs)


class TestBuild(
        steps.BuildStepMixin,
        unittest.TestCase,
        configmixin.ConfigErrorsMixin):

    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def test_TargetConfigInvalid(self):
        self.assertRaisesConfigError(
            "target_config 'Foo' is not supported",
            createBuildCommandLambda(
                target_config="Foo"
            )
        )

    def test_TargetPlatformInvalid(self):
        self.assertRaisesConfigError(
            "target_platform 'Foo' is not supported",
            createBuildCommandLambda(
                target_platform="Foo"
            )
        )

    def test_BuildPlatformInvalid(self):
        self.assertRaisesConfigError(
            "build_platform 'Foo' is not supported",
            createBuildCommandLambda(
                build_platform="Foo"
            )
        )

    def test_EngineTypeInvalid(self):
        self.assertRaisesConfigError(
            "engine_type 'Foo' is not supported",
            createBuildCommandLambda(
                engine_type="Foo"
            )
        )

    def test_NoSanityChecks(self):
        self.setupStep(
            createBuildCommand(
                do_sanity_checks=False,
                target_config="Foo")
        )
        self.expectCommands(
            createExpectedShell(target_config="Foo")
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()

    def test_WaitMutex(self):
        self.setupStep(
            createBuildCommand(wait_mutex=True)
        )
        self.expectCommands(
            createExpectedShell(wait_mutex=True)
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()

    def test_NoWaitMutex(self):
        self.setupStep(
            UBT.Build("Here", "There", "Target", wait_mutex=False)
        )
        self.expectCommands(
            createExpectedShell(wait_mutex=False)
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()

    def test_RebuildClass(self):
        self.setupStep(
            UBT.Rebuild("Here", "There", "Target")
        )
        self.expectCommands(
            createExpectedShell(build_type="Rebuild")
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()

    def test_CleanClass(self):
        self.setupStep(
            UBT.Clean("Here", "There", "Target")
        )
        self.expectCommands(
            createExpectedShell(build_type="Clean")
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()


def buildTypeTemplate(build_type):
    def buildTypeImplementation(self):
        self.setupStep(
            UBT.Build("Here", "There", "Target", build_type=build_type)
        )
        self.expectCommands(
            createExpectedShell(build_type=build_type)
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()
    return buildTypeImplementation


# Create test functions for all supported platforms
for build_type in UBT.Build.supported_build_types:
    setattr(
        TestBuild,
        "test_BuildType{0}".format(build_type),
        buildTypeTemplate(build_type))


def targetPlatformTemplate(target_platform):

    """
    Creates a test function to test if the client
    and serverconfig is correctly set for the given platform
    """
    def targetPlatformImplementation(self):
        self.setupStep(
            createBuildCommand(target_platform=target_platform)
        )
        self.expectCommands(
            createExpectedShell(target_platform=target_platform)
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()
    return targetPlatformImplementation


# Create test functions for all supported platforms
for platform in UBT.Build.supported_target_platforms:
    setattr(
        TestBuild,
        "test_TargetPlatform{0}".format(platform),
        targetPlatformTemplate(platform))


def generateTargetConfigurationTest(target_config):
    def targetConfigurationImplementation(self):
        self.setupStep(
            createBuildCommand(target_config=target_config)
        )
        self.expectCommands(
            createExpectedShell(target_config=target_config)
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()
    return targetConfigurationImplementation


for config in UBT.Build.supported_target_config:
    setattr(
        TestBuild,
        "test_TargetConfiguration{0}".format(config),
        generateTargetConfigurationTest(config))


def generateBuildPlatformTest(build_platform, ending):
    def BuildPlatformImplementation(self):
        self.setupStep(
            createBuildCommand(build_platform=build_platform)
        )
        self.expectCommands(
            createExpectedShell(ending=ending)
        )
        self.expectOutcome(result=SUCCESS)
        return self.runStep()
    return BuildPlatformImplementation


for platform, ending in[
        ("Windows", "bat"), ("Linux", "sh"), ("Mac", "command")]:
    setattr(
        TestBuild,
        "test_BuildPlatform{0}".format(platform),
        generateBuildPlatformTest(platform, ending))
