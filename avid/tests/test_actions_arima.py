import unittest, os, shutil
import avid.common.workflow as workflow
from avid.actions.arima import ArimaBatchAction as arima
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.selectors.keyValueSelector import DoseStatSelector

class TestArima(unittest.TestCase):
  def setUp(self):
    self.testDataDir = os.path.join(os.path.split(__file__)[0], "data", "arimaTest")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0], "data", "arimaTest", "testlist.avid")
    self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary_test_arima")

    self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True,
                                        bootstrapArtefacts=self.testArtefactFile)

  def tearDown(self):
    try:
      shutil.rmtree(self.sessionDir)
    except:
      pass

  def test_simple_arima_action(self):

    action = arima(ActionTagSelector("collector")+DoseStatSelector("maximum"), planSelector=ActionTagSelector("plan"), selectedStats="maximum", actionTag="SimpleArima")
    token = action.do()
    self.assertEqual(token.isSuccess(), True)
    token = action.do()
    self.assertEqual(token.isSkipped(), True)


if __name__ == "__main__":
  unittest.main()
