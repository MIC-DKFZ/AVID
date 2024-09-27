# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools import Command as SetupCommand
import os

with open('README.md') as f:
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
    # a more sophisticated project might have something like:
    #install_requires=['numpy>=1.11.0', 'scipy>=0.17', 'scikit-learn']
    install_requires=[],
    # the requirements are only need for special configurations.
	extras_require = {
        'rich': ["rich==13.7.1"],
    },
    # after running setup.py, you will be able to call samplepackage_exe
    # from the console as if it was a normal binary. It will call the function
    # main in bin/samplepackage_exe.py
    entry_points={
        'console_scripts': ['avidconfig=bin.avidconfig.__main__:main',
                            'aviddiag=bin.aviddiag.__main__:main',
							'avidsplit=bin.avidsplit.__main__:main'],
    },
)

