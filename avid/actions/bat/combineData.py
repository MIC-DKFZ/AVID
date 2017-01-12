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

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
import avid.common.demultiplexer as demux
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.sorter.timePointSorter import TimePointSorter

logger = logging.getLogger(__name__)

class CombineDataAction(CLIActionBase):
  '''Class that wraps the single action for Matlab script combineRegisteredData.'''

  def __init__(self, inputImages, scriptDirectory,
               actionTag = "combineData", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe")):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, scriptDirectory)
    
    inputs = dict();
    for pos, aInput in enumerate(inputImages):
      inputs[str(pos)] = aInput
      
    self._addInputArtefacts(**inputs)
    
    sorter = TimePointSorter()
    
    self._inputImages = sorter.sortSelection(inputImages)
    self._matlab = matlab
    
  def _generateName(self):
    name = "combined_"+str(artefactHelper.getArtefactProperty(self._inputImages[0],artefactProps.ACTIONTAG))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName
                  
    self._batchArtefact = self.generateArtefact(self._inputImages[0])
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + ".bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "matlab", self._matlab)
    
    content = '"' + execURL + '" -wait -nodisplay -nosplash -nodesktop -r "inputs = {'
       
    for inputImage in self._inputImages:
      inputPath = artefactHelper.getArtefactProperty(inputImage,artefactProps.URL)
      content += "'" + inputPath + "' "
      
    content += '}; combineRegisteredData( inputs, ' + "'"+resultPath+"'" + '); exit;"'
      
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      


class CombineDataBatchAction(BatchActionBase):    
  '''Batch action that uses the BAT combineRegisteredData matlab script.
     It will combine all given data of case/instance. The data will be sorted
     by timepoint.'''
  
  def __init__(self,  inputSelector, scriptDirectory, actionTag = "combineData", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe"), scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputImages = inputSelector.getSelection(self._session.inData)
    self._matlab = matlab
    self._scriptDirectory = scriptDirectory

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureRelevantArtefacts(self._inputImages, resultSelector, "combine Data inputs")
        
    actions = list()
    
    caseSelectorDict = demux.getSelectors(artefactProps.CASE, workflowData = inputs)

    for case in caseSelectorDict:
      instanceSelectorDict = demux.getSelectors(artefactProps.CASEINSTANCE, caseSelectorDict[case], inputs)
      
      for instance in instanceSelectorDict:
        relevantInputSelector = caseSelectorDict[case] + instanceSelectorDict[instance]
        
        relevantInputs = relevantInputSelector.getSelection(inputs)
        
        action = CombineDataAction(relevantInputs, self._scriptDirectory,
                              self._actionTag,
                              alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              matlab =self._matlab)
        actions.append(action)
    
    return actions
