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

import sys, os, shutil, stat

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import actionToken 
from . import ActionBase
from . import BatchActionBase
from .simpleScheduler import SimpleScheduler
from os import listdir
from os.path import isfile, join
import logging

logger = logging.getLogger(__name__)

class cleanWorkflowAction(ActionBase):
  """Removes the passed selection from the workflow and also deletes the referenced files"""
  
  def __init__(self, deleteArtefact, deleteWholeDirectory=False, removeWriteProtection=False, actionTag = "clean", session = None, additionalActionProps = None):
    ActionBase.__init__(self, actionTag, session, additionalActionProps)

    self._deleteArtefact = deleteArtefact
    self._deleteWholeDirectory = deleteWholeDirectory
    self._removeWriteProtection = removeWriteProtection

  def _generateName(self):
    name = "Clean_"+str(artefactHelper.getArtefactProperty(self._deleteArtefact,artefactProps.ACTIONTAG))
    return name
     
  def _indicateOutputs(self):
    return list()
    
  def _do(self):
    """Removes the passed selection from the workflow and also deletes the referenced files"""
    try:
        delURL = artefactHelper.getArtefactProperty(self._deleteArtefact,artefactProps.URL)
        if delURL:
          if self._deleteWholeDirectory:
            dirToDelete = os.path.dirname(os.path.abspath(delURL))
            if os.path.exists(dirToDelete):
              if self._removeWriteProtection:
                files = self._getListOfFiles(dirToDelete)
                self._removeWriteProtection(dirToDelete, files)
              shutil.rmtree(dirToDelete)
          else:
            self._session.inData.remove(self._deleteArtefact)
            os.remove(delURL)
        else:
          logger.info("nothing deleted!")

    except:
      logger.error("Unexpected error: %s", sys.exc_info()[0])
      raise    
    
    token = self.generateActionToken()
    
    return token


  def _getListOfFiles(self, directory):
    allFiles = [ f for f in listdir(directory) if isfile(join(directory,f)) ]
    return allFiles


  def _removeWriteProtection(self, directory, files):
    for aFile in files:
      fileWithDirectory = os.path.join(directory, aFile)
      os.chmod(fileWithDirectory, stat.S_IWRITE )


class cleanWorkflowBatchAction(BatchActionBase):    
  '''Batch action work the cleaning of the workflow.'''
  
  def __init__(self, deleteSelector, deleteWholeDirectory=False, removeWriteProtection=False,
               actionTag = "clean", session = None, additionalActionProps = None, scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, True, scheduler, session, additionalActionProps)

    self._deleteArtefacts = deleteSelector.getSelection(self._session.inData)
    
    self._deleteWholeDirectory = deleteWholeDirectory
    self._removeWriteProtection = removeWriteProtection

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    
    actions = list()
    
    for artefact in self._deleteArtefacts:
      action = cleanWorkflowAction(artefact, self._deleteWholeDirectory, self._removeWriteProtection,
                              self._actionTag, session = self._session,
                              additionalActionProps = self._additionalActionProps)
      actions.append(action)
    
    return actions
