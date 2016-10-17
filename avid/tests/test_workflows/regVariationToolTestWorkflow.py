import sys
import os
import argparse

import avid.common.workflow as workflow
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.actions.regVarTool import RegVariationToolBatchAction as regVarTool
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath

__this__ = sys.modules[__name__]

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inFile')
parser.add_argument('-b', '--bootstrap')
args = parser.parse_args()

templatePath = os.path.join(getAVIDProjectRootPath(), "templates", "Gauss_trans.reg.var.xml")

with workflow.initSession(args.inFile, "regVarToolTestSession", True, autoSave = True, bootstrapArtefacts = args.bootstrap) as session:
  
  session.setWorkflowActionTool("regVariationTool","D:\\Dev\\AVID\\source\\Utilities\\RegVariationTool\\regVariationTool.exe")

  regVarTool(ActionTagSelector("Registration"), 5, templatePath, 0.0, 2.0, actionTag = "TestReg").do()
