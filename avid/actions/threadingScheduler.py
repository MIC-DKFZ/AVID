from threading import Thread
import Queue

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
      except Queue.Empty:
        pass


class ThreadingScheduler(object):
  '''Simple threaded scheduler that processes the actions via a thread pool.'''
  def __init__(self, threadcount ):
    self.threadcount = threadcount
  
  def execute(self, actionList):
    
    actionqueue = Queue.Queue()
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