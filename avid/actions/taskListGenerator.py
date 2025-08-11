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

import logging
import os
import json

from avid.common.artefact import defaultProps as artefactProps

from .pythonAction import PythonUnaryStackBatchAction
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class TaskListGeneratorAction(PythonUnaryStackBatchAction):
    """ Class that takes a list of artefacts and generates a MITK tasklist based on them """
    @staticmethod
    def _indicate_outputs(actionInstance, **args):
        rootPath = actionInstance._session.contentPath
        result = actionInstance.generateArtefact()
        result[artefactProps.URL] = os.path.join(rootPath, actionInstance.actionTag + '.json')
        return [result]

    @staticmethod
    def _generate_tasks(inputs, outputs, **args):
        output_file = outputs[0][artefactProps.URL]
        inspected_dir = os.path.dirname(output_file)
        tasks = []
        for artefact in inputs:
            url = artefact[artefactProps.URL]
            os.path.dirname(url)
            tasks.append({
                "Name": artefact['name'],
                "Image": url,
                "Result": os.path.join(inspected_dir, 'inspected', os.path.basename(url))
            })

        return tasks

    def _generate_default_tasklist(self, inputs, outputs, **args):
        output_file = outputs[0][artefactProps.URL]
        logger.info(f"Writing tasklist to {output_file}")

        tasks = self.generate_tasks_callable(inputs, outputs, **args)

        data = {
            "FileFormat": "MITK Segmentation Task List",
            "Version": 3,
            "Name": outputs[0][artefactProps.ACTIONTAG],
            "Tasks": tasks
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

    def __init__(self, inputSelector, actionTag='TaskListGenerator', generateCallable=None, indicateCallable=None,
                 generate_tasks_callable=None, passOnlyURLs=False, **kwargs):
        """
        :param inputSelector: Specified artefacts will all be included in the resulting tasklist
        :param generateCallable: Custom callable that defines how the resulting tasklist should be built. By default,
        each tasklist entry contains the artefact name and url. The signature of generateCallable is:
        generateCallable(inputs ( = Input artefacts), outputs (=the output that should be produced), **allArgs
        (= all other arguments passed to the action)
        :param indicateCallable: Custom callable that defines which outputs should be produced (see generateCallable).
        By default, a single json file in the top directory of the current session content will be created.
        :param generate_tasks_callable: Custom callable that creates a list of tasks to write into a tasklist. If a
        custom generateCallable is defined, this method may not be used.
        By default, each input artefact gets a task with it as Image. generate_tasks_callable() receives the same inputs
        as generateCallable, but returns a list of dictionaries that define tasklist tasks.
        """
        if indicateCallable is None:
            indicateCallable = TaskListGeneratorAction._indicate_outputs

        if generateCallable is None:
            generateCallable = self._generate_default_tasklist

        if generate_tasks_callable is None:
            generate_tasks_callable = TaskListGeneratorAction._generate_tasks
        self.generate_tasks_callable = generate_tasks_callable

        PythonUnaryStackBatchAction.__init__(self,
                                             inputSelector=inputSelector,
                                             actionTag=actionTag,
                                             generateCallable=generateCallable,
                                             indicateCallable=indicateCallable,
                                             passOnlyURLs=passOnlyURLs,
                                             **kwargs)
