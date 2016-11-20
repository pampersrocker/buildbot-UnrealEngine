
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

  def test_TargetPlatformInvalid(self):
    self.assertRaisesConfigError(
            "target_platform 'Foo' is not supported",
            lambda: UAT.BuildCookRun("Here", "There", target_platform="Foo"))


  def test_TargetPlatformWin32(self):
    target_platform="Win32"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformWin64(self):
    target_platform="Win64"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformMac(self):
    target_platform="Mac"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformXboxOne(self):
    target_platform="XboxOne"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformPS4(self):
    target_platform="PS4"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformIOS(self):
    target_platform="IOS"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformAndroid(self):
    target_platform="Android"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformHTML5(self):
    target_platform="HTML5"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformLinux(self):
    target_platform="Linux"
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
    self.expectOutcome(result=SUCCESS)
    return self.runStep()

  def test_TargetPlatformTVOS(self):
    target_platform="TVOS"
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

    self.expectOutcome(result=SUCCESS)
    return self.runStep()
