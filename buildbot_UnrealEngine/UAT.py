from buildbot.steps.shell import ShellCommand
from os import path

class BuildCookRun(ShellCommand):

  renderables = [
    "project_path",
    "engine_path",
    "target_platform",
    "configuration"
  ]

  """Creates build commands for the Unreal Automation Tool"""
  def __init__(self,
      engine_path,
      project_path,
      target_platform="Win64",
      configuration="Development"
      ):
    self.engine_path=engine_path
    self.project_path=project_path
    self.target_platform=target_platform
    self.configuration=configuration
    ShellCommand.__init__(self)

  def start(self):
    command=[ path.join( self.engine_path, "Engine", "Build", "BatchFiles", "RunUAT" )]
    command.append("BuildCookRun")
    command.append("--project={0}".format(self.project_path))
    self.setCommand(command)
    return ShellCommand.start(self)
