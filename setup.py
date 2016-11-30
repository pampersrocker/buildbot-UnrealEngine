#!/usr/bin/env python

from setuptools import setup

long_description ="""
=========
buildbot-UnrealEngine
=========

For documentation see: `Project Homepage`_

.. _Project Homepage: https://github.com/pampersrocker/buildbot-UnrealEngine
"""

VERSION="0.0.4"

setup(
    name="buildbot_UnrealEngine",
    version=VERSION,
    description="Easy configuration for the Unreal Automation Tool",
    long_description=long_description,
    author="Marvin Pohl",
    author_email="mp120@hdm-stuttgart.de",
    url="https://github.com/pampersrocker/buildbot-UnrealEngine",
    packages=["buildbot_UnrealEngine"],
    requires=["Buildbot (==0.9.1)"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points= {
      'buildbot.steps': [
        'BuildCookRun = buildbot_UnrealEngine.AutomationTool:BuildCookRun',
        'UEBuild = buildbot_UnrealEngine.BuildTool:Build'
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
