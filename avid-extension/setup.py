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
import configparser

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()
    
setup(
    name='AVID-extensions',
    version='0.0.1',
    description='AVID action extension project',
    long_description=readme,
    # if you want, put your own name here
    # (this would likely result in people sending you emails)
    author='SIDT@DKFZ',
    author_email='r.floca@dkfz.de',
    url='http://mitk.org',
    license=license,
    packages=find_packages(exclude=('tests', 'doc')),
    install_requires=['numpy>=1.11.0', 'scipy>=0.17', 'simpleitk'],
)

