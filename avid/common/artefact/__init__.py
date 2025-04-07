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
            self._defaultProps[defaultProps.ACTIONTAG] = "unknown_tag"
            self._defaultProps[defaultProps.TYPE] = None
            self._defaultProps[defaultProps.FORMAT] = None
            self._defaultProps[defaultProps.URL] = None
            self._defaultProps[defaultProps.OBJECTIVE] = None
            self._defaultProps[defaultProps.RESULT_SUB_TAG] = None
            self._defaultProps[defaultProps.RESULT_SUB_COUNT] = None
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
        """ Function that indicates if one artefact can be assumed as equal/similar to self as they share the
            same similarity relevant properties. It is also used for __eq__()."""
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

    def is_identical(self, other):
        """ Function that indicates if one artefact can be assumed as truly identical to self as they
            have the same properties."""
        if isinstance(other, self.__class__):
            return self._defaultProps == other._defaultProps and self._additionalProps == other._additionalProps
        else:
            return False
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
            #raise RuntimeError
            return self.is_similar(other)
        else:
            return False

    def __hash__(self):
        """Define hash based on similarity-relevant properties."""

        def __make_hashable(value):
            # If the value is a dictionary, convert it to a sorted tuple of key-value pairs
            if isinstance(value, dict):
                return tuple(sorted((k, __make_hashable(v)) for k, v in value.items()))
            # If the value is a list or other iterable, convert to tuple recursively
            elif isinstance(value, (list, set, tuple)):
                return tuple(__make_hashable(item) for item in value)
            # Otherwise, return the value as-is (should be hashable)
            return value

        # Generate a hashable representation of the similarity-relevant properties
        hashable_properties = tuple(
            __make_hashable(self[key]) for key in similarityRelevantProperties if key in self.keys())
        return hash(hashable_properties)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Artefact(%s, %s)' % (self._defaultProps, self._additionalProps)

    def __copy__(self):
        new_artefact = Artefact(defaultP=deepcopy(self._defaultProps), additionalP=deepcopy(self._additionalProps))
        return new_artefact

    def clone(self):
        """ Create a copy of the artefact with its own uid """
        new_artefact = Artefact(defaultP=deepcopy(self._defaultProps), additionalP=deepcopy(self._additionalProps))
        new_artefact[defaultProps.ID] = str(uuid.uuid1())
        return new_artefact


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

def update_artefacts(destination_collection, source_collection, update_existing=False):
    """Helper function that updates the content of the destination list with the content of the source list."""
    for artefact in source_collection:
        if not artefact in destination_collection or update_existing:
            destination_collection.add_artefact(artefact, replace_if_exists=True)


def get_all_values_of_a_property(workflow_data, property_key):
    """Helper function that returns a list of all values found for a certain property in the passed collection
    of artefact.
    :param workflow_data: list of artefacts that should be evaluated.
    :param property_key: the key of the property that should be evaluated.
    :return Returns the list of values. Each value is only present once in the list, even if multiple artefacts
    have this value."""
    values = [a[property_key] for a in workflow_data if property_key in a]
    return sorted(list(set(values)))

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


class ArtefactCollection:
    def __init__(self, initial_artefacts=None):
        # Dictionary for storing artefacts with a hash-based key for efficient lookup
        self.artefact_dict = {}
        if not initial_artefacts is None:
            self.extend(initial_artefacts, replace_if_exists=True)

    def extend(self, artefacts, replace_if_exists=True):
        for artefact in artefacts:
            self.add_artefact(artefact=artefact)

    def add_artefact(self, artefact, replace_if_exists=True):
        """
        Adds an artefact to the collection. If an artefact with the same hash exists:
        - Replaces it if replace_if_exists is True.
        - Raises a ValueError otherwise.
        Returns the replaced artefact. If no artefact was replaced it returns None.
        """
        artefact_hash = hash(artefact)

        already_existing = artefact_hash in self.artefact_dict
        replace_artefact = None
        if already_existing:
            if not replace_if_exists:
                raise ValueError(f'An identical artefact already exists in the collection. Existing artefact: "'
                             f'{self.artefact_dict[artefact_hash]}". New artefact: "{artefact}"')
            replace_artefact = self.artefact_dict[artefact_hash]

        self.artefact_dict[artefact_hash] = artefact
        return replace_artefact

    def remove_artefact(self, artefact):
        """Removes the artefact from the collection if it exists."""
        artefact_hash = hash(artefact)
        if artefact_hash in self.artefact_dict:
            del self.artefact_dict[artefact_hash]
            return True
        return False

    def find_similar(self, artefact):
        """
        Finds an artefact in the collection that is similar to the given artefact.
        Returns the artefact if found, or None if no match exists.
        """
        artefact_hash = hash(artefact)
        return self.artefact_dict.get(artefact_hash, None)

    def similar_artefact_exists(self, artefact):
        """Checks if an artefact similar to the given artefact exists in the collection."""
        return self.find_similar(artefact=artefact) is not None

    def identical_artefact_exists(self, artefact):
        """Checks if the identical (so all, not only the identity relevant properties, are the same) artefact to the
         given artefact exists in the collection."""
        artefact_in_dict = self.find_similar(artefact)
        if artefact_in_dict is None:
            return False
        return artefact_in_dict.is_identical(artefact)

    def __iter__(self):
        """Allows iteration over artefacts in the collection."""
        return iter(self.artefact_dict.values())

    def __len__(self):
        """Returns the number of artefacts in the collection."""
        return len(self.artefact_dict)

    def __contains__(self, artefact):
        """Check if an identical artefact exists in the collection."""
        return self.identical_artefact_exists(artefact=artefact)

    def __repr__(self):
        return f"ArtefactCollection({len(self.artefact_dict)} artefacts)"

    def __eq__(self, other):
        """Checks if the passed container containes the identical artefacts then self.
        Order of artefects is not relevant for equality."""
        other_collection = ArtefactCollection()

        try:
            other_collection.extend(other, replace_if_exists=False)
        except ValueError:
            return False

        if len(self) != len(other_collection):
            return False

        for artefact in self:
            if not other_collection.identical_artefact_exists(artefact=artefact):
                return False
        return True

    def collection_is_similar(self, other):
        """Checks if the passed container containes simelar artefacts then self.
        Order of artefects is not relevant for equality."""
        other_collection = ArtefactCollection()

        try:
            other_collection.extend(other, replace_if_exists=False)
        except ValueError:
            return False

        if len(self) != len(other_collection):
            return False

        for artefact in self:
            if not other_collection.similar_artefact_exists(artefact=artefact):
                return False
        return True