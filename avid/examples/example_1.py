import os

import avid.common.workflow as workflow
from avid.linkers import TimePointLinker, CaseLinker, CaseInstanceLinker

from avid.selectors import ActionTagSelector as ATS
from avid.actions.pythonAction import PythonNaryBatchActionV2
from avid.splitter import CaseSplitter

mr_image_selector = ATS('MR')
ct_image_selector = ATS('CT')
mask_selector = ATS('Seg')

###############################################################################
# Define callable
###############################################################################
def my_function(outputs, **kwargs):
    '''
        Simple print-callable that outputs the combinations of input artifacts.
    '''
    keys = kwargs.keys()
    print_output = 'output: {'

    for i, key in enumerate(keys):
        if i != 0:
            print_output += ', '
        print_output += '{}:{}'.format(key, [os.path.basename(mr) for mr in kwargs[key]])
    print_output += '}'

    print(print_output)
    with open(outputs[0], "w") as ofile:
        ofile.write(str(kwargs))

###############################################################################
# Example 1: only select a specific modality (here MR) and make a call per image
###############################################################################
with workflow.initSession(bootstrapArtefacts=os.path.join(os.getcwd(),'output', 'example.avid'),
                          sessionPath=os.path.join(os.getcwd(),'output', 'example'),
                          expandPaths=True) as session:
    PythonNaryBatchActionV2(primaryInputSelector=mr_image_selector,
                            primaryAlias='mr_images',
                            additionalInputSelectors = {'ct_images': ct_image_selector},
                            # additionalInputSelectors = {'masks': mask_selector},
                            # linker={'additional': CaseLinker(allowOnlyFullLinkage=False)+CaseInstanceLinker(allowOnlyFullLinkage=False)},
                            actionTag="example_3",
                            generateCallable=my_function,
                            passOnlyURLs=True).do().tagSelector