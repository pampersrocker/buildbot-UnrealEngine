# -*- test-case-name: buildbot_UnrealEngine.test.test_BuildCookRun -*-
from buildbot.steps.shell import ShellCommand
from buildbot import config

from os import path




class BuildCookRun(ShellCommand):

  """
  Creates a command like
  <Path to Engine>\Engine\Build\BatchFiles\RunUAT.bat BuildCookRun -project=<ProjectPath> -noP4 -nocompileeditor
  -targetplatform=<Platform> -platform=<Platform> -clientconfig=<TargetConfig> -serverconfig=<TargetConfig>
  -cook -allmaps -compile -stage -pak -archive -archivedirectory=<ArchivePath> -Build -prereqs -package
  """

  supported_target_platforms = ["Win32", "Win64", "Mac", "XboxOne", "PS4", "IOS", "Android", "HTML5", "Linux", "AllDesktop", "TVOS"]
  supported_target_config = ["Debug", "Development", "Test", "Shipping"]

  renderables = [
    "project_path",
    "engine_path",
    "target_platform",
    "target_config",
    "build_platform"
  ]

  def __init__(self,
      engine_path,
      project_path,
      target_platform="Win64",
      target_config="Development",
      build_platform="Windows",
      no_compile_editor=False,
      compile=None,
      cook=None,
      cook_on_the_fly=None,
      build=False,
      #maps=True,
      **kwargs):
    self.engine_path=engine_path
    self.project_path=project_path
    self.target_platform=target_platform
    self.target_config=target_config
    self.build_platform=build_platform
    self.no_compile_editor=no_compile_editor
    self.compile=compile
    self.cook=cook
    self.cook_on_the_fly=cook_on_the_fly
    #self.build is apparently used somhwere internally for something else
    self.build_step=build
    if target_config not in self.supported_target_config:
      config.error("target_config '{0}' is not supported".format(self.target_config))
    if target_platform not in self.supported_target_platforms:
      config.error("target_platform '{0}' is not supported".format(self.target_platform))
    if build_platform not in ["Windows", "Linux", "Mac"]:
      config.error("build_platform '{0}' is not supported".format(self.build_platform))
    ShellCommand.__init__(self, **kwargs)

  def getPlatformScriptExtension(self):
    if self.build_platform == "Windows":
      return "bat"
    elif self.build_platform == "Linux":
      return "sh"
    elif self.build_platform == "Mac":
      return "command"


  def start(self):

    def addArgIfSet(flag, commandList, ifTrue, ifFalse):
      if flag == True:
        commandList.append(ifTrue)
      elif flag == False:
        commandList.append(ifFalse)
    command=[ path.join( self.engine_path, "Engine", "Build", "BatchFiles", "RunUAT.{0}".format(self.getPlatformScriptExtension()) )]
    command.append("BuildCookRun")
    command.append("-project={0}".format(self.project_path))
    command.append("-targetplatform={0}".format(self.target_platform))
    command.append("-platform={0}".format(self.target_platform))
    command.append("-clientconfig={0}".format(self.target_config))
    command.append("-serverconfig={0}".format(self.target_config))
    if self.no_compile_editor:
      command.append("-NoCompileEditor")
    addArgIfSet(self.compile, command, "-Compile", "-NoCompile")
    addArgIfSet(self.cook, command, "-Cook", "-SkipCook")
    addArgIfSet(self.cook_on_the_fly, command, "-CookOnTheFly", "-SkipCookOnTheFly")
    if self.build_step == True:
      command.append("-Build")
    self.setCommand(command)
    return ShellCommand.start(self)
