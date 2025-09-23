import os

import avid.common.workflow as workflow
from avid.actions.pythonAction import PythonNaryBatchActionV2
from avid.selectors import ActionTagSelector

mr_image_selector = ActionTagSelector('MR')
ct_image_selector = ActionTagSelector('CT')
mask_selector = ActionTagSelector('Seg')

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
with workflow.initSession(bootstrapArtefacts=os.path.join(os.getcwd(),'output', 'bootstrap.avid'),
                          sessionPath=os.path.join(os.getcwd(),'output', 'example'),
                          expandPaths=True) as session:
    action1 = PythonNaryBatchActionV2(primaryInputSelector=mr_image_selector,
                            primaryAlias='mr_images',
                            additionalInputSelectors = {'ct_images': ct_image_selector},
                            actionTag="action_1",
                            generateCallable=my_function,
                            passOnlyURLs=True)

    action2 = PythonNaryBatchActionV2(primaryInputSelector=action1.action_tag_selector,
                                      primaryAlias='action1_images',
                                      additionalInputSelectors = {'masks': mask_selector},
                                      actionTag="action_2",
                                      generateCallable=my_function,
                                      passOnlyURLs=True)
    session.run_batches()
