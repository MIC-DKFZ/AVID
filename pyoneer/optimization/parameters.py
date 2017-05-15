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

'''This module holds helper to construct and interact with a search parameter descriptor (spd).
   SPDs are used to comunicate parameter aspects (e.g. start value, boundaries) to the optimization strategy.
   olDenotes the minimum boundary of a parameter.
   A spd is basicaly a dictionary the keys denote the parameter, the value is a dictionary containing the
   decorations for the parameter.
   Two special decorations are DECORATOR_SCALING_TO_OPT and DECORATOR_SCALING_FROM_OPT. Both serve to
   scale/transform (if needed) between the evaluation domain (value that the user/workflow sees) and the
   optimization domain (value that the optimizer works with). If one of both decorators are not set "no scaling"
   can be assumed. DECORATOR_SCALING_TO_OPT scales into the optimization domain. DECORATOR_SCALING_FROM_OPT scales
   from the optimization domain back to the evaluation domain.'''
DECORATOR_MINIMUM = 'minimum'
DECORATOR_MAXIMUM = 'maximum'
DECORATOR_START = 'start'
DECORATOR_SCALING_TO_OPT = 'scaling_to_opt'
DECORATOR_SCALING_FROM_OPT = 'scaling_from_opt'
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
    decorateParameter(descriptor, paramname, DECORATOR_MINIMUM, minimum)

def decorateMaximum(descriptor, paramname, maximum):
    '''Helper function that adds a maximum for the passed parameter.'''
    decorateParameter(descriptor, paramname, DECORATOR_MAXIMUM, maximum)

def decorateStart(descriptor, paramname, start):
    '''Helper function that adds a start for the passed parameter.'''
    decorateParameter(descriptor, paramname, DECORATOR_START, start)

def decorateMinimumBoundary(descriptor, paramname, boundary):
    '''Helper function that adds a boundary for the passed parameter.'''
    decorateParameter(descriptor, paramname, DECORATOR_MINIMUM_BOUNDARY, boundary)

def decorateMaximumBoundary(descriptor, paramname, boundary):
    '''Helper function that adds a boundary for the passed parameter.'''
    decorateParameter(descriptor, paramname, DECORATOR_MAXIMUM_BOUNDARY, boundary)

def decorateScalingToOpt(descriptor, paramname, scaler):
    '''Helper function that adds a scaler instance for the passed parameter. This can be used to specify
       scalings for the parameter value from the evaluation domain (value that the user/workflow sees) into
       the optimization domain (value that the optimizer works with). Remark: All other valued decorators work
       in the evaluation domain.'''
    decorateParameter(descriptor, paramname, DECORATOR_SCALING_TO_OPT, scaler)

def decorateScalingFromOpt(descriptor, paramname, scaler):
    '''Helper function that adds a scaler instance for the passed parameter. This can be used to specify
       scalings for the parameter value from the optimization domain (value that the optimizer works with) into
       the evaluation domain (value that the user/workflow sees). Remark: All other valued decorators work
       in the evaluation domain.'''
    decorateParameter(descriptor, paramname, DECORATOR_SCALING_FROM_OPT, scaler)

def getDecoration(descriptor, paramname, decoration, must_exist = False, scaleToOpt = False):
    '''Helper function that get a specified decoration form a parameter descriptor.'''
    try:
        val = descriptor[paramname][decoration]
        if scaleToOpt:
            return getScalingToOpt(descriptor,paramname)(val)
        else:
            return val
    except:
        if must_exist:
            raise ValueError(
                'Decorated parameter ({}) is not part of the descriptor {} or does not have the spacified decorator ({}).'.format(paramname, descriptor, decoration))
        else:
            return None

def getMinimum(descriptor, paramname, must_exist = False, scaleToOpt = False):
    '''Helper function that gets the minimum for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MINIMUM, must_exist, scaleToOpt)

def getMaximum(descriptor, paramname, must_exist = False, scaleToOpt = False):
    '''Helper function that gets the maximum for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MAXIMUM, must_exist, scaleToOpt)

def getStart(descriptor, paramname, must_exist = False, scaleToOpt = False):
    '''Helper function that gets the start for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_START, must_exist, scaleToOpt)

def getMinimumBoundary(descriptor, paramname, must_exist = False, scaleToOpt = False):
    '''Helper function that gets the boundary for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MINIMUM_BOUNDARY, must_exist, scaleToOpt)

def getMaximumBoundary(descriptor, paramname, must_exist = False, scaleToOpt = False):
    '''Helper function that gets the boundary for the passed parameter. If parameter or decoration is not defined, None will be returned.'''
    return getDecoration(descriptor, paramname, DECORATOR_MAXIMUM_BOUNDARY, must_exist, scaleToOpt)

def UnityScaling(val):
    return val

def getScalingToOpt(descriptor, paramname):
    '''Helper function that gets the scaler instance for the passed parameter. If parameter or decoration is not defined,
       a unity scaler (changes nothing) will be returned.'''
    try:
        return getDecoration(descriptor, paramname, DECORATOR_SCALING_TO_OPT, True)
    except:
        return UnityScaling

def getScalingFromOpt(descriptor, paramname):
    '''Helper function that gets the scaler instance for the passed parameter. If parameter or decoration is not defined,
       a unity scaler (changes nothing) will be returned.'''
    try:
        return getDecoration(descriptor, paramname, DECORATOR_SCALING_FROM_OPT, True)
    except:
        return UnityScaling
