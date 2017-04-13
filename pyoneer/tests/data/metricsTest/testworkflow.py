# AVID - pyoneer
# AVID based tool for algorithmic evaluation and optimization
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

import sys
import os
import argparse

import avid.common.workflow as workflow

from avid.selectors import ActionTagSelector
from avid.actions.mapR import mapRBatchAction as mapR

if __name__ == "__main__":
    __this__ = sys.modules[__name__]

    parser = argparse.ArgumentParser()
    parser.add_argument('--modifier1', type=int)
    cliargs, unknown = parser.parse_known_args()

    actionProps = None

    if cliargs.modifier1 is not None:
        actionProps = {'modifier1': cliargs.modifier1}

    with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
      mapR(ActionTagSelector("Moving"), registrationSelector = ActionTagSelector("Registration"), templateSelector=ActionTagSelector("Target"), actionTag = "Result", additionalActionProps= actionProps).do()