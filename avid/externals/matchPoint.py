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
import os
import xml.etree.ElementTree as ElementTree
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from pointset import PointRepresentation
import csv

logger = logging.getLogger(__name__)

def _addNullKernelToXML(builder, kernelID, dimension):
  builder.start("Kernel", {"ID": str(kernelID), "InputDimensions": str(dimension), "OutputDimensions": str(dimension)})
  builder.start("StreamProvider", {})
  builder.data("NullRegistrationKernelWriter<"+str(dimension)+","+str(dimension)+">")
  builder.end("StreamProvider")
  builder.start("KernelType", {})
  builder.data("NullRegistrationKernel")
  builder.end("KernelType")
  builder.end("Kernel")
  
def _addExpandedFieldKernelToXML(builder, kernelID, dimension, fieldPath):
  builder.start("Kernel", {"ID": str(kernelID), "InputDimensions": str(dimension), "OutputDimensions": str(dimension)})
  builder.start("StreamProvider", {})
  builder.data("ExpandingFieldKernelWriter<"+str(dimension)+","+str(dimension)+">;")
  builder.end("StreamProvider")
  builder.start("KernelType", {})
  builder.data("ExpandedFieldKernel")
  builder.end("KernelType")
  builder.start("FieldPath", {})
  builder.data(str(fieldPath))
  builder.end("FieldPath")
  builder.start("UseNullVector", {})
  builder.data("0")
  builder.end("UseNullVector")
  builder.end("Kernel")

def generateSimpleMAPRegistrationWrapper(deformationFieldPath, wrapperPath, dimension=3, inverse=True):
  """Helper function that generates a mapr file for a given deformation image.
  @param deformationFieldPath: Path to the existing deformation field.
  @param wrapperPath: Path where the wrapper should be stored.
  @param dimension: Indicating the dimensionality of the wrapped registration.
  @param inverse: Indicates if it should be wrapped as direct or inverse
  (default) kernel."""
  
  builder = ElementTree.TreeBuilder()
  
  builder.start("Registration", {})
  builder.start("Tag", {"Name":"RegistrationUID"})
  builder.data("AVID_simple_auto_wrapper")
  builder.end("Tag")
  builder.start("MovingDimensions", {})
  builder.data(str(dimension))
  builder.end("MovingDimensions")
  builder.start("TargetDimensions", {})
  builder.data(str(dimension))
  builder.end("TargetDimensions")
  
  if inverse:
    _addNullKernelToXML(builder, "direct", dimension)
    _addExpandedFieldKernelToXML(builder, "inverse", dimension, deformationFieldPath)
  else:
    _addExpandedFieldKernelToXML(builder, "direct", dimension, deformationFieldPath)
    _addNullKernelToXML(builder, "inverse", dimension)
  
  builder.end("Registration")
    
  root = builder.close()
  tree = ElementTree.ElementTree(root)
  
  try:
    os.makedirs(os.path.split(wrapperPath)[0])
  except:
    pass
  
  if os.path.isfile(wrapperPath):
    os.remove(wrapperPath)
  
  tree.write(wrapperPath, xml_declaration = True)
 
  

def ensureMAPRegistrationArtefact(regArtefact, templateArtefact, session):
  """Helper function that ensures that the returned registration artefact is stored
  in a format that is supported by MatchPoint. If the passed artefact is valid
  or None, it will just a loop through (None is assumed as a valid artefact as
  well in this context). In other cases the function will try to convert/wrap
  the passed artefact/data and return a matchpoint conformant artefact.
  @param regArtefact: the artefact that should be checked, converted if needed.
  @param conversionPath: Path where any conversion artefacts, if needed, should
  be stored.
  @return: Tuple: the first is a boolean indicating if a conversion was necessary;
  the second is the valid (new) artefact. The value (True,None) encodes the
  fact, that a conversion was needed but not possible."""
  registrationPath = artefactHelper.getArtefactProperty(regArtefact,artefactProps.URL)
  registrationType = artefactHelper.getArtefactProperty(regArtefact,artefactProps.FORMAT)
  
  result = None
  conversion = True
  
  if regArtefact is None or registrationType == artefactProps.FORMAT_VALUE_MATCHPOINT:
    #no conversion needed
    result = regArtefact
    conversion = False
  elif registrationType == artefactProps.FORMAT_VALUE_ITK:
    #conversion needed. 
    logging.debug("Conversion of registration artefact needed. Given format is ITK. Generate MatchPoint wrapper. Assume that itk image specifies the deformation field for the inverse kernel.")
    
    templateArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    templateArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_MATCHPOINT

    path = artefactHelper.generateArtefactPath(session, templateArtefact)
    wrappedFile = os.path.split(registrationPath)[1] + "." + str(artefactHelper.getArtefactProperty(templateArtefact,artefactProps.ID)) + ".mapr"
    wrappedFile = os.path.join(path, wrappedFile)    
    
    templateArtefact[artefactProps.URL] = wrappedFile
    
    generateSimpleMAPRegistrationWrapper(registrationPath,wrappedFile,3,True)
    conversion = True
    result = templateArtefact
    
  return (conversion, result)

def load_simple_pointset(filePath):
    '''Loads a point set stored in slicer fcsv format. The points stored in a list as PointRepresentation instances.
    While loaded the points are converted from RAS (slicer) to LPS (DICOM, itk).
    @param filePath Path where the fcsv file is located.
    '''
    points = list()

    if not os.path.isfile(filePath):
        raise ValueError( "Cannot load point set file. File does not exist. File path: " +str(filePath))

    with open(filePath, "rb", newline='') as csvfile:
        pointreader = csv.reader(csvfile, delimiter = " ")

        for row in pointreader:
            point = PointRepresentation(label = None)
            for no ,entry in enumerate(row):
                if no == 0:
                    try:
                        point.x = float(entry)
                    except:
                        ValueError("Cannot convert x element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(row, entry))
                elif no == 1:
                    try:
                        point.y = float(entry)
                    except:
                        ValueError("Cannot convert y element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(row, entry))
                elif no == 2:
                    try:
                        point.z = float(entry)
                    except:
                        ValueError("Cannot convert z element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(row, entry))

    return points


def write_simple_pointset(filePath, pointset):
    from avid.common import osChecker
    osChecker.checkAndCreateDir(os.path.split(filePath)[0])
    with open(filePath, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', lineterminator='\n')

        '''write given values'''
        for point in pointset:
            row = list()
            row.append(point.x)
            row.append(point.y)
            row.append(point.z)
            writer.writerow(row)
