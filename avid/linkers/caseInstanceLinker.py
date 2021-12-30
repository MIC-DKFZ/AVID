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

from avid.linkers import InnerLinkerBase
import avid.common.artefact.defaultProps as artefactProps

class CaseInstanceLinker(InnerLinkerBase):
    """
    Links data on the basis of the artefactProps.CASEINSTANCE entry.
    If strict linkage is false the linker will also accept instances where
    one of primary and secondary is none and the other has a defined value.
    """

    def __init__(self, useStrictLinkage=False, allowOnlyFullLinkage = True, performInternalLinkage=False):
        '''@param useStrictLinkage If true it will only link with the very same instance id.
           If false, it will treat None as wildcard that also matches.'''
        InnerLinkerBase.__init__(self, allowOnlyFullLinkage=allowOnlyFullLinkage,
                                 performInternalLinkage=performInternalLinkage)

        self._useStrictLinkage = useStrictLinkage

    def _findLinkedArtefactOptions(self, primaryArtefact, secondarySelection):
        linkValue = None

        if primaryArtefact is not None and artefactProps.CASEINSTANCE in primaryArtefact:
            linkValue = primaryArtefact[artefactProps.CASEINSTANCE]

        result = list()
        for secondArtefact in secondarySelection:
            if secondArtefact is not None and artefactProps.CASEINSTANCE in secondArtefact:
                itemValue = secondArtefact[artefactProps.CASEINSTANCE]
                if itemValue == linkValue \
                        or (not self._useStrictLinkage \
                            and (linkValue is None or itemValue is None)):
                    result.append(secondArtefact)
            else:
                if linkValue is None:
                    # key does not exist, but selection value is None, therefore it is a match
                    result.append(secondArtefact)

        return result
