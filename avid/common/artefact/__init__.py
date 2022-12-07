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

'''
  This module offers methods for correct generation ore adding of artefact entries
  tis responsible to add new dict entries in the flat file data container 
'''

from collections.abc import Mapping
import logging
import os
import platform
import threading
import time
import uuid
from builtins import object
from builtins import str
from copy import deepcopy

from . import defaultProps

logger = logging.getLogger(__name__)

'''List of properties that should be checked to determine the similarity of two artifacts.'''
similarityRelevantProperties = [defaultProps.CASE, defaultProps.CASEINSTANCE, defaultProps.TIMEPOINT,
                                defaultProps.ACTIONTAG, defaultProps.ACTION_CLASS, defaultProps.INPUT_IDS,
                                defaultProps.TYPE, defaultProps.FORMAT, defaultProps.OBJECTIVE,
                                defaultProps.RESULT_SUB_TAG, defaultProps.DOSE_STAT, defaultProps.DIAGRAM_TYPE,
                                defaultProps.ONLY_ESTIMATOR, defaultProps.N_FRACTIONS_FOR_ESTIMATION, defaultProps.ACC_ELEMENT]


def ensureSimilarityRelevantProperty(propertyName):
    '''Helper that ensures that the passed propertyName is contained in similarityRelevantProperties and therefore will
     be used to discriminate artifacts.'''
    global similarityRelevantProperties
    if propertyName not in similarityRelevantProperties:
        similarityRelevantProperties.append(propertyName)


class Artefact(object):
    def __init__(self, defaultP=None, additionalP=None):

        self.lock = threading.RLock()

        self._defaultProps = dict()
        if defaultP is None:
            self._defaultProps[defaultProps.CASE] = None
            self._defaultProps[defaultProps.CASEINSTANCE] = None
            self._defaultProps[defaultProps.TIMEPOINT] = 0
            self._defaultProps[defaultProps.ACTIONTAG] = "unkown_tag"
            self._defaultProps[defaultProps.TYPE] = None
            self._defaultProps[defaultProps.FORMAT] = None
            self._defaultProps[defaultProps.URL] = None
            self._defaultProps[defaultProps.OBJECTIVE] = None
            self._defaultProps[defaultProps.RESULT_SUB_TAG] = None
            self._defaultProps[defaultProps.INVALID] = None
            self._defaultProps[defaultProps.INPUT_IDS] = None
            self._defaultProps[defaultProps.ACTION_CLASS] = None
            self._defaultProps[defaultProps.ACTION_INSTANCE_UID] = None
        else:
            for key in defaultP:
                self._defaultProps[key] = defaultP[key]

        if not defaultProps.ID in self._defaultProps:
            self._defaultProps[defaultProps.ID] = str(uuid.uuid1())
        if not defaultProps.TIMESTAMP in self._defaultProps:
            self._defaultProps[defaultProps.TIMESTAMP] = str(time.time())
        if not defaultProps.EXECUTION_DURATION in self._defaultProps:
            self._defaultProps[defaultProps.EXECUTION_DURATION] = None

        self._additionalProps = dict()
        if not additionalP is None:
            for key in additionalP:
                self._additionalProps[key] = additionalP[key]

    def is_similar(self, other):

        mykeys = list(self.keys())
        okeys = list(other.keys())

        for key in similarityRelevantProperties:
            if key in mykeys and key in okeys:
                if not (self[key] == other[key]):
                    # Both have defined the property but values differ -> false
                    return False
            elif key in mykeys or key in okeys:
                # Only one has defined the property -> false
                return False

        return True

    def keys(self):
        return list(self._defaultProps.keys()) + list(self._additionalProps.keys())

    def is_invalid(self):
        return self._defaultProps[defaultProps.INVALID]

    def __getitem__(self, key):

        if key in self._defaultProps:
            return self._defaultProps[key]
        elif key in self._additionalProps:
            return self._additionalProps[key]

        raise KeyError('Unkown artefact key was requested. Key: {}; Artefact: {}'.format(key, self))

    def __setitem__(self, key, value):
        with self.lock:
            if value is not None and not key == defaultProps.INPUT_IDS:
                value = str(value)

            if key == defaultProps.TIMEPOINT:
                try:
                    # If timepoint can be converted into a number, do so
                    value = int(value)
                except:
                    pass
            elif key == defaultProps.EXECUTION_DURATION:
                try:
                    value = float(value)
                except:
                    pass
            elif key == defaultProps.INVALID:
                if value in ["True", "true", "TRUE"]:
                    value = True
                else:
                    value = False
            elif key == defaultProps.INPUT_IDS:
                if isinstance(value, Mapping):
                    value = dict(value)
                elif value is not None:
                    raise ValueError(
                        'Cannot set INPUT_IDS property of artefact. Value is no dict. Value: {}'.format(value))

            if key in self._defaultProps:
                self._defaultProps[key] = value
            else:
                self._additionalProps[key] = value

    def __missing__(self, key):
        logger.warning("Unkown artefact property was requested. Unknown key: %s", str(key))
        return None

    def __len__(self):
        return len(self._defaultProps) + len(self._additionalProps)

    def __contains__(self, key):
        if key in self._defaultProps or key in self._additionalProps:
            return True

        return False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._defaultProps == other._defaultProps and self._additionalProps == other._additionalProps
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Artefact(%s, %s)' % (self._defaultProps, self._additionalProps)

    def __copy__(self):
        newArtefact = Artefact(defaultP=deepcopy(self._defaultProps), additionalP=deepcopy(self._additionalProps))
        return newArtefact


def getArtefactProperty(artefact, key):
    '''Helper function that returns the value of an artefact property indicated by
    key. If the artefact is None or the key does not exist it returns None.
    @param artefact Reference to the artefact entity that contains the wanted property value
    @param key Key of the value that is wanted.'''
    result = None
    if artefact is not None and key in artefact:
        result = artefact[key]

    return result


def ensureCaseInstanceValidity(checkedArtefact, *otherArtefacts):
    '''Checks if the checkedArtefact has a valid case instance compared to all
       other artefacts. The case instance is valid if checkedArtefact has the value
       None or the same value then all other artefacts. If the other artifacts
       have a value, checkedArtefact gets the same value.
       @pre otherArtefacts must have amongst other the same instance value or none
       @pre checkedArtefact must have the same instance value or none
       @return Returns false if there was a conflict (failed precondition) while
       ensuring the validity.'''
    result = True
    masterInstance = None
    for oa in otherArtefacts:
        oInstance = getArtefactProperty(oa, defaultProps.CASEINSTANCE)
        if oInstance is not None:
            if masterInstance is None:
                masterInstance = oInstance
            elif not masterInstance == oInstance:
                result = False

    if masterInstance is not None:
        checkedInstance = getArtefactProperty(checkedArtefact, defaultProps.CASEINSTANCE)
        if checkedInstance is None:
            checkedArtefact[defaultProps.CASEINSTANCE] = masterInstance
        elif not masterInstance == checkedInstance:
            result = False

    return result


def addArtefactToWorkflowData(workflowData, artefactEntry, removeSimelar=False):
    '''
        This method adds an arbitrary artefact entry to the workflowData list.
        @param removeSimelar If True the method checks if the session data contains
        a simelar entry. If yes the simelar entry will be removed.
    '''
    if removeSimelar:
        simelar = findSimilarArtefact(workflowData, artefactEntry)
        if simelar is not None:
            workflowData.remove(simelar)

    workflowData.append(artefactEntry)
    return workflowData


def findSimilarArtefact(workflowData, artefactEntry):
    '''
        Checks if a passed artefact has already an entry in the workflow data and
        returns this entry. Returns None if no entry was found. Remark: URL is
        not check because it is not relevant for an artefact to be simelar.
    '''
    for entry in (workflowData):
        if artefactEntry.is_similar(entry):
            return entry

    return None


def artefactExists(workflowData, artefactEntry):
    '''
        Checks if a passed artefact has already an entry in the workflow data.
        Remark: It only ensures that the standard key (CASE, CASEINSTANCE,
        TIMEPOINT, ACTIONTAG, TYPE and FORMAT) are equal. Differences in URL are
        ignored. As well as custom properties of the artefact.
    '''
    return findSimilarArtefact(workflowData, artefactEntry) is not None


def update_artefacts(destination_list, source_list, update_existing=False):
    """Helper function that updates the content of the destination list with the content of the source list."""
    for artefact in source_list:
        if findSimilarArtefact(destination_list,artefact) is None or update_existing:
            addArtefactToWorkflowData(destination_list,artefact, removeSimelar=True)


def get_all_values_of_a_property(workflow_data, property_key):
    """Helper function that returns a list of all values found for a certain property in the passed collection
    of artefact.
    :param workflow_data: list of artefacts that should be evaluated.
    :param property_key: the key of the property that should be evaluated.
    :return Returns the list of values. Each value is only present once in the list, even if multiple artefacts
    have this value."""
    values = [a[property_key] for a in workflow_data if property_key in a]
    return list(set(values))

def generateVerboseArtefactPath(workflow, workflowArtefact):
    """ Generates the path derived from the workflow informations and the
        properties of the artefact. This default style will generate the following
        path:
        [workflow.outputpath]+[workflow.name]+[artefact.actiontag]+[artefact.type]
        +[artefact.case]+[artefact.caseinstance]+[artefact.timepoint]
        The case, caseinstance and timepoint parts are skipped if the respective
        value is NONE. """
    artefactPath = os.path.join(workflow.contentPath, workflowArtefact[defaultProps.ACTIONTAG],
                                workflowArtefact[defaultProps.TYPE])
    if workflowArtefact[defaultProps.CASE] is not None:
        artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.CASE]))
    if workflowArtefact[defaultProps.CASEINSTANCE] is not None:
        artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.CASEINSTANCE]))
    if workflowArtefact[defaultProps.TIMEPOINT] is not None:
        artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.TIMEPOINT]))

    return artefactPath


def generateDefaultArtefactPath(workflow, workflowArtefact):
    """ Generates the path derived from the workflow informations and the
        properties of the artefact. This default style will generate the following
        path:
        [workflow.outputpath]+[workflow.name]+[artefact.actiontag]+[artefact.type]
        +[artefact.case]+[artefact.caseinstance]
        The case and caseinstance parts are skipped if the respective
        value is NONE. """
    artefactPath = os.path.join(workflow.contentPath, workflowArtefact[defaultProps.ACTIONTAG],
                                workflowArtefact[defaultProps.TYPE])
    if workflowArtefact[defaultProps.CASE] is not None:
        artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.CASE]))
    if workflowArtefact[defaultProps.CASEINSTANCE] is not None:
        artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.CASEINSTANCE]))

    return artefactPath

def generateFlatArtefactPath(workflow, workflowArtefact):
    """ Using this function will write all artefacts directly into the content directory of the workflow."""
    return workflow.contentPath

pathGenerationDelegate = generateDefaultArtefactPath


def ensureValidPath(unsafePath):
    """
    Normalizes string, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import string
    validPathChars = ":-_.() #%s%s" % (string.ascii_letters, string.digits)
    validPathChars += os.sep
    if platform.system() == 'Windows':
        # also add unix version because windows can handle it to.
        validPathChars += '/'
    cleanedFilename = unicodedata.normalize('NFKD', unsafePath).encode('ascii', 'ignore').decode('ascii')
    result = ''.join(c for c in cleanedFilename if c in validPathChars)
    result = result.strip().replace(' ','_')
    return result


def generateArtefactPath(workflow, workflowArtefact):
    """ Public method that should be used to get an artefact path.
       Uses the path generation delegate to generate an artefact path.
       Ensures that the path is valid."""
    artefactPath = pathGenerationDelegate(workflow, workflowArtefact)
    return ensureValidPath(artefactPath)


def _defaultGetArtefactShortName(workflowArtefact):
    '''Default strategy for the short name. If no objective is defined '''
    from . import defaultProps as artefactProps
    tag = getArtefactProperty(workflowArtefact, artefactProps.ACTIONTAG)
    timePoint = getArtefactProperty(workflowArtefact, artefactProps.TIMEPOINT)
    name = '{}#{}'.format(tag, timePoint)

    objective = getArtefactProperty(workflowArtefact, artefactProps.OBJECTIVE)
    if not objective is None:
        name = '{}-{}#{}'.format(tag, objective, timePoint)

    return name

shortNameGenerationDelegate = _defaultGetArtefactShortName

def getArtefactShortName(workflowArtefact):
    '''Public method that should be used to get a "nick name" for the passed artefact. This is e.g. used by action
     if the determin the name of an action instance based on the gifen artefacts. One may alter the short name strategy
     by overwritting the shortNameGenerationDelegate.'''
    name = shortNameGenerationDelegate(workflowArtefact)
    return ensureValidPath(name)


from .generator import generateArtefactEntry
