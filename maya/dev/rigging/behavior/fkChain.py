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
import utils.common.attributes as attributes
import utils.rigging.joints as joints
import utils.rigging.constraints as constraints
import utils.rigging.controls as controls

## import behavior
import behavior

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#      CLASS      #
#=================#
class FkChain(behavior.Behavior):
	"""
	fkChain rig behavior

	Kwargs:
		@behavior
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
		@fkChain
			lockHide(list): lock and hide controls channels
			endJoint(bool)[True]: add control for the end joint
	"""
	def __init__(self, **kwargs):
		super(FkChain, self).__init__(**kwargs)
		self._lockHide = variables.kwargs('lockHide', attributes.Attr.scale, kwargs, shortName='lh')
		self._jointSuffix = variables.kwargs('jointSuffix', 'Fk', kwargs, shortName='jntSfx')
		self._ctrlShape = variables.kwargs('controlShape', 'circle', kwargs, shortName='shape')
		self._end = variables.kwargs('endJoint', True, kwargs, shortName='end')
	def create(self):
		super(FkChain, self).create()

		if isinstance(self._ctrlShape, basestring):
			self._ctrlShape = [self._ctrlShape]*len(self._jnts)

		# create controls
		parent = self._controlsGrp
		jnts = self._jnts
		if not self._end:
			jnts = self._jnts[:-1]
		for jnt, shape in zip(jnts, self._ctrlShape):
			Namer = naming.Namer(jnt)
			Control = controls.create(Namer.description, side=Namer.side, index=Namer.index,
									  offsets=self._offsets, parent=parent, pos=jnt, 
									  lockHide=self._lockHide, shape=shape,
									  size=self._ctrlSize, color=self._ctrlCol, sub=self._sub)

			## connect ctrl to joint
			constraints.matrix_connect(Control.localMatrixAttr, jnt, skip=attributes.Attr.translate)
			constraints.matrix_connect(Control.worldMatrixAttr, jnt, 
									   skip=attributes.Attr.rotate+attributes.Attr.scale)

			self._ctrls.append(Control.name)
			parent = Control.output