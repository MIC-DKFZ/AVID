# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools import Command as SetupCommand
import os
import ConfigParser

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()
    
setup(
    name='AVID',
    version='0.0.1',
    description='AVID project',
    long_description=readme,
    # if you want, put your own name here
    # (this would likely result in people sending you emails)
    author='SIDT@DKFZ',
    author_email='r.floca@dkfz.de',
    url='http://mitk.org',
    license=license,
    packages=find_packages(exclude=('tests', 'doc', 'tutorials', 'templates')),
    # the requirements to install this project.
    # Since this one is so simple this is empty.
    install_requires=[],
    # a more sophisticated project might have something like:
    #install_requires=['numpy>=1.11.0', 'scipy>=0.17', 'scikit-learn']

    # after running setup.py, you will be able to call samplepackage_exe
    # from the console as if it was a normal binary. It will call the function
    # main in bin/samplepackage_exe.py
    entry_points={
        'console_scripts': ['avidconfig=bin.avidconfig.__main__:main',
                            'avidpyoneer=bin.avidpyoneer.__main__:main'],
    },
)

