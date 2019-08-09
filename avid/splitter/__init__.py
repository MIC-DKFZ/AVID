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

from builtins import object


class BaseSplitter(object):
    '''base clase for functors used to split a artefact list by certain criterias
    and pass back a list of splitted artefact lists.
    The default implementation does not touch the selection at all and just passes back a copy of the passed selection
    as first (and only) split list element.'''

    def __init__(self):
        pass

    def splitSelection(self, selection):
        '''
        does nothing
        '''
        return [selection.copy()]


from .keyValueSplitter import KeyValueSplitter
from .singleSplitter import SingleSplitter