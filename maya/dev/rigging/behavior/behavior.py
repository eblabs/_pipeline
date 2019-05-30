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
import utils.rigging.joints as joints
#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#

class Behavior(object):
	"""
	base behavior class

	normally rig component will call behavior in class to do the rig
	
	Kwargs:
		side(str)
		description(str)
		index(int)
		blueprintJoints(list)
		jointSuffix(str)
		createJoints(bool): False will use blueprint joints as joints directly
		offsets(int): controls' offset groups
		controlSize(float)
		controlColor(str/int): None will follow the side's preset
		controlShape(str/list): controls shape
		subControl(bool)[True]
		controlsGrp(str): transform node to parent controls
		jointsGrp(str): transform node to parent joints
		nodesHideGrp(str): transform node to parent hidden nodes
		nodesShowGrp(str): transform node to parent visible nodes
		nodesWorldGrp(str): transform node to parent world rig nodes
	"""
	def __init__(self, **kwargs):
		self._side = variables.kwargs('side', 'middle', kwargs, shortName='s')
		self._des = variables.kwargs('description', '', kwargs, shortName='des')
		self._index = variables.kwargs('index', None, kwargs, shortName='i')
		self._bpJnts = variables.kwargs('blueprintJoints', [], kwargs, shortName='bpJnts')
		self._jointSuffix = variables.kwargs('jointSuffix', '', kwargs, shortName='jntSfx')
		self._createJoints = variables.kwargs('createJoints', True, kwargs, shortName='create')

		self._offsets = variables.kwargs('offsets', 1, kwargs, shortName=naming.Type.offset)
		self._ctrlSize = variables.kwargs('controlSize', 1, kwargs, shortName='size')
		self._ctrlCol = variables.kwargs('controlColor', None, kwargs, shortName='color')
		self._ctrlShape = variables.kwargs('controlShape', 'circle', kwargs, shortName='shape')
		self._sub = variables.kwargs('subControl', True, kwargs, shortName='sub')

		self._controlsGrp = variables.kwargs('controlsGrp', '', kwargs, shortName=naming.Type.controlsGrp)
		self._jointsGrp = variables.kwargs('jointsGrp', '', kwargs, shortName=naming.Type.jointsGrp)
		self._nodesHideGrp = variables.kwargs('nodesHideGrp', '', kwargs, shortName=naming.Type.nodesHideGrp)
		self._nodesShowGrp = variables.kwargs('nodesShowGrp', '', kwargs, shortName=naming.Type.nodesShowGrp)
		self._nodesWorldGrp = variables.kwargs('nodesWorldGrp', '', kwargs, shortName=naming.Type.nodesWorldGrp)

		self._jnts = []
		self._ctrls = []
		self._nodesWorld = []
		self._nodesHide = []
		self._nodesShow = []

	def create(self):
		if self._createJoints:
			self._jnts = joints.create_on_hierarchy(self._bpJnts,
							naming.Type.blueprintJoint, naming.Type.joint,
							suffix=self._jointSuffix, parent=self._jointsGrp)
		else:
			self._jnts = self._bpJnts