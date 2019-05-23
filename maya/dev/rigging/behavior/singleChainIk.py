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
import utils.common.transforms as transforms
import utils.common.nodeUtils as nodeUtils
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
class SingleChainIk(behavior.Behavior):
	"""
	single chain ik rig behavior

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
			controlShape(str): controls shape
			subControl(bool)[True]
			controlsGrp(str): transform node to parent controls
			jointsGrp(str): transform node to parent joints
			nodesLocalGrp(str): transform node to parent local rig nodes
			nodesHideGrp(str): transform node to parent hidden nodes
			nodesShowGrp(str): transform node to parent visible nodes
		@singleChainIk
			ikType(str): ik/aim
		
	"""
	def __init__(self, **kwargs):
		super(SingleChainIk, self).__init__(**kwargs)
		self._ikType = variables.kwargs('ikType', 'ik', kwargs, shortName='ik')
		self._jointSuffix = variables.kwargs('jointSuffix', self._ikType.title(),
											 kwargs, shortName='jntSfx')
		self._iks = []
		self._nodesLocal = []

	def create(self):
		super(SingleChainIk, self).create()

		if isinstance(self._ctrlShape, basestring):
			self._ctrlShape = [self._ctrlShape]*2

		# create controls
		Controls = []
		for jnt, ctrlShape, suffix in zip([self._jnts[0], self._jnts[-1]], 
											 self._ctrlShape,
											 ['Root', 'Target']):
			Namer = naming.Namer(jnt)
			Control = controls.create(Namer.description+suffix,
									  side=Namer.side,
									  index=Namer.index,
									  pos=[jnt, self._jnts[0]],
									  lockHide=attributes.Attr.rotate + attributes.Attr.scale,
									  shape=ctrlShape,
									  size=self._ctrlSize,
									  color=self._ctrlCol,
									  sub=self._sub,
									  parent=self._controlsGrp)
			Control.lock_hide_attrs('ro')
			self._ctrls.append(Control.name)
			Controls.append(Control)

		# connect root jnt with controller
		constraints.matrix_connect(Controls[0].worldMatrixAttr, self._jnts[0], 
									skip=attributes.Attr.rotate+attributes.Attr.scale)

		# unhide target control attrs
		Controls[1].unlock_attrs('rx')

		# set up ik
		if self._ikType == 'ik':
			# ik solver
			ikHandle = naming.Namer(type=naming.Type.ikHandle, side=self._side,
									description=self._des+self._jointSuffix,
									index=self._index).name
			cmds.ikHandle(sj=self._jnts[0], ee=self._jnts[1], sol='ikSCsolver',
						  name=ikHandle)

			# add transform to control ikHandle
			trans = naming.Namer(type=naming.Type.null, side=Controls[1].side,
								 description=Controls[1].description,
								 index=Controls[1].index).name
			trans = transforms.create(trans, pos=Controls[1].name, 
									  parent=self._nodesLocalGrp,
									  lockHide=attributes.Attr.all,
									  vis=False)
			constraints.matrix_connect(Controls[1].worldMatrixAttr, trans)

			# parent ik handle to transform
			cmds.parent(ikHandle, trans)

			# pass info
			self._nodesLocal = [trans]
			self._iks.append(ikHandle)

		else:
			# aim constraint
			twistAttr = nodeUtils.twist_extract(Controls[1].localMatrixAttr)
			composeMatrixTwsit = nodeUtils.compose_matrix([0,0,0], [twistAttr,0,0],
									side=Controls[1].side, 
									description=Controls[1].description+'TwistExtract',
									index=Controls[1].index)
			matrixRoot = cmds.getAttr(self._jnts[0]+'.worldMatrix[0]')
			multMatrixTwist = nodeUtils.mult_matrix([composeMatrixTwsit, matrixRoot],
													side=self._side,
													description=self._des+'AimUp',
													index=self._index)
			constraints.matrix_aim_constraint(Controls[1].worldMatrixAttr, self._jnts[0],
											  worldUpMatrix=multMatrixTwist, local=True)

