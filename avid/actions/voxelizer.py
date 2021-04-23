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

import logging
import re

import avid.common.artefact.defaultProps as artefactProps
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class VoxelizerAction(GenericCLIAction):
    """Class that wraps the single action for the tool rttb VoxelizerTool."""

    def __init__(self, structSet, referenceImage, structName,
                 actionTag='Voxelizer', allowIntersections=True,
                 booleanMask=False, outputExt='nrrd', alwaysDo=False, session=None,
                 additionalActionProps=None, actionConfig=None, propInheritanceDict=None):

        structSet = self._ensureSingleArtefact(structSet, "structSet")
        referenceImage = self._ensureSingleArtefact(referenceImage, "referenceImage")
        self._structName = structName
        self._init_session(session)

        additionalArgs = {'y': 'itk', 'a': None, 'e': self._getStructPattern()}
        if allowIntersections:
            additionalArgs['i'] = None
        if booleanMask:
            additionalArgs['z'] = None

        internalActionProps = {artefactProps.OBJECTIVE: self._structName,
                               artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK}

        if additionalActionProps is not None:
            internalActionProps.update(additionalActionProps)

        GenericCLIAction.__init__(self, s=[structSet], r=[referenceImage], actionID="VoxelizerTool",
                                  outputFlags=['o'],
                                  outputReferenceArtefactName='s',
                                  additionalArgs=additionalArgs,
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=internalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict,
                                  defaultoutputextension=outputExt)

    def _getStructPattern(self):
        pattern = self._structName
        if self._session.hasStructurePattern(self._structName):
            pattern = self._session.structureDefinitions[self._structName]
        else:
            # we stay with the name, but be sure that it is a valid regex. because it
            # is expected by the doseTool
            pattern = re.escape(pattern)

        return pattern


def _voxelizer_creation_delegate(structNames, **kwargs):
    actions = list()
    actionArgs = kwargs.copy()
    for name in structNames:
        actionArgs['structName'] = name
        actions.append(VoxelizerAction(**actionArgs))
    return actions


class VoxelizerBatchAction(BatchActionBase):
    """Batch action for the voxelizer tool.."""

    def __init__(self, structSetSelector, referenceSelector, structNames=None,
                 referenceLinker=None,
                 actionTag="doseStat",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        """ Batch action for the voxelizer tool.
    @param structNames: List of the structures names that should be voxelized.
     If none is passed all structures defined in current session's structure
     definitions.
    """
        if referenceLinker is None:
            referenceLinker = CaseLinker()

        additionalInputSelectors = {"referenceImage": referenceSelector}
        linker = {"referenceImage": referenceLinker}

        self._init_session(session)
        if structNames is None:
            structNames = list(self._session.structureDefinitions.keys())

        BatchActionBase.__init__(self, actionTag=actionTag, actionCreationDelegate=_voxelizer_creation_delegate,
                                 primaryInputSelector=structSetSelector, primaryAlias="structSet",
                                 additionalInputSelectors=additionalInputSelectors, linker=linker,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 structNames=structNames, **singleActionParameters)
