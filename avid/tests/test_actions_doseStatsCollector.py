
import unittest
import os
import shutil
import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as collector
from avid.selectors import CaseSelector
from avid.selectors import CaseInstanceSelector
from avid.selectors.keyValueSelector import ActionTagSelector

class TestDoseStatsCollector(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "doseStatsCollectorTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "doseStatsCollectorTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_doseStatsCollector")
      self.tempRoot = os.path.join(os.path.split(__file__)[0],"temporary")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.tempRoot)
      except:
        pass


    def readFile(self, filePath):
      result = None
      with open(filePath) as fileHandle:
        result = fileHandle.read()
        
      return result


    def test_simple_batch_action(self):
      
      action = collector(CaseSelector("case_1")+ActionTagSelector("stats"), ["minimum","maximum"])
      token = action.do()
      
      refFile = os.path.join(self.testDataDir, "ref_caseInstance_x_timePoint_maximum.csv")
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefacts["maximum"], artefactProps.URL)
               
      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(self.readFile(refFile), self.readFile(resultFile))


    def test_simple_batch_action_no_rows(self):
      
      action = collector(CaseSelector("case_1")+ActionTagSelector("stats"), ["minimum","maximum"], withHeaders = False, actionTag = "NoHeader")
      token = action.do()

      refFile = os.path.join(self.testDataDir, "ref_noHeader_caseInstance_x_timePoint_minimum.csv")
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefacts["minimum"], artefactProps.URL)
              
      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(self.readFile(refFile), self.readFile(resultFile))


    def test_batch_action_custom_keys(self):     
      action = collector(CaseInstanceSelector("instance_1")+ActionTagSelector("stats"), ["mean","Dx_x=5"], rowKey = artefactProps.CASE, columnKey= artefactProps.OBJECTIVE, actionTag = "CustomKeys")
      token = action.do()

      refFile = os.path.join(self.testDataDir, "ref_case_x_objective_mean.csv")
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefacts["mean"], artefactProps.URL)
               
      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(self.readFile(refFile), self.readFile(resultFile))

    def test_collect_all_batch_action(self):

      action = collector(CaseSelector("case_1")+ActionTagSelector("stats"))
      token = action.do()

      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(sorted(action._actions[0]._resultArtefacts.keys()), sorted(['MOHx_x=10', 'standardDeviation', 'maximum', 'minimum', 'MOCx_x=2', 'MOCx_x=5', 'MinOCx_x=10', 'Dx_x=5', 'Dx_x=2', 'Dx_x=10', 'volume', 'MOCx_x=10', 'Dx_x=98', 'MinOCx_x=5', 'Dx_x=95', 'MaxOHx_x=10', 'Dx_x=90', 'MOHx_x=5', 'MOHx_x=2', 'numberOfVoxels', 'MinOCx_x=2', 'variance', 'MaxOHx_x=2', 'MaxOHx_x=5', 'mean']))


if __name__ == "__main__":
    unittest.main()