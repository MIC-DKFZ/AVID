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

import pyoneer.optimization.parameters as param_helper
from pyoneer.optimization.dlibWrapper import FindMinGlobalOptimizer
from pyoneer.optimization.strategy import OptimizationStrategy


class DefaultDlibFindMinGlobalStrategy(OptimizationStrategy):
    ''' Predefined strategy that uses the dlib find_min_global optimizer in default settings.
    To use it you have to derive and implement defineSearchParameters.
    '''

    def defineOptimizer(self):
        paramdesc = self.defineSearchParameters()

        names = list()
        minimas = list()
        maximas = list()

        for param in paramdesc:
            names.append(param)
            minimas.append(param_helper.getMinimum(paramdesc,param, True, scaleToOpt=True))
            maximas.append(param_helper.getMaximum(paramdesc,param, True, scaleToOpt=True))

        return FindMinGlobalOptimizer(names, minimas, maximas)

    def defineName(self):
        return "DefaultDlibFindMinGlobal"
