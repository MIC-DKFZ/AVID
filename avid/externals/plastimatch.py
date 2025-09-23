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
import re

logger = logging.getLogger(__name__)

"""Formate type value. Indicating the artefact is stored as a MatchPoint simple point set file."""
FORMAT_VALUE_PLM_CXT = "Plastimatch_cxt"

COMPARE_KEYS = ["MIN", "AVE", "MAX", "MAE", "MSE", "DIF", "NUM", "RATIO"]


def parseCompareResult(outputStr):
    """Helper that parses the output of plastimatch compare into a dict.
    @param outputStr: String that contains the output of plastimatch compare
    @result Dictionary that containes the result values of the plastimatch call.
    Keys are (From the plastimatch documentation):
    MIN      Minimum value of difference image
    AVE      Average value of difference image
    MAX      Maximum value of difference image
    MAE      Mean average value of difference image
    MSE      Mean squared difference between images
    DIF      Number of pixels with different intensities
    NUM      Total number of voxels in the difference image
    And additionally:
    RATIO    ratio between DIF and NUM
    """
    result = dict()

    lines = outputStr.splitlines()

    for line in lines:
        items = [_f for _f in line.split() if _f]
        key = None
        for item in items:
            candidate = item.strip(" \t\n\r")
            if candidate in COMPARE_KEYS:
                key = candidate
            elif not key is None:
                result[key] = float(candidate)

    result["RATIO"] = result["DIF"] / result["NUM"]

    return result


DICE_KEYS = [
    "TP",
    "TN",
    "FN",
    "FP",
    "DICE",
    "SE",
    "SP",
    "Hausdorff distance",
    "Avg average Hausdorff distance",
    "Max average Hausdorff distance",
    "Percent (0.95) Hausdorff distance",
    "Hausdorff distance (boundary)",
    "Avg average Hausdorff distance (boundary)",
    "Max average Hausdorff distance (boundary)",
    "Percent (0.95) Hausdorff distance (boundary)",
]


def parseDiceResult(outputStr):
    """Helper that parses the output of plastimatch dice into a dict.
    @param outputStr: String that contains the output of plastimatch compare
    @result Dictionary that containes the result values of the plastimatch call.
    Keys are:
    'TP','TN','FN','FP','DICE','SE','SP',
    'Hausdorff distance','Avg average Hausdorff distance',
    'Max average Hausdorff distance','Percent (0.95) Hausdorff distance',
    'Hausdorff distance (boundary)','Avg average Hausdorff distance (boundary)',
    'Max average Hausdorff distance (boundary)','Percent (0.95) Hausdorff distance (boundary)'
    """
    result = dict()

    lines = outputStr.splitlines()
    for line in lines:
        try:
            items = [_f for _f in re.split(r"\s*[:\=]\s*", line) if _f]
            if items[0] in DICE_KEYS:
                result[items[0]] = float(items[1])
        except:
            pass

    return result
