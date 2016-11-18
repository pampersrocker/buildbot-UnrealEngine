
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

from buildbot.test.fake.remotecommand import ExpectShell
from buildbot.process.results import EXCEPTION
from buildbot.process.results import FAILURE
from buildbot.process.results import SKIPPED
from buildbot.process.results import SUCCESS
from buildbot.process.results import WARNINGS

def CreateBuildCookRun():
  build = Properties(
    project_path="Here",
    engine_path="There",
    target_platform="Win64",
    configuration="Development"
  )
  builder = UAT.BuildCookRun(
    project_path=Property("project_path"),
    engine_path=Property("engine_path"),
    target_platform=Property("target_platform"),
    configuration=Property("configuration")
  )
  return build, builder

class TestBuildCookRun(steps.BuildStepMixin, unittest.TestCase):
  def setUp(self):
    return self.setUpBuildStep()

  def tearDown(self):
    return self.tearDownBuildStep()

  def test_Command(self):
    self.setupStep(
      UAT.BuildCookRun("Here", "There")
    )
    self.expectCommands(
      ExpectShell(workdir="wkdir",command=[path.join("Here", "Engine", "Build", "BatchFiles", "RunUAT"), "BuildCookRun", "--project=There"])
      + 0
    )
    self.expectOutcome(result=SUCCESS)
    return self.runStep()
