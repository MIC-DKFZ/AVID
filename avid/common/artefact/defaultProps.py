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

'''
This module is the central unit to store the default artefact propertie keys
To ensure an easier maintenance and upgrade all autoprocessing modules,
'''

'''Unique identifier for an entry'''
ID = "id"
'''Case ID (e.g. Patient ID) should be unique for one subject/person/entity in a cohort'''
CASE = "case"
'''ID for an instance of the case (e.g. for variation analysis)'''
CASEINSTANCE = "caseInstance"
'''ID for time points of data acquisition of a case. Value should be ordinal (e.g. numbers)'''
TIMEPOINT = "timePoint"
'''Tag lable used for a certain action step in the workflow'''
ACTIONTAG = "actionTag"
'''Objective or Object id that can e.g. used to indicates a certain objective of
 an action (e.g. Registration with a special structure, segmentation/mask or statistics
 of a certain organ at risk).'''
OBJECTIVE = "objective"
'''Type of the artefact represented by the entry'''
TYPE = "type"
'''Format of the artefact represented by the entry'''
FORMAT = "format"
'''URL to the artefact stored in a file/resource and indicated by the entry'''
URL = "url"
'''In case actions produce more then one result artefact, this property may be used to make the results distinguishable.'''
RESULT_SUB_TAG = "result_sub_tag"
'''Indicates if a given artefact is valid (True) or not (False).'''
INVALID = "invalid"
'''Creation time of an artefact.'''
TIMESTAMP = "timestamp"
'''Dict with the IDs lists of input artefacts used to generate the artefact.'''
INPUT_IDS = "input_ids"
'''Duration of the action execution that generated the artefact (in [s]).'''
EXECUTION_DURATION = "execution_duration"
'''Name of the action class that used to do/represent the action.'''
ACTION_CLASS = "action_class"
'''UID of the action instance that generated the artefact'''
ACTION_INSTANCE_UID = "action_instance_uid"
'''Defines a reference to a plan file the artefact is associated with. Normaly
this could be found as optional property for virtuos dose artefacts.'''
VIRTUOS_PLAN_REF = "virtuos_plan_ref"
'''Property containes the number of planned fractions associated with a artefact
 (typically a plan). The value of the property should be of type int.'''
PLANNED_FRACTIONS = "planned_fractions"
'''Property containes the prescribed dose associated with a artefact
 (typically a plan). The value of the property should be of type float.'''
PRESCRIBED_DOSE = "prescribed_dose"
'''Element of an accumulation (e.g. dose accumulation)'''
ACC_ELEMENT = "acc_element"

''' Property indicates a certain dose statistic value covered by the associated artefact '''
DOSE_STAT = "dose_stat"
''' Property indicates a certain diagram type covered by the associated artefact '''
DIAGRAM_TYPE = "diagram_type"
''' Property indicates a certain diagram type covered by the associated artefact '''
ONLY_ESTIMATOR = "only_estimator"
''' Property indicates a certain diagram type covered by the associated artefact '''
N_FRACTIONS_FOR_ESTIMATION = "n_fractions_for_estimation"

'''Standard type value. Indicating misc files like batch files for cli execution.'''
TYPE_VALUE_MISC = "misc"
'''Standard type value. Indicating any configuration artefacts that are needed
by an action.'''
TYPE_VALUE_CONFIG = "config"
''' Standard type value. Indicating any result artefacts produced by an action.'''
TYPE_VALUE_RESULT = "result"
''' Standard type value. Indicating any result artefacts that is produced by an action as an interim result
when the extion is processed. It is not the final result of the action and should not be used in normal workflows.'''
TYPE_VALUE_INTERIM = "interim_result"

'''Standard type value. Indicating the artefact is stored as DICOM iod.'''
FORMAT_VALUE_DCM = "dcm"
'''Standard type value. Indicating the artefact is stored as an itk supported image format (e.g. NRRD, MetaImage,...).'''
FORMAT_VALUE_ITK = "itk"
'''Standard type value. Indicating the artefact is stored as an itk supported image format (e.g. NRRD, MetaImage,...).'''
FORMAT_VALUE_ITK_TRANSFORM = "itk_transform"
'''Standard type value. Indicating the artefact is stored in an virtuos format.'''
FORMAT_VALUE_VIRTUOS = "virtuos"
'''Standard type value. Indicating the artefact is stored in an virtuos plan format.'''
FORMAT_VALUE_VIRTUOS_PLAN = "virtuos_plan"
'''Standard type value. Indicating the artefact is stored in an virtuos hed format.'''
FORMAT_VALUE_VIRTUOS_HEAD = "virtuos_head"
'''Standard type value. Indicating the artefact is stored as a comma seperated value file.'''
FORMAT_VALUE_CSV = "csv"
'''Standard type value. Indicating the artefact is stored as a JSON file.'''
FORMAT_VALUE_JSON = "json"
'''Standard type value. Indicating the artefact is stored as a XML file.'''
FORMAT_VALUE_XML = "xml"
'''Standard type value. Indicating the artefact is stored as a bat file/batch script.'''
FORMAT_VALUE_BAT = "bat"
'''Standard type value. Indicating the artefact is stored as a avid tools xml format (legacy).'''
FORMAT_VALUE_AVIDXML = "AVIDXMLConfig"
'''Standard type value. Indicating the artefact is stored as helax DICOM iod.'''
FORMAT_VALUE_HELAX_DCM = "helax"
'''Standard type value. Indicating the artefact is stored as a RTTB result xml.'''
FORMAT_VALUE_RTTB_STATS_XML = "rttb_stats_xml"
'''Standard type value. Indicating the artefact is stored as a RTTB cumulative DVH result xml.'''
FORMAT_VALUE_RTTB_CUM_DVH_XML = "rttb_cum_dvh_xml"
'''Standard type value. Indicating the artefact is stored as a R file.'''
FORMAT_VALUE_R = "R"
'''Standard type value. Indicating the artefact is stored as a PNG file.'''
FORMAT_VALUE_PNG = "PNG"