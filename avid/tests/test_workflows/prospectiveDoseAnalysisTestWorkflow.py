__author__ = 'hentsch'

import sys, os

import avid.common.workflow as workflow
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.selectors.keyValueSelector import DoseStatSelector

from avid.actions.prospectiveDoseAnalysisSimulator import ProspectiveDoseAnalysisSimulatorBatchAction as prospectiveDoseAnalysisSimulator
from avid.actions.arima import ArimaBatchAction as arima
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath

__this__ = sys.modules[__name__]

templatePath = os.path.join(getAVIDProjectRootPath(), "templates")

with workflow.initSession_byCLIargs(expandPaths=True, autoSave=True) as session:
  prospectiveDoseAnalysisSimulator(inputSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), actionTag="ProspectiveDoseAnalysis").do()
  prospectiveDoseAnalysisSimulator(inputSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), useOnlyEstimator=True,
                                   actionTag="ProspectiveDoseAnalysis").do()
  prospectiveDoseAnalysisSimulator(inputSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), useAllFractionsForEstimation=False,
                                   nFractionsEstimation=5, actionTag="ProspectiveDoseAnalysis").do()
  prospectiveDoseAnalysisSimulator(inputSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), useAllFractionsForEstimation=False,
                                   nFractionsEstimation=10, actionTag="ProspectiveDoseAnalysis").do()
  arima(doseStatsSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), selectedStats="maximum", planSelector=ActionTagSelector("plan"),
        actionTag="Arima").do()
