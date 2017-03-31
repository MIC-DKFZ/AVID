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

from pyoneer.optimization import OptimizerBase

DECORATOR_MINIMUM = 'minimum'
DECORATOR_MAXIMUM = 'maximum'
DECORATOR_START = 'start'
DECORATOR_SCALING = 'scaling'
DECORATOR_MINIMUM_BOUNDARY = 'minimum_boundary'
DECORATOR_MAXIMUM_BOUNDARY = 'maximum_boundary'


def generateDescriptor(names):
    '''Helper function that generates a search parameter descriptor dict that is used by optimization strategies.'''
    result = dict()
    for name in names:
      result[name] = dict()

    return result


def decorateParameter(descriptor, paramname, decorator, value):
    '''Helper function that adds a user specified decorator for the passed parameter.'''
    if paramname in descriptor:
        descriptor[paramname][decorator] = value
    else:
        raise ValueError('Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname,descriptor))

def decorateMinimum(descriptor, paramname, minimum):
    '''Helper function that adds a minimum for the passed parameter.'''
    if paramname in descriptor:
        descriptor[paramname][DECORATOR_MINIMUM] = minimum
    else:
        raise ValueError('Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname,descriptor))


def decorateMaximum(descriptor, paramname, maximum):
    '''Helper function that adds a maximum for the passed parameter.'''
    if paramname in descriptor:
        descriptor[paramname][DECORATOR_MAXIMUM] = maximum
    else:
        raise ValueError(
            'Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname, descriptor))


def decorateStart(descriptor, paramname, start):
    '''Helper function that adds a start for the passed parameter.'''
    if paramname in descriptor:
        descriptor[paramname][DECORATOR_START] = start
    else:
        raise ValueError(
            'Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname, descriptor))

def decorateMinimumBoundary(descriptor, paramname, boundary):
    '''Helper function that adds a boundary for the passed parameter.'''
    if paramname in descriptor:
        descriptor[paramname][DECORATOR_MINIMUM_BOUNDARY] = boundary
    else:
        raise ValueError('Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname,descriptor))


def decorateMaximumBoundary(descriptor, paramname, boundary):
    '''Helper function that adds a boundary for the passed parameter.'''
    if paramname in descriptor:
        descriptor[paramname][DECORATOR_MAXIMUM_BOUNDARY] = boundary
    else:
        raise ValueError(
            'Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname, descriptor))


def decorateScaling(descriptor, paramname, scaler):
    '''Helper function that adds a scaler instance for the passed parameter. This can be used to specify
       scalings for the parameter value between the evaluation domain (value that the user/workflow sees) and
       the optimization domain (value that the optimizer works with). Remark: All other valued decorators work
       in the evaluation domain.'''
    if paramname in descriptor:
        descriptor[paramname][DECORATOR_SCALING] = scaler
    else:
        raise ValueError(
            'Cannot decorate parameter ({}). It is not part of the descriptor {}.'.format(paramname, descriptor))

def getDecoration(descriptor, paramname, decoration, must_exist = False):
    '''Helper function that get a specified decoration form a parameter descriptor.'''
    try:
        return descriptor[paramname][decoration]
    except:
        if must_exist:
            raise ValueError(
                'Decorate parameter ({}) is not part of the descriptor {}. But must exist.'.format(paramname, descriptor))
        else:
            return None

def getMinimum(descriptor, paramname, must_exist = False):
    '''Helper function that gets the minimum for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MINIMUM, must_exist)

def getMaximum(descriptor, paramname, must_exist = False):
    '''Helper function that gets the maximum for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MAXIMUM, must_exist)

def getStart(descriptor, paramname, must_exist = False):
    '''Helper function that gets the start for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_START, must_exist)

def getMinimumBoundary(descriptor, paramname, must_exist = False):
    '''Helper function that gets the boundary for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MINIMUM_BOUNDARY, must_exist)

def getMaximumBoundary(descriptor, paramname, must_exist = False):
    '''Helper function that gets the boundary for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MAXIMUM_BOUNDARY, must_exist)

def getScaling(descriptor, paramname, must_exist = False):
    '''Helper function that gets the scaler instance for the passed parameter. If parameter or decoration is not defined, None will be returned.
       Scaler specify the scalings for the parameter value between the evaluation domain (value that the user/workflow sees) and
       the optimization domain (value that the optimizer works with). Remark: All other valued decorators work
       in the evaluation domain.'''
    return getDecoration(descriptor, paramname, DECORATOR_SCALING, must_exist)

