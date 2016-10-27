import os
import logging
import time

from ..common import actionToken
from ..common.artefact.generator import generateArtefactEntry
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from simpleScheduler import SimpleScheduler
import avid.common.workflow as workflow
import avid.selectors as selectors

logger = logging.getLogger(__name__)

class ActionBase(object):
  '''Base class for action objects used in the pipeline.'''
  
  def __init__(self, actionTag, session = None, additionalActionProps = None):
    '''init the action and setting the workflow session, the action is working
      in.
      @param session: Session object of the workflow the action is working in
      @param actionTag: Tag of the action within the session
      @param additionalActionProps: Dictionary that can be used to define additional
      properties that should be added to any artefact that are produced by the action.
    '''
    if session is None:
      #check if we have a current generated global session we can use
      if workflow.currentGeneratedSession is not None:
        self._session = workflow.currentGeneratedSession
      else:
        raise ValueError("Session passed to the action is invalid. Session is None.")
    else: 
      self._session = session
    
    self._actionTag = actionTag
    
    self._additionalActionProps = additionalActionProps
    if self._additionalActionProps is None:
      self._additionalActionProps = {}
      
    self._outputArtefacts = list()

  @property
  def actionTag(self):
    return self._actionTag
    
  @property
  def outputArtefacts(self):
    return self.indicateOutputs()
   
  def indicateOutputs(self):
    ''' Return a list of artefact entries the action will produce if do() is
      called. Reimplement this method for derived actions. The method should
      return complete entries. Therefore the enties should already contain the
      url where they *will* be stored if the action is executed.'''
    if len(self._outputArtefacts) is 0:
      self._outputArtefacts = self._indicateOutputs()
      
    return self._outputArtefacts

  def _indicateOutputs(self):
    ''' Internl function that is called by indicate outputs if no output artefact
      list exists yet. Return a list of artefact entries the action will produce
      if do() is called. The method should
      return complete entries. Therefore the enties should already contain the
      url where they *will* be stored if the action is executed.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: return a list of valid artefact entries
    pass

  @property
  def instanceName(self):
    return self._generateName()

  def _generateName(self):
    ''' Internal function that generates a name for the current action instance
      based on its configuration and input artefacts.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: return a list of valid artefact entries
    pass
      
  def _do(self):
    ''' Internal function that triggers the processing of an action.
      This Method is used internally (e.g. when ever an action is used by an other
      action; and no action tag should be added to the session. '''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: what the action should realy do
    pass


  def do(self, autoTokenAdding = True):
    ''' Triggers the processing of an action. This should be used as public
    trigger of an action. You can control if the resulting session token should
    be automatically added to the session by the optional flag autoTokenAdding.
    Normaly it is activated, but may be usefull to deactivate it if yiu trigger
    an action within an other action. See the schedulers of batch actions for
    example.'''
    global logger
    logger.info("Starting action: "+self.instanceName+" (hash: "+str(self.__hash__())+") ...")

    token = self._do()

    if autoTokenAdding:
      self._session.addActionToken(token)
    
    status = "SUCCESS"
    if token.isSkipped():
      status = "SKIPPED"
    elif token.isFailure():
      status = "FAILURE"
    logger.info("Finished action: "+self.instanceName+" (hash: "+str(self.__hash__())+") -> "+status)
    return token

  def generateActionToken(self, state = actionToken.ACTION_SUCCESS):
    ''' Helper function that creates a action token (with the passed state
    for the current action instance and pass the token back. '''
    token = actionToken.ActionToken(self._session, self.actionTag, self.instanceName, state)
        
    return token



class SingleActionBase(ActionBase):
  '''Base class for action that directly will work on artefact and generate them.'''
  
  def __init__(self, actionTag, alwaysDo = False, session = None, additionalActionProps = None):
    '''init the action and setting the workflow session, the action is working
      in.
      @param session: Session object of the workflow the action is working in
      @param actionTag: Tag of the action within the session
      @param alwaysDo: Indicates if the action should generate its artefacts even
      if they already exist in the workflow (True) or if the action should skip
      the processing (False).      
    '''
    ActionBase.__init__(self, actionTag, session, additionalActionProps)

    self._alwaysDo = alwaysDo
    #CaseInstance that should all artefacts generated by this action have 
    self._caseInstance = None

  def _setCaseInstanceByArtefact(self, *inputArtefacts):
    '''defines the case instance used by the action based on the passed input artefact.'''
    stubArtefact = dict()
    stubArtefact[artefactProps.CASEINSTANCE] = None
    if not artefactHelper.ensureCaseInstanceValidity(stubArtefact, *inputArtefacts):
      logger.warning("Case instance conflict raised by the input artefact of the action. Input artefacts %s", inputArtefacts)
    
    self._caseInstance = stubArtefact[artefactProps.CASEINSTANCE]
    

  def generateArtefact(self, reference = None, copyAdditionalPropsFromReference = True):
    '''Helper method that can be used in derived action classes in their
    indicateOutputs() implementation. It generates an artefact that has the
    actionTag of the current action and all additional action properties.
    Other properties will be taken from the reference (if given). URL will allways
    be None.
    @param reference An other artefact as reference. If given, the following
    properties will be copied to the new artefact: Case, case instance, timepoint,
    type, format, objective.'''
    result = artefactGenerator.generateArtefactEntry(artefactHelper.getArtefactProperty(reference, artefactProps.CASE),\
                                                     self._caseInstance,\
                                                     artefactHelper.getArtefactProperty(reference, artefactProps.TIMEPOINT),\
                                                     self._actionTag,\
                                                     artefactHelper.getArtefactProperty(reference, artefactProps.TYPE),\
                                                     artefactHelper.getArtefactProperty(reference, artefactProps.FORMAT),\
                                                     None,\
                                                     artefactHelper.getArtefactProperty(reference, artefactProps.OBJECTIVE),\
                                                     ** self._additionalActionProps)
    
    if reference is not None and copyAdditionalPropsFromReference:
      k1 = result._additionalProps.keys()
      k2 = reference._additionalProps.keys()
      additionalKs = [x for x in k2 if x not in k1]
      
      for k in additionalKs:
        result[k] = reference[k]
    
    return result;

  
  def _generateOutputs(self):
    ''' Internal execution method of any action. This method should be
      reimplemented in derived classes to do the real work.
      @postcondition: all artefacts indicated by indicateOutputs are correctly created
      and do exist.
      @remark It is *not* needed to add the artefacts to the session or something
      else. This all will be handled by the calling do() method.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: do the action job and generate all artefacts indicated by indicateOutputs,
    #so that they exist after returning from this function.
    pass

  
  def _checkNecessity(self, outputs):
    '''Checks if the workflow already contains the outputs of type 'result' in a valid state.
      @param outputs: Entries that would be generated by the action.
      @return Tupple: 1. indicating if action should run. 2. list of all entries
      that are valid and already available. If 1st is True the list has alternatives
      for all outputs.'''
    global logger
    needed = False
    alternatives = list()
    
    for output in outputs:
      if artefactHelper.getArtefactProperty(output, artefactProps.TYPE) == artefactProps.TYPE_VALUE_RESULT:
        alternative = artefactHelper.findSimilarArtefact(self._session.inData, output)
        if alternative is None\
        or alternative[artefactProps.INVALID]\
        or alternative[artefactProps.URL] is None\
        or not os.path.isfile(alternative[artefactProps.URL]):
          needed = True
        else:
          alternatives += alternative,
          logger.debug("Valid alternative already exists. Indicated output: %s; alternative: %s", str(output), str(alternative))
    
    return (needed,alternatives)
        
  
  def _checkOutputs(self, outputs):
    '''Checks if the given artefacts exists as file. Outputs that do not exist
      are marked as invalid.
      @return a tupple as result. 1. indicating if all outputs are valid. 2. the
      output list with updated validity state.'''
    valid = True
    result = list()
    for output in outputs:
      if os.path.isfile(output[artefactProps.URL]):
        output[artefactProps.INVALID] = False
      else:
        output[artefactProps.INVALID] = True
        valid = False
        global logger
        logger.info("Generated output is invalid and marked as such. Invalid output: %s", str(output))
      result += output,
    
    return (valid,result)

     
  def _do(self):
    ''' Triggers the processing of an action. '''
    global logger

    outputs = self.indicateOutputs()
    (isNeeded, alternatives) = self._checkNecessity(outputs)
    
    token = self.generateActionToken()
    
    if self._alwaysDo or isNeeded:
      isValid = False
      
      starttime = time.time()
      endtime = None

      try:
        self._generateOutputs()
        endtime = time.time()
      except BaseException as e:
        logger.warning('(hash: %s) Error while generating outputs for action tag "%s". All outputs will be marked as invalid. Error details: %s',str(self.__hash__()), self.actionTag, str(e))
        for artefact in outputs:
          artefact[artefactProps.INVALID] = True
      except:
        logger.warning('(hash: %s) Unkown error while generating outputs for action tag "%s". All outputs will be marked as invalid.',str(self.__hash__()), self.actionTag)
        for artefact in outputs:
          artefact[artefactProps.INVALID] = True
      else:
        (isValid, outputs) = self._checkOutputs(outputs)
        
      token.generatedArtefacts = outputs
      
      for artefact in outputs:
        try:
          artefact[artefactProps.EXECUTION_DURATION] = endtime - starttime
        except:
          pass
        
        self._session.addArtefact(artefact, True)

      if not isValid:
        token.state = actionToken.ACTION_FAILUER
    else:
      token.generatedArtefacts = alternatives
      token.state = actionToken.ACTION_SKIPPED
    
    return token



class BatchActionBase(ActionBase):
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self, actionTag, alwaysDo = False, scheduler = SimpleScheduler(), session = None, additionalActionProps = None):
    '''init the action and setting the workflow session, the action is working
      in.
      @param session: Session object of the workflow the action is working in
      @param actionTag: Tag of the action within the session
      @param alwaysDo: Indicates if single actions should generate its artefacts even
      if they already exist in the workflow (True) or if the action should skip
      the processing (False).
      @param scheduler Strategy how to execute the single actions.      
    '''
    ActionBase.__init__(self, actionTag, session, additionalActionProps)

    self._alwaysDo = alwaysDo
    self._actions = None
    self._scheduler = scheduler #scheduler that should be used to execute the jobs
    
    
  def ensureValidArtefacts(self, artefacts, additionalSelector = None, infoTag = "none"):
    ''' Helper function that filters the passed artefact list for valid artefacts.
    Returns the list containing the valid artefacts. If the valid list is empty
    it will be logged as. You may pass additionalSelectors that will also be checked.'''
    afilter = selectors.ValiditySelector()
    if additionalSelector is not None:
      afilter = afilter + additionalSelector
      
    result = afilter.getSelection(artefacts)
    
    if len(result) == 0:
      global logger
      logger.debug("Input selection contains no valid artefacts. Info tag: %s", infoTag)    

    return result   

  def _generateName(self):
    return self.__class__.__name__+"_"+str(self.actionTag)

  def _indicateOutputs(self):
    ''' Return a list of artefact entries the action will produce if do() is
      called. Reimplement this method for derived actions. The method should
      return complete entries. Therefore the enties should already contain the
      url where they *will* be stored if the action is executed.'''
    if self._actions is None:
      self._actions = self._generateActions()
    
    outputs = list()
    
    for action in self._actions:
      outputs += action.indicateOutputs()

    return outputs
  

  def _generateActions(self):
    ''' Internal method that should generate all single actions that should be
      executed and returns them in a list. This method should be
      reimplemented in derived classes to do the real work of dispatching the
      selectors and creating the action functors for all needed actions.
      @postcondition: all needed single actions are created and configured to be
      read to be executed.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: generat all jobs and return them.
    pass
 
    
  def _do(self):
    ''' Triggers the processing of an action. '''
    
    if self._actions is None:
      self._actions = self._generateActions()
      
    tokens = self._scheduler.execute(self._actions)
      
    token = self.generateActionToken(actionToken.ACTION_SKIPPED)

    for aToken in tokens:
      if aToken.isSuccess() and not token.isFailure():
        token.state = actionToken.ACTION_SUCCESS
      elif aToken.isFailure():
        token.state = actionToken.ACTION_FAILUER
        
      token.generatedArtefacts.extend(aToken.generatedArtefacts)

    return token