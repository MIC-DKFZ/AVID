
import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.plmDice import plmDiceBatchAction as plmDice
from avid.selectors.keyValueSelector import ActionTagSelector
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

class TestPlmDice(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "plmDiceTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "plmDiceTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_plmDice")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_plm_dice_action(self):
      
      action = plmDice(ActionTagSelector("Target"), ActionTagSelector("Moving"), actionTag = "TestDice")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      refFile = os.path.join(self.testDataDir, "plmDice_Target_#0_vs_Moving_#1_ref.xml")
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefact,
                                                      artefactProps.URL)
      self.assertEqual(open(refFile).read(), open(resultFile).read())

      refFile = os.path.join(self.testDataDir, "plmDice_Target_#0_vs_Moving_#2_ref.xml")
      resultFile = artefactHelper.getArtefactProperty(action._actions[1]._resultArtefact,
                                                      artefactProps.URL)
      self.assertEqual(open(refFile).read(), open(resultFile).read())

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_plm_dice_action_alwaysdo(self):
      
      action = plmDice(ActionTagSelector("Target"), ActionTagSelector("Moving"), alwaysDo = True, actionTag = "TestDice")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()