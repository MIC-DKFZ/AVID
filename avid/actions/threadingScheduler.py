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

from builtins import range
from builtins import object
from threading import Thread
import queue

class Worker(Thread):
    def __init__(self, actions, tokens):
      Thread.__init__(self)
      self.actions = actions
      self.tokens = tokens
      self.daemon = True
      self.start()
    
    def run(self):
      try:
        while True:
          action = self.actions.get()
          token = action.do(False)    
          self.tokens.append(token)
          self.actions.task_done()
      except queue.Empty:
        pass


class ThreadingScheduler(object):
  '''Simple threaded scheduler that processes the actions via a thread pool.'''
  def __init__(self, threadcount ):
    self.threadcount = threadcount
  
  def execute(self, actionList):
    
    actionqueue = queue.Queue()
    tokens = list()

    threadcount = self.threadcount
    if threadcount>len(actionList):
      threadcount = len(actionList)

    for action in actionList:
      actionqueue.put(action)
      
    for i in range(threadcount):
      w = Worker(actionqueue, tokens)
      
    actionqueue.join();
           
    return tokens