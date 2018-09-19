# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.


import argparse
from avid.common.artefact import defaultProps
from avid.common.artefact.fileHelper import loadArtefactList_xml

from avid.selectors import SelectorBase, AndSelector
from avid.selectors import ValiditySelector
from avid.selectors.diagnosticSelector import RootSelector, IsInputSelector, IsPrimeInvalidSelector


def main():
  mainDesc = "A simple diagnostics tool to analyse AVID artefact files."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('artefactfile', help = "Specifies the path to the artefact file that should be analyzed")
  parser.add_argument('commands', nargs='*', help="Specifies the type of analysation that should be done.")
  parser.add_argument('--invalids', help = 'Will only analyze or select invalid artefacts.',action='store_true')
  parser.add_argument('--roots', help = 'Will only analyze or select artefacts that have no input artefacts/sources.',action='store_true')
  parser.add_argument('--prime-invalids', help = 'Will only analyze or select invalid artefacts, that have only valid input artefact (or None). Therefore artefacts that "started" a problem. This flag overwrites --invalids',action='store_true')
  parser.add_argument('--sources', help = 'Will only analyze or select artefacts that are inputs for other artefacts.',action='store_true')

  args_dict = vars(parser.parse_args())

  print('AVID diagnostics tool')
  print('')

  artefacts = loadArtefactList_xml(args_dict['artefactfile'], expandPaths=True)
  print('Artefacts loaded from: {}'.format(args_dict['artefactfile']))

  selector = SelectorBase()
  if args_dict['invalids']:
    selector = AndSelector(selector,ValiditySelector(negate = True))
  if args_dict['roots']:
    selector = AndSelector(selector,RootSelector())
  if args_dict['prime_invalids']:
    selector = AndSelector(selector,IsPrimeInvalidSelector())
  if args_dict['sources']:
    selector = AndSelector(selector,IsInputSelector())

  selected_artefacts = selector.getSelection(artefacts)
  print('Number of selected artefacts: {}'.format(len(selected_artefacts)))
  print('')

  #if 'command' in args_dict:
  if len(args_dict['commands']) == 0:
    #default mode

    format_str = '{:4} | {a['+defaultProps.CASE+']:20.20} | {a['+defaultProps.ACTIONTAG+']:20.20} | {a['+defaultProps.TIMEPOINT+']:10} | {a['+defaultProps.INVALID+']:5} | {a['+defaultProps.URL+']}'
    header = {defaultProps.CASE:'Case',defaultProps.ACTIONTAG:'Action tag', defaultProps.TIMEPOINT: 'Timepoint', defaultProps.INVALID: 'Fail', defaultProps.URL: 'URL'}
    print(format_str.format('#', a=header))
    for pos, artefact in enumerate(selected_artefacts):
      print(format_str.format(pos, a=artefact))
  else:
    pass

if __name__ == "__main__":
  main()