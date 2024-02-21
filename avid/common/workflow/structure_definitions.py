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

from builtins import str
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