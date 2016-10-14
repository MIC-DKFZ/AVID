import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from avid.linkers import CaseInstanceLinker

class TestCaseInstanceLinker(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case2", "a", 1, "Action2", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case2", 4, 2, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case4", "noLink", 0, "Action3", "result", "dummy", None)

    self.slave = list()
    self.slave = artefact.addArtefactToWorkflowData(self.slave, self.a1)
    self.slave = artefact.addArtefactToWorkflowData(self.slave, self.a2)
    self.slave = artefact.addArtefactToWorkflowData(self.slave, self.a3)
    self.slave = artefact.addArtefactToWorkflowData(self.slave, self.a4)
    self.slave = artefact.addArtefactToWorkflowData(self.slave, self.a5)

    self.master = list()
    self.master = artefact.addArtefactToWorkflowData(self.master, self.a1)
    self.master = artefact.addArtefactToWorkflowData(self.master, self.a2)
    self.master = artefact.addArtefactToWorkflowData(self.master, self.a3)
    self.master = artefact.addArtefactToWorkflowData(self.master, self.a6)


  def test_CaseInstanceLinker_strict(self):
    linker = CaseInstanceLinker(True)
    selection = linker.getLinkedSelection(0, self.master, self.slave)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a1, selection)
  
    linker = CaseInstanceLinker(True)
    selection = linker.getLinkedSelection(1, self.master, self.slave)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a4, selection)

    linker = CaseInstanceLinker(True)
    selection = linker.getLinkedSelection(2, self.master, self.slave)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a3, selection)

    linker = CaseInstanceLinker(True)
    selection = linker.getLinkedSelection(3, self.master, self.slave)
    self.assertEqual(len(selection), 0)


  def test_CaseInstanceLinker_not_strict(self):
    linker = CaseInstanceLinker()
    selection = linker.getLinkedSelection(0, self.master, self.slave)
    self.assertEqual(len(selection), 5)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
  
    linker = CaseInstanceLinker()
    selection = linker.getLinkedSelection(1, self.master, self.slave)
    self.assertEqual(len(selection), 3)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a4, selection)

    linker = CaseInstanceLinker()
    selection = linker.getLinkedSelection(2, self.master, self.slave)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a3, selection)

    linker = CaseInstanceLinker()
    selection = linker.getLinkedSelection(3, self.master, self.slave)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a1, selection)


  def test_FractionLinker_empty_slaves(self):
    linker = CaseInstanceLinker()
    selection = linker.getLinkedSelection(2, self.slave, [])
    self.assertEqual(len(selection), 0)
  
    linker = CaseInstanceLinker(True)
    selection = linker.getLinkedSelection(2, self.slave, [])
    self.assertEqual(len(selection), 0)


if __name__ == '__main__':
    unittest.main()