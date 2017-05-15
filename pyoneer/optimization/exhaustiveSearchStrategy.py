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
from pyoneer.optimization.exhaustiveSearch import ExhaustiveSearchOptimizer
from pyoneer.optimization.strategy import OptimizationStrategy


class ExhaustiveSearchStrategy(OptimizationStrategy):
    ''' Predefined strategy that uses the exhaustive search optimization.
    This is more a demo strategy, because the optimization scheme is very inefficient.
    To use it you have to derive and implement defineSearchParameters. Additionally you have
    to decorate the parameter with 'frequency' to indicate the number of samples per parameters.
    '''

    def defineOptimizer(self):
        paramdesc = self.defineSearchParameters()

        names = list()
        minimas = list()
        maximas = list()
        freqs = list()

        for param in paramdesc:
            names.append(param)
            minimas.append(param_helper.getMinimum(paramdesc,param,True, scaleToOpt=True))
            maximas.append(param_helper.getMaximum(paramdesc,param,True, scaleToOpt=True))
            freqs.append(param_helper.getDecoration(paramdesc, param, 'frequency',True, scaleToOpt=True))

        return ExhaustiveSearchOptimizer(names, minimas, maximas,freqs)

    def defineName(self):
        return "ExhaustiveSearch"
