
from buildbot_UnrealEngine import UAT
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

class TestBuildCookRun(steps.BuildStepMixin, unittest.TestCase, configmixin.ConfigErrorsMixin):
  def setUp(self):
    return self.setUpBuildStep()

  def tearDown(self):
    return self.tearDownBuildStep()

  def test_Command(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There")
    )
    self.expectCommands(
      ExpectShell(
        workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.bat"),
          "BuildCookRun",
          "-project=There",
          "-targetplatform=Win64",
          "-platform=Win64",
          "-clientconfig=Development",
          "-serverconfig=Development"
          ]
        )
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_BuildPlatformInvalid(self):
    self.assertRaisesConfigError(
            "build_platform 'Foo' is not supported",
            lambda: UAT.BuildCookRun("Here", "There", build_platform="Foo"))

  def test_TargetConfigInvalid(self):
    self.assertRaisesConfigError(
            "target_config 'Foo' is not supported",
            lambda: UAT.BuildCookRun("Here", "There", target_config="Foo"))

  def test_TargetPlatformInvalid(self):
    self.assertRaisesConfigError(
            "target_platform 'Foo' is not supported",
            lambda: UAT.BuildCookRun("Here", "There", target_platform="Foo"))

  def test_NoCompileEditor(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", no_compile_editor=True)
    )
    self.expectCommands(
      ExpectShell(
        workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.bat"),
          "BuildCookRun",
          "-project=There",
          "-targetplatform=Win64",
          "-platform=Win64",
          "-clientconfig=Development",
          "-serverconfig=Development",
          "-NoCompileEditor"
        ]
      )
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

def targetPlatformTemplate(target_platform):

  """
  Creates a test function to test if the client and serverconfig is correctly set for the given platform
  """
  def targetPlatformImplementation(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", target_platform=target_platform)
    )
    self.expectCommands(
      ExpectShell(
        workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.bat"),
          "BuildCookRun",
          "-project=There",
          "-targetplatform={0}".format(target_platform),
          "-platform={0}".format(target_platform),
          "-clientconfig=Development",
          "-serverconfig=Development"
        ]
      )
      + 0
    )
  return targetPlatformImplementation

# Create test functions for all supported platforms
for platform in UAT.BuildCookRun.supported_target_platforms:
  setattr(TestBuildCookRun, "test_TargetPlatform{0}".format(platform), targetPlatformTemplate(platform))

def generateTargetConfigurationTest(target_config):
  def targetConfigurationImplementation(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", target_config=target_config)
    )
    self.expectCommands(
      ExpectShell(
        workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.bat"),
          "BuildCookRun",
          "-project=There",
          "-targetplatform=Win64",
          "-platform=Win64",
          "-clientconfig={0}".format(target_config),
          "-serverconfig={0}".format(target_config)]
        )
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()
  return targetConfigurationImplementation

for config in UAT.BuildCookRun.supported_target_config:
  setattr(TestBuildCookRun, "test_TargetConfiguration{0}".format(config), generateTargetConfigurationTest(config))

def generateBuildPlatformTest(build_platform, ending):
  def BuildPlatformImplementation(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", build_platform=build_platform)
    )
    self.expectCommands(
      ExpectShell(workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.{0}".format(ending)),
          "BuildCookRun",
          "-project=There",
          "-targetplatform=Win64",
          "-platform=Win64",
          "-clientconfig=Development",
          "-serverconfig=Development"
        ]
      )
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()
  return BuildPlatformImplementation

for platform, ending in [("Windows", "bat"),("Linux", "sh"),("Mac", "command")]:
  setattr(TestBuildCookRun, "test_BuildPlatform{0}".format(platform), generateBuildPlatformTest(platform, ending))
