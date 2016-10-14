class SimpleScheduler(object):
  '''Simple scheduler implementation that just executes the actions sequentially.'''
  def __init__(self):
    pass
  
  def execute(self, actionList):
    tokens = list()
    
    for action in actionList:
      tokens += action.do(False),
      
    return tokens