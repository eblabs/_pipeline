#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds

## import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.transforms as transforms
import utils.common.attributes as attributes
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import utils.rigging.constraints as constraints

## import component
import component

## import behavior
import dev.rigging.behavior.splineIk as splineIkBhv

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger, COMPONENT_PATH

#=================#
#      CLASS      #
#=================#
class SplineIk(component.Component):
	"""
	spline ik component base class
	
	Args:
		component(str)
	Kwargs:
		side(str)
		description(str)
		index(int)
		parent(str)
		blueprintJoints(list)
		offsets(int): controls' offset groups
		controlSize(float)
		controlColor(str/int): None will follow the side's preset
		subControl(bool)[True]
		blueprintCurve(str): blueprint curve position
		rebuildCurve(bool)[True]: rebuild curve
	Returns:
		Component(obj)
	"""
	def __init__(self, *arg, **kwargs):
		super(SplineIk, self).__init__(*arg, **kwargs)
		self._componentType = COMPONENT_PATH + '.splineIk'
		self._suffix = 'IkSpline'
		self._iks = []

	def register_kwargs(self):
		super(SplineIk, self).register_kwargs()
		self._kwargs.update({'bpCrv': ['blueprintCurve', None, 'bpCrv'],
							 'rebuild': ['rebuildCurve', True, 'rebuild']})

	def create_component(self):
		super(SplineIk, self).create_component()

		kwargs = {'side': self._side,
				  'description': self._des,
				  'index': self._index,
				  'blueprintJoints': self._bpJnts,
				  'jointSuffix': self._suffix,
				  'offsets': self._offsets,
				  'controlSize': self._ctrlSize,
				  'controlColor': self._ctrlCol,
				  'subControl': self._sub,
				  'blueprintCurve': self._bpCrv,
				  'rebuildCurve': self._rebuild,

				  'controlsGrp': self._controlsGrp,
				  'jointsGrp': self._jointsGrp,
				  'nodesHideGrp': self._nodesHideGrp,
				  'nodesShowGrp': self._nodesShowGrp,
				  'nodesWorldGrp': self._nodesWorldGrp}

		Behavior = splineIkBhv.SplineIk(**kwargs)
		Behavior.create()

		# pass info
		self._jnts += Behavior._jnts
		self._ctrls += Behavior._ctrls
		self._iks += Behavior._iks
		self._nodesHide += Behavior._nodesHide