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
	"""
	def __init__(self, **kwargs):
		self._side = variables.kwargs('side', 'middle', kwargs, shortName='s')
		self._des = variables.kwargs('description', '', kwargs, shortName='des')
		self._index = variables.kwargs('index', None, kwargs, shortName='i')
		self._bpJnts = variables.kwargs('blueprintJoints', [], kwargs, shortName='bpJnts')
		self._jointSuffix = variables.kwargs('jointSuffix', '', kwargs, shortName='jntSfx')
		self._createJoints = variables.kwargs('createJoints', True, kwargs, shortName='create')

		self._offsets = variables.kwargs('offsets', 1, kwargs, shortName=naming.Type.offset)
		self._controlSize = variables.kwargs('controlSize', 1, kwargs, shortName='ctrlSize')

		self._controlsGrp = variables.kwargs('controlsGrp', '', kwargs, shortName=naming.Type.controlsGrp)
		self._jointsGrp = variables.kwargs('jointsGrp', '', kwargs, shortName=naming.Type.jointsGrp)
		self._nodesLocalGrp = variables.kwargs('nodesLocalGrp', '', kwargs, shortName=naming.Type.nodesLocalGrp)
		self._nodesHideGrp = variables.kwargs('nodesHideGrp', '', kwargs, shortName=naming.Type.nodesHideGrp)
		self._nodesShowGrp = variables.kwargs('nodesShowGrp', '', kwargs, shortName=naming.Type.nodesShowGrp)

		self._jnts = []
		self._ctrls = []
		self._nodesLocal = []
		self._nodesHide = []
		self._nodesShow = []

	def create(self):
		if self._createJoints:
			self._jnts = joints.create_on_hierarchy(self._bpJnts,
							naming.Type.blueprintJoint, naming.Type.joint,
							suffix=self._jointSuffix, parent=self._jointsGrp)
		else:
			self._jnts = self._bpJnts