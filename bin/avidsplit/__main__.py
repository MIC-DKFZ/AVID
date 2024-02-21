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


import argparse
from avid.common.artefact.fileHelper import loadArtefactList_xml, saveArtefactList_xml

import avid.common.demultiplexer as demux
from random import shuffle

import os

from avid.selectors import OrSelector
from avid.selectors import KeyValueSelector


def main():
  mainDesc = "A simple tool to split a AVID artefact files in subsets."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('artefactfile', help = "Specifies the path to the source artefact file that should be analyzed")
  parser.add_argument('outputpath', nargs='?', help = "Specifies the path where the subset files should be stored to.")
  parser.add_argument('--percentage', '-p', nargs='+', type=float, help = 'One can define the percentage of instances that should be distributed into the new subsets. The total sum of numbers must not exceed 100. E.g. calling with "-p 20 20" will result in to subsets files containing 20% (non oberlapping) of the instances each.')
  parser.add_argument('--split-property', '-s', nargs='+',
                  help='Passes a list of property to define instances of artefacts that should/can be distributed into the subsets.')
  parser.add_argument('--baseline', '-b', action='append', nargs=2, metavar=('key', 'value'),
                      help='Allows to specify selection criteria for base line artefacts. Base line artefacts are copied into all subsets and are not distributed. The key is the artefact property name and the value is its content that qualifies base line artifacts.')

  args_dict = vars(parser.parse_args())

  print('AVID diagnostics tool')
  print('')

  artefacts = loadArtefactList_xml(args_dict['artefactfile'], expandPaths=True)
  print('Artefacts loaded from: {}'.format(args_dict['artefactfile']))

  fileNameBase, fileExt = os.path.splitext(args_dict['artefactfile'])
  filePath, fileNameBase = os.path.split(fileNameBase)

  if args_dict['outputpath'] is not None:
    filePath = args_dict['outputpath'];

  split_prop = list()
  if args_dict['split_property'] is not None:
    for prop in args_dict['split_property']:
      split_prop.append(prop)

  baseLineSelector = None
  noBaseLineSelector = None
  if args_dict['baseline'] is not None:
    for base in args_dict['baseline']:
      newSelector = KeyValueSelector(base[0], base[1], allowStringCompare=True)
      if baseLineSelector is None :
        baseLineSelector = newSelector
      else:
        baseLineSelector = baseLineSelector + newSelector
      newNoSelector = KeyValueSelector(base[0], base[1], allowStringCompare=True, negate=True)
      if noBaseLineSelector is None :
        noBaseLineSelector = newNoSelector
      else:
        noBaseLineSelector = OrSelector(noBaseLineSelector,newNoSelector)

  baseArtefacts = baseLineSelector.getSelection(artefacts)
  if len(baseArtefacts) > 0:
    print('Number of base line artefacts: {}'.format(len(baseArtefacts)))

  distArtefacts = noBaseLineSelector.getSelection(artefacts)
  splitInstances = demux.splitArtefact(distArtefacts, *split_prop)
  shuffle(splitInstances)
  print('Number of instances that will be distributed: {}'.format(len(splitInstances)))
  print('')

  subsetSizes = [len(splitInstances)]
  if args_dict['percentage'] is not None:
    subsetSizes = list()
    leftCount = len(splitInstances)
    totalCount = len(splitInstances)
    for subPercentage in args_dict['percentage']:
      subCount = round(totalCount*(subPercentage/100))
      subsetSizes.append(subCount)
      leftCount -= subCount

  for pos, subSize in enumerate(subsetSizes):
    print('Generate subset {}. Instance size: {}'.format(pos+1, subSize))
    subArtefacts = list()
    subArtefacts.extend(baseArtefacts)
    for i in range(subSize):
      subArtefacts.extend(splitInstances[0])
      splitInstances.pop(0)
    subFilePath = os.path.join(filePath, fileNameBase+os.path.extsep+'sub'+str(pos+1)+fileExt)
    saveArtefactList_xml(subFilePath,subArtefacts)

  if len(splitInstances)>0:
    print('Generate subset {}. Instance size: {}'.format(len(subsetSizes)+1, len(splitInstances)))
    subArtefacts = list()
    subArtefacts.extend(baseArtefacts)
    for si in splitInstances:
      subArtefacts.extend(si)
    subFilePath = os.path.join(filePath, fileNameBase+os.path.extsep+'resudial'+fileExt)
    saveArtefactList_xml(subFilePath,subArtefacts)



if __name__ == "__main__":
  main()