

from ..UnrealCommand import BaseUnrealCommand

class Build(BaseUnrealCommand):
  """Runs the UnrealBuildTool (UBT)"""
  def __init__(
      self,
      engine_path,
      project_path,
      target,
      target_config="Development",
      target_platform="Win64",
      **kwargs):
    self.target = target
    self.target_config=target_config
    self.target_platform=target_platform
    super(Build, self).__init__(engine_path, project_path, **kwargs)

  def start(self):
    command = [ self.getEngineBatchFilesPath("Build"), self.target, self.target_platform, self.target_config, self.project_path ]
    self.setCommand(command)
    return super(Build, self).start()
