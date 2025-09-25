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
import csv
import logging
import os
import xml.etree.ElementTree as ElementTree
from builtins import str

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps

from .pointset import PointRepresentation

logger = logging.getLogger(__name__)

"""Formate type value. Indicating the artefact is stored as a MatchPoint registration object."""
FORMAT_VALUE_MATCHPOINT = "MatchPoint"
"""Formate type value. Indicating the artefact is stored as a MatchPoint simple point set file."""
FORMAT_VALUE_MATCHPOINT_POINTSET = "MatchPoint_pointset"


def _addNullKernelToXML(builder, kernelID, dimension):
    builder.start(
        "Kernel",
        {
            "ID": str(kernelID),
            "InputDimensions": str(dimension),
            "OutputDimensions": str(dimension),
        },
    )
    builder.start("StreamProvider", {})
    builder.data(
        "NullRegistrationKernelWriter<" + str(dimension) + "," + str(dimension) + ">"
    )
    builder.end("StreamProvider")
    builder.start("KernelType", {})
    builder.data("NullRegistrationKernel")
    builder.end("KernelType")
    builder.end("Kernel")


def _addExpandedFieldKernelToXML(builder, kernelID, dimension, fieldPath):
    builder.start(
        "Kernel",
        {
            "ID": str(kernelID),
            "InputDimensions": str(dimension),
            "OutputDimensions": str(dimension),
        },
    )
    builder.start("StreamProvider", {})
    builder.data(
        "ExpandingFieldKernelWriter<" + str(dimension) + "," + str(dimension) + ">;"
    )
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


def generateSimpleMAPRegistrationWrapper(
    deformationFieldPath, wrapperPath, dimension=3, inverse=True
):
    """Helper function that generates a mapr file for a given deformation image.
    @param deformationFieldPath: Path to the existing deformation field.
    @param wrapperPath: Path where the wrapper should be stored.
    @param dimension: Indicating the dimensionality of the wrapped registration.
    @param inverse: Indicates if it should be wrapped as direct or inverse
    (default) kernel."""

    builder = ElementTree.TreeBuilder()

    builder.start("Registration", {})
    builder.start("Tag", {"Name": "RegistrationUID"})
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
        _addExpandedFieldKernelToXML(
            builder, "inverse", dimension, deformationFieldPath
        )
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

    tree.write(wrapperPath, xml_declaration=True)


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
    registrationPath = artefactHelper.getArtefactProperty(
        regArtefact, artefactProps.URL
    )
    registrationType = artefactHelper.getArtefactProperty(
        regArtefact, artefactProps.FORMAT
    )

    result = None
    conversion = True

    if regArtefact is None or registrationType == FORMAT_VALUE_MATCHPOINT:
        # no conversion needed
        result = regArtefact
        conversion = False
    elif registrationType == artefactProps.FORMAT_VALUE_ITK:
        # conversion needed.
        logging.debug(
            "Conversion of registration artefact needed. Given format is ITK. Generate MatchPoint wrapper. Assume that itk image specifies the deformation field for the inverse kernel."
        )

        templateArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
        templateArtefact[artefactProps.FORMAT] = FORMAT_VALUE_MATCHPOINT

        path = artefactHelper.generateArtefactPath(session, templateArtefact)
        wrappedFile = (
            os.path.split(registrationPath)[1]
            + "."
            + str(
                artefactHelper.getArtefactProperty(templateArtefact, artefactProps.ID)
            )
            + ".mapr"
        )
        wrappedFile = os.path.join(path, wrappedFile)

        templateArtefact[artefactProps.URL] = wrappedFile

        generateSimpleMAPRegistrationWrapper(registrationPath, wrappedFile, 3, True)
        conversion = True
        result = templateArtefact

    return (conversion, result)


def getDeformationFieldPath(regPath, getInverseKernel=True):
    """Helper function that retrieves the deformation field specified in a kernel from a matchpoint registration file.
    @param regPath Path to the registration file from where to extract the information.
    @getInverseKernel Indicates if the field file of the inverse kernel (True) or the direct kernel (False) should be
    extracted.
    @return File path to the deformation field. If kernel is not defined by a registration field or registration does
    not exist the return will be None."""
    if not os.path.isfile(regPath):
        raise ValueError(
            "Cannot load evaluation result from file. File does not exist. File path: {}".format(
                regPath
            )
        )

    tree = ElementTree.parse(regPath)
    root = tree.getroot()

    searchPath = "./Kernel[@ID='inverse']/FieldPath"
    if not getInverseKernel:
        searchPath = "./Kernel[@ID='direct']/FieldPath"

    node = root.find(searchPath, namespaces=None)
    try:
        fieldPath = node.text
        if not os.path.isabs(fieldPath):
            fieldPath = os.path.join(os.path.split(regPath)[0], fieldPath)
        return fieldPath
    except:
        return None


def read_simple_pointset(filePath):
    """Loads a point set stored in slicer fcsv format. The points stored in a list as PointRepresentation instances.
    While loaded the points are converted from RAS (slicer) to LPS (DICOM, itk).
    @param filePath Path where the fcsv file is located.
    """
    points = list()

    if not os.path.isfile(filePath):
        raise ValueError(
            "Cannot load point set file. File does not exist. File path: "
            + str(filePath)
        )

    with open(filePath, "rb") as csvfile:
        lines = csvfile.readlines()

        for line in lines:
            values = line.split()
            point = PointRepresentation()
            try:
                point.x = float(values[0])
            except:
                ValueError(
                    "Cannot convert x element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(
                        row, entry
                    )
                )
            try:
                point.y = float(values[1])
            except:
                ValueError(
                    "Cannot convert y element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(
                        row, entry
                    )
                )
            try:
                point.z = float(values[2])
            except:
                ValueError(
                    "Cannot convert z element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(
                        row, entry
                    )
                )

            points.append(point)

    return points


def write_simple_pointset(filePath, pointset):
    from avid.common import osChecker

    osChecker.checkAndCreateDir(os.path.split(filePath)[0])
    with open(filePath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=" ")

        """write given values"""
        for point in pointset:
            row = list()
            row.append(point.x)
            row.append(point.y)
            row.append(point.z)
            writer.writerow(row)
