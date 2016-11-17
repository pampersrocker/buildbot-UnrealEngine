#!/usr/bin/env python

from setuptools import setup

setup(
    name="UE4-Buildbot",
    version="0.0.1",
    description="Easy configuration for the Unreal Automation Tool",
    author="Marvin Pohl",
    author_email="mp120@hdm-stuttgart.de",
    url="https://github.com/pampersrocker/ue4-buildbot",
    packages=["UE4BuildBot"],
    requires=["Buildbot (==0.9.1)"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
