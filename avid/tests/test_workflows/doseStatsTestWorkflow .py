import sys
import os

import avid.common.workflow as workflow
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.actions.doseStats import DoseStatBatchAction as doseStats

__this__ = sys.modules[__name__]


with workflow.initSession_byCLIargs(name = "doseStatsTestSession", expandPaths = True, autoSave = True) as session:

  doseStats(ActionTagSelector("dose"), ActionTagSelector("struct"), ["PTV"]).do()
