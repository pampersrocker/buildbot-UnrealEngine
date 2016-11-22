#!/usr/bin/env python

from setuptools import setup

setup(
    name="buildbot_UnrealEngine",
    version="0.0.1",
    description="Easy configuration for the Unreal Automation Tool",
    author="Marvin Pohl",
    author_email="mp120@hdm-stuttgart.de",
    url="https://github.com/pampersrocker/ue4-buildbot",
    packages=["buildbot_UnrealEngine"],
    requires=["Buildbot (==0.9.1)"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points= {
      'buildbot.steps': [
        'BuildCookRun = buildbot_UnrealEngine.UAT.BuildCookRun'
      ]
    }
)
