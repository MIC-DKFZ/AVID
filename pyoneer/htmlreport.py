# AVID - pyoneer
# AVID based tool for algorithmic evaluation and optimization
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

import os
import pyhtml as html

def getAllInstanceMeasurementValueKeys(ims):
    vkeys = set()
    for imkey in ims:
        try:
            vkeys = vkeys | set(ims[imkey].keys())
        except:
            pass
    return list(sorted(vkeys))

def getMeasurementValueKeys(ms, onlyWeigted = False):
    '''Returns the value keys of the passed measurement dictionary. Funxtion assumes that all measurements have the
    same values and only checks the first elmeent.'''
    try:
        m = ms[0]
        vkeys = list()
        if onlyWeigted:
            vkeys = m.measureWeights.keys()

        if len(vkeys)==0:
            vkeys = m.measurements.keys()
    except:
        vkeys = list()

    return vkeys

def getWorkflowModKeys(ms):
    '''Returns the workflow modifier keys of the passed measurement dictionary. Function assumes that all measurements
     have the same modifier and only checks the first elmeent.'''
    try:
        m = ms[0]
        vkeys = m.workflowModifier.keys()
    except:
        vkeys = list()

    return sorted(vkeys)

def getValueDisplayName(result, valueKey):
    try:
        return result.valueNames[valueKey]
    except:
        return valueKey

def _generateResultBase(result):
    return html.table(
        html.tr(html.td('Name:'), html.td(result.name)),
        html.tr(html.td('Workflow file:'), html.td(result.workflowFile)),
        html.tr(html.td('Artefact file:'), html.td(result.artefactFile)))

def _generateInstanceHeader(result):
    vkeys = getAllInstanceMeasurementValueKeys(result.instanceMeasurements)
    header = [html.td('Instance descriptor')]
    for vkey in vkeys:
        header.append(html.td(html.a(href='#'+vkey)(getValueDisplayName(result,vkey))))

    return html.tr(*header)

def _generateInstanceContent(result):
    vkeys = getAllInstanceMeasurementValueKeys(result.instanceMeasurements)
    for imkey in result.instanceMeasurements:
        im = result.instanceMeasurements[imkey]
        content = [html.td(str(imkey))]
        for vkey in vkeys:
            try:
                content.append(html.td(im[vkey]))
            except:
                content.append(html.td())

        yield html.tr(*content)

def _generateModifierContent(result):
    for key in result.workflowModifier:
        yield html.tr(html.td(key), html.td(result.workflowModifier[key]))

def _generateMeasurementContent(result):
    for key in sorted(result.measurements):
        try:
            weight = result.measureWeights[key]
        except:
            if len(result.measureWeights)>0:
                weight = 0
            else:
                weight = 1

        yield html.tr(html.td(html.a(href='#'+key)(getValueDisplayName(result,key))), html.td(result.measurements[key]),html.td(weight), html.td(result.measurements_weighted[key]))

def _generateMeasuremntResult(result):
    return html.section(
        html.section(
            html.header(html.h4('Workflow modifier')),
            html.table(
                html.tr(html.th('Parameter'), html.th('Value')),
                _generateModifierContent(result))),
        html.section(html.div('SV measure: ', str(result.svMeasure)),
            html.header(html.h4('Measurments')),
            html.table(
                html.tr(html.th('Name'), html.th('Value'),html.th('Weight'),html.th('Weighted Value')),
                _generateMeasurementContent(result))),
            html.section(html.header(html.h4('Instances')),
                     html.table(
                         _generateInstanceHeader(result),
                         _generateInstanceContent(result))))

def _generateValueDescriptionsContent(result):
    valueKeys = list(set(result.valueNames.keys())|set(result.valueDescriptions.keys()))
    for key in valueKeys:
        try:
            name = result.valueNames[key]
        except:
            name = ''

        try:
            desc = result.valueDescriptions[key]
        except:
            desc = ''

        yield html.tr(html.td(id=key)(name), html.td(desc))

def _generateValueDescriptions(result):
    return html.table(
        html.tr(html.th('Name:'), html.th('Description')),
        _generateValueDescriptionsContent(result))

def generateEvaluationReport(result):
    '''generates an html (string) based on the passsed evaluation result'''
    report = html.html(
        html.head(
            html.title('AVID pyoneer - evaluation report'),
        html.body(
            html.section(
                html.header(html.h2('General Info')),
                _generateResultBase(result)),
            html.section(
                html.header(html.h2('Evaluation results')),
                _generateMeasuremntResult(result)),
            html.section(
                html.header(html.h2('Legend:')),
                _generateValueDescriptions(result)))))

    return report.render()

def _generateBestDetails(result):
    content = list()
    for aBest in result.best:
        content.append(html.section(html.h3(id='#cand_'+aBest.label)('Candidate: {}'.format(aBest.label)),_generateMeasuremntResult(aBest)))
    return content

def _generateCandidatesOverview(result, showBest = True):
    ms = result.best
    if not showBest:
        ms = result.candidates

    vkeys = getMeasurementValueKeys(ms, onlyWeigted=True)
    wmkeys = getWorkflowModKeys(ms)
    tablecontent = list()

    headers = list([html.th('Label'), html.th('SV score')])
    for wmkey in wmkeys:
        headers.append(html.th(wmkey))

    plotNames = list()
    plotValues = dict()
    if not showBest:
        plotValues['SV'] = list()

    for vkey in vkeys:
        headers.append(html.th(html.a(href='#'+vkey)(getValueDisplayName(result,vkey))))
        if showBest:
            plotValues[vkey] = list()

    tablecontent.append(html.tr(*headers))


    for m in ms:
        rowcontent = list()
        if showBest:
            rowcontent.append(html.td(html.a(href='#cand_'+m.label)(m.label)))
        else:
            rowcontent.append(html.td(m.label))

        plotNames.append(m.label)

        rowcontent.append(html.td(m.svMeasure))

        for wmkey in wmkeys:
            rowcontent.append(html.td(m.workflowModifier[wmkey]))

        for vkey in vkeys:
            rowcontent.append(html.td(m.measurements[vkey]))
            if showBest:
                plotValues[vkey].append(m.measurements_weighted[vkey])

        if not showBest:
            plotValues['SV'].append(m.svMeasure)

        tablecontent.append(html.tr(*rowcontent))

    chartKey = 'chart_candidate'
    if showBest:
        chartKey = 'chart_details'

    genStr = "var chart = c3.generate({bindto: '#"+chartKey+"',data: {x: 'x', columns: ["
    for pos, vk in enumerate(plotValues):
        if not pos == 0:
            genStr+=', '
        genStr+="['"+getValueDisplayName(result,vk)+"'"
        for v in plotValues[vk]:
            genStr+=", "+str(v)
        genStr+="]"

    genStr += ", ['x'"
    for name in plotNames:
        genStr += ", '" + str(name)+"'"
    genStr += "]"

    genStr += "]"
    if showBest:
        genStr +=", type: 'bar', groups: [["
        for pos, vk in enumerate(plotValues):
            if not pos == 0:
                genStr+=', '
            genStr+="'"+getValueDisplayName(result,vk)+"'"
        genStr += "]]"
    genStr += "}, axis: { x: {type: 'category'}}"

    if not showBest:
        genStr += ", subchart: {show: true}"

    genStr += '})'

    return html.div(html.script(type = "text/javascript", src = "http://cdnjs.cloudflare.com/ajax/libs/d3/3.5.0/d3.js"),
                    html.script(type = "text/javascript", src = "http://cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.js"),
                    html.link(href = "http://cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.css", rel = "stylesheet", type = "text/css"),
                    html.table(*tablecontent),
                    html.div(id = chartKey),
                    html.script(genStr))


def generateOptimizationReport(result):
    '''generates an html (string) based on the passsed optimization result'''
    report = html.html(
        html.head(
            html.title('AVID pyoneer - optimization report')),
        html.body(
            html.section(
                html.header(html.h2('General Info')),
                _generateResultBase(result)),
            html.section(
                html.header(html.h2('Best Candidates')),
                _generateCandidatesOverview(result, showBest= True)),
            html.section(
                html.header(html.h2('All Candidates')),
                _generateCandidatesOverview(result, showBest=False)),
            html.section(
                html.header(html.h2('Best candidates details')),
                _generateBestDetails(result)),
            html.section(
                html.header(html.h2('Legend:')),
                _generateValueDescriptions(result))
        ))
    return report.render()