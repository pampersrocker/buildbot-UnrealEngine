#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = "1.3.0"

setup(
    name="buildbot_UnrealEngine",
    version=VERSION,
    description="Easy configuration for the Unreal Automation Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marvin Pohl",
    author_email="marvin@lab132.com",
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
        "Development Status :: 5 - Production/Stable",
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
