import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from avid.linkers import AndLinker, LinkerBase
from avid.linkers import CaseLinker
from avid.linkers import TimePointLinker

class TestLinkers(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None)
    self.a7 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action2", "result", "dummy", None)
    self.a8 = artefactGenerator.generateArtefactEntry("Case2", None, 2, "Action2", "result", "dummy", None)
    self.a9 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None)
    self.a10 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a6)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a7)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a8)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a9)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a10)

  def test_LinkerBase(self):
    linker = LinkerBase()
    selection = linker.getLinkedSelection(2, self.data, self.data)
    self.assertEqual(selection, self.data)

    selection = linker.getLinkedSelection(0, self.data, self.data)
    self.assertEqual(selection, self.data)


  def test_AndLinker(self):
    linker = CaseLinker() + TimePointLinker()
    selection = linker.getLinkedSelection(2, self.data,self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
  
    selection = linker.getLinkedSelection(0, self.data,self.data)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a1, selection)
    
    selector2 = AndLinker(CaseLinker(), TimePointLinker())
    selection = selector2.getLinkedSelection(2, self.data,self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)


if __name__ == '__main__':
    unittest.main()