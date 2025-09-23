# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact.generator as artefactGenerator
from avid.linkers import CaseLinker, KeyValueLinker, TimePointLinker


class TestKeyValueLinker(unittest.TestCase):
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
    self.a11 = artefactGenerator.generateArtefactEntry("CaseLonePrimary", "1", 0, "LoneAction", "result", "dummy", None)

    self.data = [[self.a1],[self.a2],[self.a3],[self.a4],[self.a5],[self.a6],[self.a7],[self.a8],[self.a9],[self.a10],
                 [self.a1, self.a2],[self.a1, self.a2, self.a3],[self.a1, self.a5],[self.a5, self.a9],[self.a11]]
    self.data2 = [[self.a1, self.a2],[self.a3 , self.a4],[self.a4, self.a5],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]]


  def checkSelections(self, refSelections, testSelections):
    self.assertEqual(len(testSelections), len(refSelections))

    for pos,refSelection in enumerate(refSelections):
      self.assertEqual(len(testSelections[pos]), len(refSelection))
      for posArtefact, artefact in enumerate(refSelection):
        self.assertIn(artefact, testSelections[pos])

  def test_CaseLinker_default(self):
    #check default settings
    linker = CaseLinker()
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a2],[self.a3 , self.a4],[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a6, self.a7], [self.a8, self.a9, self.a10]], selections)

    selections = linker.getLinkedSelection(14, self.data, self.data2)
    self.checkSelections([], selections)

    selections = linker.getLinkedSelection(14, self.data, [])
    self.checkSelections([], selections)


  def test_CaseLinker_internallinkageOn(self):
    linker = CaseLinker(performInternalLinkage=True, allowOnlyFullLinkage=True)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a1],[self.a3 , self.a3],[self.a4 , self.a4]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a5, self.a5], [self.a8, self.a8, self.a8]], selections)

    selections = linker.getLinkedSelection(14, self.data, self.data2)
    self.checkSelections([], selections)

    selections = linker.getLinkedSelection(14, self.data, [])
    self.checkSelections([], selections)

    linker = CaseLinker(performInternalLinkage=True, allowOnlyFullLinkage=False)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a1],[self.a3 , self.a3],[self.a4 , self.a4]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a1 , None],[self.a3 , None],[self.a4 , self.a5],[None , self.a5],[None , self.a8]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a5, self.a5], [self.a8, self.a8, self.a8]], selections)

    selections = linker.getLinkedSelection(14, self.data, self.data2)
    self.checkSelections([], selections)

    selections = linker.getLinkedSelection(14, self.data, [])
    self.checkSelections([], selections)

  def test_CaseLinker_internallinkageOff(self):
    linker = CaseLinker(performInternalLinkage=False, allowOnlyFullLinkage=True)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a2],[self.a3 , self.a4],[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a5, self.a5], [self.a8, self.a8, self.a8]], selections)

    linker = CaseLinker(performInternalLinkage=False, allowOnlyFullLinkage=False)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4],[self.a1, self.a2],[self.a1, self.a2, self.a3],[self.a1, self.a5]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8],[self.a1, self.a5],[self.a5, self.a9]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a2],[self.a3 , self.a4],[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections(self.data2, selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a4, self.a5],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]], selections)


  def test_TimePointLinker_default(self):
    linker = TimePointLinker()
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.checkSelections([[self.a3],[self.a4],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a4],[self.a4, self.a5]], selections)


  def test_TimePointLinker_internalLinkageOn(self):
    linker = TimePointLinker(performInternalLinkage=True, allowOnlyFullLinkage=True)
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.checkSelections([[self.a3],[self.a4],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a3],[self.a4, self.a4],[self.a8, self.a8]], selections)

    linker = TimePointLinker(performInternalLinkage=True, allowOnlyFullLinkage=False)
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.checkSelections([[self.a3],[self.a4],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a3],[self.a4, self.a4],[self.a8, self.a8]], selections)


  def test_KeyValueLinker(self):
    linker = KeyValueLinker(artefactProps.ACTIONTAG)
    selections = linker.getLinkedSelection(0, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a5],[self.a6]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a4]], selections)

    weakLinker = KeyValueLinker(artefactProps.ACTIONTAG, allowOnlyFullLinkage=False)
    selections = weakLinker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a4],[self.a4, self.a5],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]], selections)

    linker = KeyValueLinker(artefactProps.ACTIONTAG)
    selections = linker.getLinkedSelection(0, self.data,[])
    self.assertEqual(len(selections), 0)


if __name__ == '__main__':
    unittest.main()