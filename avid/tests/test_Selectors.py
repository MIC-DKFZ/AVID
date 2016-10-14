import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from avid.selectors import AndSelector
from avid.selectors import ActionTagSelector
from avid.selectors import CaseSelector

class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action2", "result", "dummy", None)
    self.a7 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None)
    self.a8 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a6)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a7)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a8)

  def test_ActionTagSelector(self):
    selector = ActionTagSelector("Action1")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    
  def test_ActionTagSelector_negate(self):
    selector = ActionTagSelector("Action1", negate=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

  def test_CaseSelector(self):
    selector = CaseSelector("Case3")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a7, selection)

  def test_CaseSelector_negate(self):
    selector = CaseSelector("Case3", True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 7)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a8, selection)


  def test_AndSelector(self):
    selector = ActionTagSelector("Action1") + CaseSelector("Case2")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
  
    selector2 = AndSelector(ActionTagSelector("Action1"), CaseSelector("Case2"))
    selection = selector2.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)


if __name__ == '__main__':
    unittest.main()