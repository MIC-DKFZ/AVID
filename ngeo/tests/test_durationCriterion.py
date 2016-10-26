import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from ngeo.eval.criteria.durationCriterion import DurationCriterion

class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None, execution_duration = 1)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None, execution_duration = 10)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "config", "dummy", None, execution_duration = 100)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None, execution_duration = 1000, invalid= True)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)

    self.a5 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None, execution_duration = 30)
    self.a6 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "config", "dummy", None, execution_duration = 300)
    self.a7 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None, execution_duration = 3000, invalid= True)

    self.data2 = list()
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a5)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a6)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a7)

  def test_DurationCriterion_instance(self):
    TODO
    selector = ActionTagSelector("Action1")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    
  def test_DurationCriterion_set(self):
    TODO
    selector = ActionTagSelector("Action1", negate=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

  def test_DurationCriterion_names(self):
    TODO
    selector = CaseSelector("Case3")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a7, selection)

  def test_DurationCriterion_descriptions(self):
    TODO
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


if __name__ == '__main__':
    unittest.main()