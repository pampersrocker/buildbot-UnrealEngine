
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

class TestBuild(steps.BuildStepMixin, unittest.TestCase, configmixin.ConfigErrorsMixin):
  def setUp(self):
    return self.setUpBuildStep()

  def tearDown(self):
    return self.tearDownBuildStep()


def targetPlatformTemplate(target_platform):

  """
  Creates a test function to test if the client and serverconfig is correctly set for the given platform
  """
  def targetPlatformImplementation(self):
    self.setupStep(
      UBT.Build("Here", "There", "Target", target_platform=target_platform)
    )
    self.expectCommands(
      ExpectShell(
        workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "Build.bat"),
          "Target",
          target_platform,
          "Development"
          "There",
        ]
      )
      + 0
    )
  return targetPlatformImplementation

# Create test functions for all supported platforms
for platform in UBT.Build.supported_target_platforms:
  setattr(TestBuild, "test_TargetPlatform{0}".format(platform), targetPlatformTemplate(platform))

def generateTargetConfigurationTest(target_config):
  def targetConfigurationImplementation(self):
    self.setupStep(
      UBT.Build("Here", "There", "Target", target_config=target_config)
    )
    self.expectCommands(
      ExpectShell(
        workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "Build.bat"),
          "Target",
          "Win64",
          target_config,
          "There",
        ]
      )
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()
  return targetConfigurationImplementation

for config in UBT.Build.supported_target_config:
  setattr(TestBuild, "test_TargetConfiguration{0}".format(config), generateTargetConfigurationTest(config))

def generateBuildPlatformTest(build_platform, ending):
  def BuildPlatformImplementation(self):
    self.setupStep(
      UBT.Build("Here", "There", "Target", build_platform=build_platform)
    )
    self.expectCommands(
      ExpectShell(workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "Build.{0}".format(ending)),
          "Target",
          "Win64",
          "Development",
          "There"
        ]
      )
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()
  return BuildPlatformImplementation

for platform, ending in [("Windows", "bat"),("Linux", "sh"),("Mac", "command")]:
  setattr(TestBuild, "test_BuildPlatform{0}".format(platform), generateBuildPlatformTest(platform, ending))
