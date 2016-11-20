
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

class TestBuildCookRunTargetPlatforms(steps.BuildStepMixin, unittest.TestCase, configmixin.ConfigErrorsMixin):
  def setUp(self):
    return self.setUpBuildStep()

  def tearDown(self):
    return self.tearDownBuildStep()

  def test_TargetPlatformInvalid(self):
    self.assertRaisesConfigError(
            "target_platform 'Foo' is not supported",
            lambda: UAT.BuildCookRun("Here", "There", target_platform="Foo"))

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
  setattr(TestBuildCookRunTargetPlatforms, "test_TargetPlatform{0}".format(platform), targetPlatformTemplate(platform))
