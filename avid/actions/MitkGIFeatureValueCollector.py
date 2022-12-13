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

from builtins import str
from copy import copy
import logging
import csv

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from ..common.demultiplexer import getSelectors
from . import BatchActionBase
from .pythonAction import PythonAction
from avid.selectors import TypeSelector, KeyValueSelector
from .simpleScheduler import SimpleScheduler
from ..splitter import BaseSplitter
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def _indicate_outputs(actionInstance, selected_features, value_table, row_keys, column_key, **allargs):

    feature_files = actionInstance._inputArtefacts['feature_files']
    refInput = feature_files[0]
    outputs = []
    case_values = artefactHelper.get_all_values_of_a_property(feature_files, artefactProps.CASE)
    case_value = 'COLLECTION'
    if len(case_values) == 1:
        case_value = case_values[0]
    objective_values = artefactHelper.get_all_values_of_a_property(feature_files, artefactProps.OBJECTIVE)
    objective_value = None
    if len(case_values) == 1:
        objective_value = objective_values[0]

    if value_table:
        resultCSV = actionInstance.generateArtefact(refInput, userDefinedProps={artefactProps.CASE: case_value,
                                                                                artefactProps.OBJECTIVE: objective_value,
                                                                                artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                                                artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV},
                                                    urlHumanPrefix=actionInstance.instanceName,urlExtension='csv')
        outputs.append(resultCSV)
    else:
        for feature in selected_features:
            prefix = f'{actionInstance.instanceName}_for_Feature_{feature}'

            resultCSV = actionInstance.generateArtefact(refInput, userDefinedProps={artefactProps.CASE: case_value,
                                                                                    artefactProps.OBJECTIVE: objective_value,
                                                                                    artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                                                    artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV,
                                                                                    artefactProps.RESULT_SUB_TAG: feature},
                                                        urlHumanPrefix=prefix,urlExtension='csv')
            outputs.append(resultCSV)

    return outputs


def _get_feature_values(file_path, value_names=None):
    result = None
    try:
        tree = ET.parse(file_path)

        root = tree.getroot()

        XML_NAMESPACE = 'https://www.mitk.org/Phenotyping'
        namespaces = {'mp': XML_NAMESPACE}

        if root.tag == "{" + XML_NAMESPACE + "}measurement":
            result = {}
            if value_names is None:
                findings = root.findall('./mp:features/mp:feature', namespaces)
                for finding in findings:
                    result[finding.get('name')] = finding.text
            else:
                for name in value_names:
                    result[name] = root.find(f'./mp:features/mp:feature[@name="{name}"]', namespaces).text
    except:
        raise
    return result


def _generate_statistic_rows_recursive(row_files, row_keys, selected_row_key_values):
    row_selectors = getSelectors(propKey=row_keys[0], workflowData=row_files)

    rows = list()
    for row_value in row_selectors:
        selected_row_artefacts = row_selectors[row_value].getSelection(row_files)
        new_row_key_values = [row_value]
        if selected_row_key_values is not None:
            new_row_key_values = selected_row_key_values.copy()
            new_row_key_values.append(row_value)

        if len(row_keys)>1:
            new_rows = _generate_statistic_rows_recursive(row_files=selected_row_artefacts, row_keys=row_keys[1:],
                                                          selected_row_key_values=new_row_key_values)
            rows.extend(new_rows)
        else:
            rows.append([new_row_key_values.copy(), selected_row_artefacts])
    return rows

def _get_output_artefact_by_subresult(artefacts, feature):
    selector = KeyValueSelector(key=artefactProps.RESULT_SUB_TAG, value=feature)
    findings = selector.getSelection(artefacts)

    if len(findings) == 0:
        raise RuntimeError(f'Cannot collect features. Internal state of action seems wrong. Output for feature "{feature}" is missing.')
    elif len(findings) > 1:
        raise RuntimeError(f'Cannot collect features. Internal state of action seems wrong. More then one output for'
                           f' feature "{feature}" defined. Outputs: {findings}')

    return findings[0]

def _generate_statistics(outputs, feature_files, selected_features, value_table, row_keys,
                         column_key, with_headers, fail_on_value_collision, collision_signature, **allargs):
    if not value_table and selected_features is None:
        raise ValueError(
            'If value_table is set to False, selected_feature must be specified.')
    if value_table and column_key is not None:
        raise ValueError(
            'If value_table is set to True, row_key may not be set. But it is set.')

    row_files = _generate_statistic_rows_recursive(row_files=feature_files,row_keys=row_keys,
                                                   selected_row_key_values=None)

    if value_table:
        value_table = list()
        column_names = set()

        for (selected_row_key_values, files_of_row) in row_files:
            new_row = [selected_row_key_values]

            if files_of_row is None:
                new_row.append(None)
            elif len(files_of_row)>1:
                if fail_on_value_collision:
                    raise ValueError('Value collision. At least for one row/column more then input file exist.'
                                     ' Therefore the cell content would be ambiguous. Row: {}; Found'
                                     ' artefacts: {}'.format(selected_row_key_values, files_of_row))
                else:
                    new_row.append(str(collision_signature))
            else:
                file_path = artefactHelper.getArtefactProperty(files_of_row[0], artefactProps.URL)
                values = _get_feature_values(file_path, selected_features)
                new_row.append(values)
                column_names.update(values.keys())
            value_table.append(new_row)

        column_names = sorted(list(column_names))

        outputURL = artefactHelper.getArtefactProperty(outputs[0], artefactProps.URL)
        with open(outputURL, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')

            if with_headers:
                header = row_keys.copy()
                header.extend(column_names)
                writer.writerow(header)

            for (selected_row_key_values, values) in value_table:
                row = selected_row_key_values.copy()
                for column_name in column_names:
                    if values is None:
                        row.append(None)
                    elif isinstance(values,dict):
                        if column_name in values:
                            row.append(values[column_name])
                        else:
                            row.append(None)
                    else: #thats the string with the collision message, just add
                        row.append(values)

                writer.writerow(row)
    else:
        for selected_feature in selected_features:
            column_values = artefactHelper.get_all_values_of_a_property(feature_files, column_key)
            value_table = list()
            if with_headers:
                header = row_keys.copy()
                for value in column_values:
                    header.append('{}: {}'.format(column_key,value))
                value_table.append(header)

            column_selectors = getSelectors(propKey=column_key, workflowData=feature_files)

            for (selected_row_key_values, files_of_row) in row_files:
                new_row = []
                if with_headers:
                    new_row.extend(selected_row_key_values)

                for column_value in column_selectors:
                    cell_artefacts = column_selectors[column_value].getSelection(files_of_row)
                    if cell_artefacts is None or len(cell_artefacts)==0:
                        new_row.append(None)
                    elif len(cell_artefacts)>1:
                        if fail_on_value_collision:
                            raise ValueError('Value collision. At least for one row/column more then input file exist.'
                                             ' Therefore the cell content would be ambuige. Row: {}; Column: {}; Found'
                                             ' artefacts: {}'.format(selected_row_key_values, column_value, cell_artefacts))
                        else:
                            new_row.append(str(collision_signature))
                    else:
                        file_path = artefactHelper.getArtefactProperty(cell_artefacts[0], artefactProps.URL)
                        feature_values = _get_feature_values(file_path,[selected_feature])
                        new_row.append(feature_values[selected_feature])
                value_table.append(new_row)

            output_artefact = _get_output_artefact_by_subresult(outputs, feature=selected_feature)
            outputURL = artefactHelper.getArtefactProperty(output_artefact, artefactProps.URL)
            with open(outputURL, "w", newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                for row in value_table:
                    writer.writerow(row)


class MitkGIFeatureValueCollectorAction(PythonAction):
    """Class that establishes a dose stats collection action on result generate by DoseTool.
       The result will be stored as CSV"""
    def __init__(self, feature_files, selected_features = None, value_table = True, row_keys = None,
                 column_key = None, with_headers=True, fail_on_value_collision = True, collision_signature = 'ERROR', actionTag="MitkGIFeatureValueCollector",
                 alwaysDo=True, session=None, additionalActionProps=None, propInheritanceDict=None):

        if not value_table and selected_features is None:
            raise ValueError(
                'If value_table is set to False, selected_feature must be specified.')
        if value_table and column_key is not None:
            raise ValueError(
                'If value_table is set to True, row_key may not be set. But it is set.')

        if row_keys is None:
            row_keys = [artefactProps.CASE]

        self._row_keys = row_keys
        self._column_key = column_key
        self._value_table = value_table

        aditionalArgs = {'selected_features':selected_features, 'value_table':value_table, 'row_keys': row_keys,
                         'column_key':column_key, 'with_headers':with_headers,
                         'fail_on_value_collision':fail_on_value_collision, 'collision_signature':collision_signature}

        PythonAction.__init__(self, feature_files=feature_files, generateCallable=_generate_statistics, indicateCallable=_indicate_outputs,
                              additionalArgs=aditionalArgs, passOnlyURLs=False, actionTag=actionTag, alwaysDo=alwaysDo,
                              session=session, additionalActionProps=additionalActionProps,
                              propInheritanceDict=propInheritanceDict)

    def _generateName(self):
        name = 'GIFCollection_by_'
        for pos, row_key in enumerate(self._row_keys):
            name += row_key
            if pos < len(self._row_keys)-1:
                name += '-'
        if self._value_table:
            name += '_X_features'
        else:
            name += f'_X_{self._column_key}'

        return name

class MitkGIFeatureValueCollectorBatchAction(BatchActionBase):
    """Batch class for the dose collection actions."""

    def __init__(self, feature_selector, feature_splitter = None,  actionTag="MitkGIFeatureValueCollector",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        splitter = {'feature_files': BaseSplitter()}
        if feature_splitter is not None:
            splitter = {'feature_files': feature_splitter}

        BatchActionBase.__init__(self, primaryInputSelector=feature_selector, splitter=splitter, actionTag=actionTag,
                                 primaryAlias='feature_files', actionClass=MitkGIFeatureValueCollectorAction,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 additionalActionProps=additionalActionProps,scheduler=scheduler,
                                 **singleActionParameters)
