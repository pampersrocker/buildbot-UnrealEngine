from buildbot.steps.shell import ShellCommand

class BuildCookRun(ShellCommand):

  renderables = [
    "project_path",
    "engine_path",
    "target_platform",
    "configuration"
  ]

  """Creates build commands for the Unreal Automation Tool"""
  def __init__(self,
      project_path,
      engine_path,
      target_platform="Win64",
      configuration="Development",
      **kwargs
      ):
    self.engine_path=engine_path
    self.project_path=project_path
    self.target_platform=target_platform
    self.configuration=configuration
    ShellCommand.__init__(self, **kwargs)
