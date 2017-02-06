__author__ = 'floca'

import sys
import os
import argparse

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import generateArtefactEntry as generateArtefactEntry
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.actions.dummy import DummyBatchAction as dummy
from avid.actions.dummy import DummyCLIBatchAction as dummyCLI
from avid.actions.threadingScheduler import ThreadingScheduler


with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
  #populating dummy artefacts
  for i in range(1,10000):
    entry = generateArtefactEntry('entry_%s'%i, None, 0, 'Input', artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_CSV, 'dummy_%s.txt'%i)
    session.artefacts.append(entry)

  for i in range(1,10000):
    entry = generateArtefactEntry('entry_all', None, 0, 'Input', artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_CSV, 'dummy_%s.txt'%i)
    session.artefacts.append(entry)

    
  #dummy(session.artefacts, scheduler = ThreadingScheduler(10)).do()
  dummyCLI(session.artefacts, scheduler = ThreadingScheduler(10)).do()