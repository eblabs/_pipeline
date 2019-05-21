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
		side(str)
		description(str)
		index(int)
		blueprintJoints(list)
		jointSuffix(str)
		createJoints(bool): False will use blueprint joints as joints directly
		offsets(int): controls' offset groups
		controlSize(float)
		controlColor(str/int): None will follow the side's preset
		subControl(bool)[True]
		controlsGrp(str): transform node to parent controls
		jointsGrp(str): transform node to parent joints
		nodesLocalGrp(str): transform node to parent local rig nodes
		nodesHideGrp(str): transform node to parent hidden nodes
		nodesShowGrp(str): transform node to parent visible nodes
		lockHide(list): lock and hide controls channels
		controlShape(str): controls shape
	"""
	def __init__(self, **kwargs):
		super(FkChain, self).__init__(**kwargs)
		self._lockHide = variables.kwargs('lockHide', attributes.Attr.scale, kwargs, shortName='lh')
		self._jointSuffix = variables.kwargs('jointSuffix', 'Fk', kwargs, shortName='jntSfx')
		self._ctrlShape = variables.kwargs('controlShape', 'circle', kwargs, shortName='shape')

	def create(self):
		super(FkChain, self).create()

		# create controls
		parent = self._controlsGrp
		for jnt in self._jnts:
			Namer = naming.Namer(jnt)
			Control = controls.create(Namer.description, side=Namer.side, index=Namer.index,
									  offsets=self._offsets, parent=parent, pos=jnt, 
									  lockHide=self._lockHide, shape=self._ctrlShape,
									  size=self._ctrlSize, color=self._ctrlCol, sub=self._sub)

			## connect ctrl to joint
			constraints.matrix_connect(Control.localMatrixAttr, jnt, skip=attributes.Attr.translate)
			constraints.matrix_connect(Control.worldMatrixAttr, jnt, 
									   skip=attributes.Attr.rotate+attributes.Attr.scale)

			self._ctrls.append(Control.name)
			parent = Control.output