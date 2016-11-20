
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

  def test_BuildPlatformUnix(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", build_platform="Linux")
    )
    self.expectCommands(
      ExpectShell(workdir="wkdir",
        command=[
          path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.sh"),
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

  def test_BuildPlatformMac(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", build_platform="Mac")
    )
    self.expectCommands(
      ExpectShell(workdir="wkdir",
      command=[
        path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT.command"),
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

  def test_BuildPlatformWindows(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There", build_platform="Windows")
    )
    self.expectCommands(
      ExpectShell(workdir="wkdir",
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

  def test_TargetConfigurationDebug(self):
    target_config="Debug"
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
          "-serverconfig={0}".format(target_config)])
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetConfigurationDevelopment(self):
    target_config="Development"
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
          "-serverconfig={0}".format(target_config)])
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetConfigurationShipping(self):
    target_config="Shipping"
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
          "-serverconfig={0}".format(target_config)])
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetConfigurationTest(self):
    target_config="Test"
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
          "-serverconfig={0}".format(target_config)])
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetConfigInvalid(self):
    self.assertRaisesConfigError(
            "target_config 'Foo' is not supported",
            lambda: UAT.BuildCookRun("Here", "There", target_config="Foo"))
