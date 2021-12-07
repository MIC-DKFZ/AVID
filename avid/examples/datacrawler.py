__author__ = 'kleina'

import os

from avid.common.artefact.crawler import runSimpleCrawlerScriptMain
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact.generator import generateArtefactEntry


def fileFunction(pathParts, fileName, fullPath):
    """
    Functor to generate an artefact for a file stored with the BAT project
    storage conventions.

    This is an example datacrawler for the follwoing folder structure:
    data
      - img
            pat1_TP1_MR (in the example, the file name consists of <case case_id>_<date>_<image_id>.nrrd)
            ...
      - mask
            pat1_TP1_Seg1.nrrd (in the example, the file name consists of <case case_id>_<date>_<seg_id>.nrrd)

    """
    result = None
    name, ext = os.path.splitext(fileName)
    try:
        case_id, time, image_id = name.split('_') # first dir is <case case_id>_<date>
        case = case_id # + '_' + time
    except:
        print('Something went wrong extracting case_id, time and image_id. Please check your data naming or datacrawler script.')


    if pathParts[0] == 'img':
        # we are in the base dir of a case. Get the images
        actionTag = image_id
        if 'MR' in image_id:
            actionTag = 'MR'
        elif 'CT' in image_id:
            actionTag = 'CT'
        objective = image_id

        result = generateArtefactEntry(case=case, caseInstance=None, timePoint=time, actionTag=actionTag, artefactType=artefactProps.TYPE_VALUE_RESULT,
                                       artefactFormat=artefactProps.FORMAT_VALUE_ITK, url=fullPath, objective=objective)

    elif pathParts[0] == 'mask':

        objective = image_id

        actionTag = 'Seg'

        result = generateArtefactEntry(case=case, caseInstance=None, timePoint=time, actionTag=actionTag, artefactType=artefactProps.TYPE_VALUE_RESULT, artefactFormat=artefactProps.FORMAT_VALUE_ITK, url=fullPath, objective=objective)

    return result


if __name__ == "__main__":
    runSimpleCrawlerScriptMain(fileFunction)