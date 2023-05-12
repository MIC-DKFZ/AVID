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
import math
import os
import time
import xml.etree.ElementTree as ElementTree
from builtins import str

from avid.common.artefact import generateArtefactEntry, update_artefacts
from . import defaultProps

logger = logging.getLogger(__name__)

def indent(elem, level=0):
    """ copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


XML_ARTEFACTS = "avid:artefacts"
XML_ARTEFACT = "avid:artefact"
XML_PROPERTY = "avid:property"
XML_INPUT_ID = "avid:input_id"
XML_ATTR_VERSION = "version"
XML_ATTR_KEY = "key"
XML_NAMESPACE = "http://www.dkfz.de/en/sidt/avid"
XML_NAMESPACE_DICT = {"avid": XML_NAMESPACE}
CURRENT_XML_VERSION = "1.0"


def loadArtefactList_xml(filePath, expandPaths=False, rootPath=None):
    """Loads a artefact list from a XML file.
    @param filePath Path where the artefact list is located or file like object that grants access to the list.
    @param expandPaths If true all relative url will be expanded by the rootPath
    If rootPath is not set, it will be the directory of filePath
    @param rootPath If defined any relative url in the list will expanded by the
    root path. If rootPath is set, expandPaths is implicitly true.
    """
    artefacts = list()

    if rootPath is None and expandPaths is True:
        rootPath = os.path.split(filePath)[0]
    if not os.path.isfile(filePath):
        raise ValueError("Cannot load artefact list from file. File does not exist. File path: " + str(filePath))

    tree = ElementTree.parse(filePath)
    root = tree.getroot()

    if root.tag != "{" + XML_NAMESPACE + "}artefacts":
        raise ValueError("XML has not the correct root element. Must be 'artefacts', but is: " + root.tag)

    for aElement in root.findall(XML_ARTEFACT, XML_NAMESPACE_DICT):
        artefact = generateArtefactEntry(None, None, 0, "UnknownAction", None, None)

        for aProp in aElement.findall(XML_PROPERTY, XML_NAMESPACE_DICT):
            if XML_ATTR_KEY in aProp.attrib:
                if aProp.attrib[XML_ATTR_KEY] == defaultProps.INPUT_IDS:
                    value = dict()
                    for aSource in aProp.findall(XML_INPUT_ID, XML_NAMESPACE_DICT):
                        if XML_ATTR_KEY in aSource.attrib:
                            if aSource.attrib[XML_ATTR_KEY] in value:
                                if aSource.text is None or len(aSource.text)==0:
                                    value[aSource.attrib[XML_ATTR_KEY]].append(None)
                                else:
                                   value[aSource.attrib[XML_ATTR_KEY]].append(aSource.text)
                            else:
                                if aSource.text is None or len(aSource.text)==0:
                                    value[aSource.attrib[XML_ATTR_KEY]] = [None]
                                else:
                                    value[aSource.attrib[XML_ATTR_KEY]] = [aSource.text]
                        else:
                            raise ValueError("XML seems not to be valid. SourceID element has no key attribute")
                    artefact[aProp.attrib[XML_ATTR_KEY]] = value
                else:
                    artefact[aProp.attrib[XML_ATTR_KEY]] = aProp.text
            else:
                raise ValueError("XML seems not to be valid. Property element has no key attribute")

        if rootPath is not None and not os.path.isabs(artefact[defaultProps.URL]):
            artefact[defaultProps.URL] = os.path.join(rootPath, artefact[defaultProps.URL])
        artefact[defaultProps.URL] = os.path.normpath(artefact[defaultProps.URL])

        if artefact[defaultProps.URL] is None or not os.path.isfile(artefact[defaultProps.URL]):
            artefact[defaultProps.INVALID] = True
            logger.info("Artefact had no valid URL. Set invalid property to true. Artefact: %s", artefact)

        artefacts.append(artefact)

    return artefacts


def saveArtefactList_xml(filePath, artefacts, rootPath=None, savePathsRelative=True):
    if rootPath is None:
        rootPath = os.path.split(filePath)[0]

    root = ElementTree.Element(XML_ARTEFACTS, {XML_ATTR_VERSION: "1.0", "xmlns:avid": XML_NAMESPACE})

    for artefact in artefacts:
        xmlArtefact = ElementTree.SubElement(root, XML_ARTEFACT)
        for key in artefact._defaultProps:
            if artefact[key] is not None:
                xmlProp = ElementTree.SubElement(xmlArtefact, XML_PROPERTY, {XML_ATTR_KEY: key})
                value = artefact[key]
                if key is defaultProps.INPUT_IDS:
                    for sourceName in value:
                        if value[sourceName] is not None:
                            for id in value[sourceName]:
                                xmlInput = ElementTree.SubElement(xmlProp, XML_INPUT_ID, {XML_ATTR_KEY: sourceName})
                                if id is not None:
                                    xmlInput.text = id
                else:
                    if key is defaultProps.URL:
                        if savePathsRelative:
                            try:
                                value = os.path.relpath(artefact[key], rootPath)
                            except:
                                logger.warning(
                                    "Artefact URL cannot be converted to be relative. Path is kept absolute. Artefact URL: %s",
                                    value)
                        value = value.replace("\\", "/")
                    xmlProp.text = str(value)
        for key in artefact._additionalProps:
            if artefact[key] is not None:
                xmlProp = ElementTree.SubElement(xmlArtefact, XML_PROPERTY, {XML_ATTR_KEY: key})
                xmlProp.text = str(artefact[key])

    tree = ElementTree.ElementTree(root)
    indent(root)

    try:
        os.makedirs(os.path.split(filePath)[0])
    except:
        pass

    if os.path.isfile(filePath):
        os.remove(filePath)

    tree.write(filePath, xml_declaration=True)


def update_artefactlist(destination_file, source_artefacts, update_existing=False,
                        rootPath=None, savePathsRelative=True, wait_time=10):
    """
    Helper function that updates the content of an artefact file with a passed artefact list.
    :param destination_file: File which content should be updated
    :param source_artefacts: List of artefacts the destination_file should be updated with
    :param update_existing: Indicates of existing/simelar artefacts in the file should also be updated or ignored.
    :param rootPath: root path that should be used for relative path operations
    :param savePathsRelative: indicates if paths should be stored as relative paths
    :param wait_time: if the destination file is locked, the update function will wait and retry. This is the time in
     seconds the function should wait and try to update until it returns with an error, if not successful.
    """

    # Simple strategy to ensure an OS independent lock while updating the file.
    # This function will only update if no lock file exists.
    # In other cases it waits and retries until it is timed out.
    pause_duration = 0.5
    max_pause_count = math.ceil(wait_time / pause_duration)
    pause_count = 0
    lf_path = destination_file+ os.extsep + 'update_lock'
    lf = None
    while True:
        try:
            lf = open(lf_path, 'x')
            break
        except OSError:
            if pause_count < max_pause_count:
                time.sleep(pause_duration)
                pause_count = pause_count + 1
                logger.debug('"%s" is not accessible. Wait and try again.', destination_file)
            else:
                raise PermissionError('Cannot update artefact list file. File is blocked by another update operation.'
                                   ' File: {}'.format(destination_file))

    try:
        destination_artefacts = loadArtefactList_xml(destination_file,rootPath=rootPath)
        update_artefacts(destination_list=destination_artefacts, source_list=source_artefacts,
                         update_existing=update_existing)
        saveArtefactList_xml(filePath=destination_file,artefacts=destination_artefacts, rootPath=rootPath,
                             savePathsRelative=savePathsRelative )
    finally:
        if lf is not None:
            lf.close()
            os.remove(lf_path)
