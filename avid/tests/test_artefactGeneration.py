import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps

class TestArtefactGeneration(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    self.a2 = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", "misc", "dummy", None, "Head", True, customProp1 = "nice", customProp2 = 42)
    self.a3 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None, None, False)
    self.a4 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFileVersion2.any")
    self.a6 = artefactGenerator.generateArtefactEntry("Case1", 1, 0, "Action2", "result", "dummy", "myCoolFileVersion2.any")

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)

  def test_generateArtefactEntry(self):
    self.assertEqual(self.a1[artefactProps.CASE], "Case1")
    self.assertEqual(self.a1[artefactProps.CASEINSTANCE], None)
    self.assertEqual(self.a1[artefactProps.TIMEPOINT], 0)
    self.assertEqual(self.a1[artefactProps.ACTIONTAG], "Action1")
    self.assertEqual(self.a1[artefactProps.TYPE], "result")
    self.assertEqual(self.a1[artefactProps.FORMAT], "dummy")
    self.assertEqual(self.a1[artefactProps.URL], "myCoolFile.any")
    self.assertEqual(self.a1[artefactProps.OBJECTIVE], None)
    self.assertEqual(self.a1[artefactProps.INVALID], False)

    self.assertEqual(self.a2["customProp1"], "nice")
    self.assertEqual(self.a2["customProp2"], "42")
    self.assertEqual(self.a2[artefactProps.OBJECTIVE], "Head")
    self.assertEqual(self.a2[artefactProps.INVALID], True)
    

  def test_addArtefactToWorkflowData(self):
    workflowData = list()
    workflowData = artefact.addArtefactToWorkflowData(workflowData, self.a1)
    workflowData = artefact.addArtefactToWorkflowData(workflowData, self.a3)
    
    self.assertEqual(len(workflowData), 2)
    self.assertIn(self.a1, workflowData)
    self.assertIn(self.a3, workflowData)
    
    #Check remove simelar is active
    workflowData = artefact.addArtefactToWorkflowData(workflowData, self.a5, True)
    self.assertEqual(len(workflowData), 2)
    self.assertEqual(workflowData[0], self.a3)
    self.assertEqual(workflowData[1], self.a5)

    #Check remove simelar is inactive
    workflowData = artefact.addArtefactToWorkflowData(workflowData, self.a1)
    self.assertEqual(len(workflowData), 3)
    self.assertEqual(workflowData[0], self.a3)
    self.assertEqual(workflowData[1], self.a5)
    self.assertEqual(workflowData[2], self.a1)

  def test_findSimelarArtefact(self):
    self.assertEqual(artefact.findSimilarArtefact(self.data, self.a1), self.a1)
    self.assertEqual(artefact.findSimilarArtefact(self.data, self.a2), self.a2)
    self.assertEqual(artefact.findSimilarArtefact(self.data, self.a4), None)
    self.assertEqual(artefact.findSimilarArtefact(self.data, self.a5), self.a1, "Check if it finds artefact that are only different by URL and returns them")
    
  def test_artefactExists(self):
    self.assertEqual(artefact.artefactExists(self.data, self.a1), True)
    self.assertEqual(artefact.artefactExists(self.data, self.a2), True)
    self.assertEqual(artefact.artefactExists(self.data, self.a4), False)
    self.assertEqual(artefact.artefactExists(self.data, self.a5), True, "Check if it finds artefact that are only different by URL and returns them")
    
  def test_ensureCaseInstanceValidity(self):
    testA = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    result = artefact.ensureCaseInstanceValidity(testA, self.a1, self.a5)
    
    self.assertEqual(result, True)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], None)
    
    result = artefact.ensureCaseInstanceValidity(testA, self.a1, self.a2, self.a5, None)
    
    self.assertEqual(result, True)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], self.a2[artefactProps.CASEINSTANCE])

    #conflict due to different instance testA and self.a3
    result = artefact.ensureCaseInstanceValidity(testA, self.a1, self.a3)
    
    self.assertEqual(result, False)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], self.a2[artefactProps.CASEINSTANCE])

    #conflict due to different instance self.a2 and self.a3
    testA = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    result = artefact.ensureCaseInstanceValidity(testA, self.a2, self.a3)
    
    self.assertEqual(result, False)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], self.a2[artefactProps.CASEINSTANCE])
    

if __name__ == '__main__':
    unittest.main()