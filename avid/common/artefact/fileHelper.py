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

from builtins import str
import csv
import logging
import os
import uuid
import xml.etree.ElementTree as ElementTree

from . import defaultProps
from avid.common.artefact import generateArtefactEntry


def indent(elem, level=0):
    ''' copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way '''
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
    '''Loads a artefact list from a XML file.
    @param filePath Path where the artefact list is located.
    @param expandPaths If true all relative url will be expanded by the rootPath
    If rootPath is not set, it will be the directory of filePath
    @param rootPath If defined any relative url in the list will expanded by the
    root path. If rootPath is set, expandPaths is implicitly true.
    '''
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
        artefact = generateArtefactEntry(None, None, 0, "UnkownAction", None, None)

        for aProp in aElement.findall(XML_PROPERTY, XML_NAMESPACE_DICT):
            if XML_ATTR_KEY in aProp.attrib:
                if aProp.attrib[XML_ATTR_KEY] == defaultProps.INPUT_IDS:
                    value = dict()
                    for aSource in aProp.findall(XML_INPUT_ID, XML_NAMESPACE_DICT):
                        if XML_ATTR_KEY in aSource.attrib:
                            if aSource.attrib[XML_ATTR_KEY] in value:
                                value[aSource.attrib[XML_ATTR_KEY]].append(aSource.text)
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
            artefact[defaultProps.URL] = os.path.normpath(os.path.join(rootPath, artefact[defaultProps.URL]))

        if artefact[defaultProps.URL] is None or not os.path.isfile(artefact[defaultProps.URL]):
            artefact[defaultProps.INVALID] = True
            logging.info("Artefact had no valid URL. Set invalid property to true. Artefact: %s", artefact)

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
                                if id is not None:
                                    xmlInput = ElementTree.SubElement(xmlProp,XML_INPUT_ID, {XML_ATTR_KEY: sourceName})
                                    xmlInput.text = id
                else:
                    if key is defaultProps.URL:
                        if savePathsRelative:
                            try:
                                value = os.path.relpath(artefact[key], rootPath)
                            except:
                                logging.warning(
                                    "Artefact URL cannot be converted to be realtive. Path is keept absolute. Artefact URL: %s",
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
