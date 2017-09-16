#!/usr/bin/env python

from setuptools import setup

long_description = """
buildbot-UnrealEngine
=====================

Documentation
-------------

See https://github.com/pampersrocker/buildbot-UnrealEngine for documentation.
"""

VERSION = "0.3.6"

setup(
    name="buildbot_UnrealEngine",
    version=VERSION,
    description="Easy configuration for the Unreal Automation Tool",
    long_description=long_description,
    author="Marvin Pohl",
    author_email="mp120@hdm-stuttgart.de",
    url="https://github.com/pampersrocker/buildbot-UnrealEngine",
    packages=[
        "buildbot_UnrealEngine",
        "buildbot_UnrealEngine.BuildTool",
        "buildbot_UnrealEngine.AutomationTool",
        "buildbot_UnrealEngine.UnrealCommand"
    ],
    requires=["Buildbot (>=0.9.1)"],
    entry_points={
        'buildbot.steps': [
            'BuildCookRun = buildbot_UnrealEngine.AutomationTool:BuildCookRun',
            'UEBuild = buildbot_UnrealEngine.BuildTool:Build',
            'UERebuild = buildbot_UnrealEngine.BuildTool:Rebuild',
            'UEClean = buildbot_UnrealEngine.BuildTool:Clean',
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C++",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Build Tools",
    ]
)
