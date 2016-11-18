import os
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.externals.plastimatch import parseCompareResult
from avid.externals.doseTool import saveSimpleDictAsResultXML

logger = logging.getLogger(__name__)

class plmCompareAction(CLIActionBase):
  '''Class that wraps the single action for the tool mapR.'''

  def __init__(self, refImage, testImage, 
               actionTag = "plmCompare", alwaysDo = False, 
               session = None, additionalActionProps = None, actionConfig = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig)
    self._addInputArtefacts(refImage = refImage, testImage = testImage)
    self._refImage = refImage
    self._testImage = testImage
    
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", actionConfig))
    self._cwd = cwd    
    
  def _generateName(self):
    name = "plmCompare_"+str(artefactHelper.getArtefactProperty(self._refImage,artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._refImage, artefactProps.OBJECTIVE)
    if not objective is None:
      name += '-%s' % objective

    name += "_#" + str(artefactHelper.getArtefactProperty(self._refImage, artefactProps.TIMEPOINT)) \
            + "_vs_" + str(artefactHelper.getArtefactProperty(self._testImage, artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._testImage, artefactProps.OBJECTIVE)
    if not objective is None:
      name += '-%s' % objective

    name += "_#" + str(artefactHelper.getArtefactProperty(self._testImage, artefactProps.TIMEPOINT))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName                    
    self._batchArtefact = self.generateArtefact(self._testImage)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_RTTB_STATS_XML
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "xml"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._refImage,artefactProps.URL)
    input2Path = artefactHelper.getArtefactProperty(self._testImage,artefactProps.URL)
    
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", self._actionConfig)
    
    content = '"' + execURL + '" compare ' + ' "' + inputPath + '"' + ' "' + input2Path +'"'
      
    with open(batPath, "w") as outputFile:
      outputFile.write(content)

    return batPath


  def _postProcessCLIExecution(self):

    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    result = parseCompareResult(open(self._logFilePath).read())

    saveSimpleDictAsResultXML(result, resultPath)


class plmCompareBatchAction(BatchActionBase):    
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  refSelector, testSelector,
               inputLinker = CaseLinker(), 
               actionTag = "plmCompare", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._refImages = refSelector.getSelection(self._session.inData)
    self._testImages = testSelector.getSelection(self._session.inData)

    self._inputLinker = inputLinker
    self._actionConfig = actionConfig


  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    refs = self.ensureValidArtefacts(self._refImages, resultSelector, "plm dice 1st input")
    tests = self.ensureValidArtefacts(self._testImages, resultSelector, "plm dice 2nd input")

    actions = list()

    for (pos,refImage) in enumerate(refs):
      linked2 = self._inputLinker.getLinkedSelection(pos,refs,tests)

      for lt in linked2:
        action = plmCompareAction(refImage, lt,
                            self._actionTag, alwaysDo = self._alwaysDo,
                            session = self._session,
                            additionalActionProps = self._additionalActionProps,
                            actionConfig =self._actionConfig)
        actions.append(action)

    return actions

