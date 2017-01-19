
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
        ending="bat",
        **kwargs):
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
        ending="bat",
        **kwargs):
    return UBT.Build(
        engine_path,
        project_path,
        target,
        do_sanity_checks=do_sanity_checks,
        **kwargs)


def createRebuildCommand(
        engine_path="Here",
        project_path="There",
        target="Target",
        do_sanity_checks=True,
        **kwargs):
    return UBT.Rebuild(
        engine_path,
        project_path,
        target,
        do_sanity_checks=do_sanity_checks,
        **kwargs)


def createCleanCommand(
        engine_path="Here",
        project_path="There",
        target="Target",
        do_sanity_checks=True,
        **kwargs):
    return UBT.Clean(
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

    def createConfigErrorTest(self, message, **kwargs):
        self.assertRaisesConfigError(
            message,
            createBuildCommandLambda(**kwargs)
        )

    def createBuildTest(self, expected=SUCCESS, **kwargs):
        self.setupStep(createBuildCommand(**kwargs))
        self.expectCommands(createExpectedShell(**kwargs))
        self.expectOutcome(result=expected)
        return self.runStep()

    def createRebuildTest(self, expected=SUCCESS, **kwargs):
        self.setupStep(createRebuildCommand(**kwargs))
        self.expectCommands(createExpectedShell(
            build_type="Rebuild",
            **kwargs))
        self.expectOutcome(result=expected)
        return self.runStep()

    def createCleanTest(self, expected=SUCCESS, **kwargs):
        self.setupStep(createCleanCommand(**kwargs))
        self.expectCommands(createExpectedShell(
            build_type="Clean",
            **kwargs))
        self.expectOutcome(result=expected)
        return self.runStep()

    def test_TargetConfigInvalid(self):
        self.createConfigErrorTest(
            "target_config 'Foo' is not supported",
            target_config="Foo"
        )

    def test_BuildTypeInvalid(self):
        self.createConfigErrorTest(
            "build_type 'Foo' is not supported",
            build_type="Foo"
        )

    def test_TargetPlatformInvalid(self):
        self.createConfigErrorTest(
            "target_platform 'Foo' is not supported",
            target_platform="Foo"
        )

    def test_BuildPlatformInvalid(self):
        self.createConfigErrorTest(
            "build_platform 'Foo' is not supported",
            build_platform="Foo"
        )

    def test_EngineTypeInvalid(self):
        self.createConfigErrorTest(
            "engine_type 'Foo' is not supported",
            engine_type="Foo"
        )

    def test_NoSanityChecks(self):
        return self.createBuildTest(
            do_sanity_checks=False,
            target_config="Foo")

    def test_WaitMutex(self):
        return self.createBuildTest(wait_mutex=True)

    def test_NoWaitMutex(self):
        return self.createBuildTest(wait_mutex=False)

    def test_RebuildClass(self):
        return self.createRebuildTest()

    def test_CleanClass(self):
        return self.createCleanTest()


def buildTypeTemplate(build_type):
    def buildTypeImplementation(self):
        return self.createBuildTest(build_type=build_type)
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
        return self.createBuildTest(target_platform=target_platform)
    return targetPlatformImplementation


# Create test functions for all supported platforms
for platform in UBT.Build.supported_target_platforms:
    setattr(
        TestBuild,
        "test_TargetPlatform{0}".format(platform),
        targetPlatformTemplate(platform))


def generateTargetConfigurationTest(target_config):
    def targetConfigurationImplementation(self):
        return self.createBuildTest(target_config=target_config)
    return targetConfigurationImplementation


for config in UBT.Build.supported_target_config:
    setattr(
        TestBuild,
        "test_TargetConfiguration{0}".format(config),
        generateTargetConfigurationTest(config))


def generateBuildPlatformTest(build_platform, ending):
    def BuildPlatformImplementation(self):
        return self.createBuildTest(
            build_platform=build_platform,
            ending=ending)
    return BuildPlatformImplementation


for platform, ending in [
        ("Windows", "bat"), ("Linux", "sh"), ("Mac", "command")]:
    setattr(
        TestBuild,
        "test_BuildPlatform{0}".format(platform),
        generateBuildPlatformTest(platform, ending))
