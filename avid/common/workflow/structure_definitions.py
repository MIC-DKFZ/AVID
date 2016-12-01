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

import os
import logging
import xml.etree.ElementTree as ElementTree
import re

XML_STRUCT_DEF = "avid:structure_definition"
XML_STRUCTURE = "avid:structure"
XML_STRUCT_PATTERN = "avid:struct_pattern"
XML_ATTR_NAME = "name"
XML_NAMESPACE = "http://www.dkfz.de/en/sidt/avid"
XML_NAMESPACE_DICT = {"avid":XML_NAMESPACE}
CURRENT_XML_VERSION = "1.0"

def loadStructurDefinition_xml(filePath):
  '''Loads a structure definition from an xml file.
  @param filePath Path where the structure definition is located.
  @return Returns a dictionary containing the definition. Key is the name of the
  structure. Value is either None (implying that the name is also the value,
  so no regulare expresion) or a pattern string (regular expresion) if given.
  '''
  struct_defs = dict()

  if not os.path.isfile(filePath):
    raise ValueError("Cannot load structure definitions from file. File does not exist. File path: "+str(filePath))
  
  tree = ElementTree.parse(filePath)
  root = tree.getroot()
  
  if root.tag != "{"+XML_NAMESPACE+"}structure_definition":
    raise ValueError("XML has not the correct root element. Must be 'avid:structure_definition', but is: "+root.tag)
  
  for aElement in root.findall(XML_STRUCTURE, XML_NAMESPACE_DICT):

    name = aElement.get(XML_ATTR_NAME, None)
    if name is None:
      logging.error("Invalid structure definition file. Structure element has no name attribute.")
      raise ValueError("XML seems not to be valid. Structure element has no name attribute.")
    
    value = None

    aRegEx = aElement.find(XML_STRUCT_PATTERN, XML_NAMESPACE_DICT)
    if aRegEx is not None:
        value = aRegEx.text
    
    struct_defs[name] = value
  
  return struct_defs