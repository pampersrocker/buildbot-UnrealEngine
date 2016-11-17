
from UE4BuildBot import UAT

class TestUE4BuildBot():
  def test_creation(self):
    project_path="Here"
    engine_path="There"
    target_platform="Win64"
    configuration="Development"

    ueBuilder = UAT.BuildCookRun(
      project_path=project_path,
      engine_path=engine_path,
      target_platform=target_platform,
      configuration=configuration
    )
    assert(ueBuilder is not None)
    assert(ueBuilder.engine_path == engine_path)
    assert(ueBuilder.project_path == project_path)
    assert(ueBuilder.target_platform==target_platform)
    assert(ueBuilder.configuration==configuration)
