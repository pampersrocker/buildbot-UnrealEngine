from buildbot.steps.shell import ShellCommand
from buildbot import config

class BaseUnrealCommand(ShellCommand):

  """
  Base class for all unreal related commands, holds basic parameters:
  - engine_path: Path to the root folder of the used engine
  - project_path: Path to the uproject file of the project used in the build

  In addition some utility functions are provided to help ensure the build parameters are valid
  """

  renderables = [
    "project_path",
    "engine_path",
  ]


  supported_target_platforms = ["Win32", "Win64", "Mac", "XboxOne", "PS4", "IOS", "Android", "HTML5", "Linux", "TVOS"]
  supported_target_config = ["Debug", "Development", "Test", "Shipping"]

  name="BaseUnrealCommand"

  def __init__(
      self,
      engine_path,
      project_path,
      **kwargs):
    self.engine_path = engine_path
    self.project_path = project_path
    ShellCommand.__init__(self, **kwargs)
