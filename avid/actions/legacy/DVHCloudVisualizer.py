import sys

from avid.core.Actions.SubActions import rDiagramSeparatedHeaderGenerator,rScriptRunner
from avid.selectors.multiKeyValueSelector import MultiKeyValueSelector
import avid.common.flatFileDictEntries as FFDE


def do(workflow, DVHDoseSelector, DVHVolumeSelector,RTemplateFile, title, xAxisName, yAxisName, actionTag = "DVHCloudVisualizer"):
    ''' the action interface method, which has to be used to start an action '''
    try:
        rDiagramSeparatedHeaderGenerator.do(workflow, DVHDoseSelector, DVHVolumeSelector, RTemplateFile, title, xAxisName, yAxisName, actionTag)
        rScriptRunner.do(workflow,MultiKeyValueSelector(workflow,{FFDE.FORMAT:"r",FFDE.ACTIONTAG: actionTag}), "Rscript")
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise 
