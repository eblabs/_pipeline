#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds
import maya.mel as mel

## import utils
import utils.common.naming as naming
import utils.common.variables as variables
import utils.common.attributes as attributes
import utils.common.transforms as transforms
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
import utils.modeling.curves as curves
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
class SplineIk(behavior.Behavior):
	"""
	spline ik rig behavior
	
	create simple spline ik with tweakers

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
			nodesHideGrp(str): transform node to parent hidden nodes
			nodesShowGrp(str): transform node to parent visible nodes
			nodesWorldGrp(str): transform node to parent world rig nodes
		@splineIk
			blueprintCurve(str): blueprint curve position
			rebuildCurve(bool)[True]: rebuild curve
		
	"""
	def __init__(self, **kwargs):
		super(SplineIk, self).__init__(**kwargs)
		self._jointSuffix = variables.kwargs('jointSuffix', 'IkSpline', kwargs, shortName='jntSfx')		
		self._ctrlSize = variables.kwargs('controlShape', 'cube', kwargs, shortName='shape')
		self._bpCrv = variables.kwargs('blueprintCurve', None, 
										kwargs, shortName=naming.Type.blueprintCurve)
		self._rebuild = variables.kwargs('rebuildCurve', True, kwargs, shortName='rebuild')

		self._iks = []

	def create(self):
		super(SplineIk, self).create()

		# create local joint chain
		self._jntsLocal = joints.create_on_hierarchy(self._jnts, '', '', 
								suffix='Local', parent=self._nodesWorldGrp, vis=False)

		# get blueprint curve
		if not self._bpCrv or not cmds.objExists(self._bpCrv):
			self._bpCrv = naming.Namer(type=naming.Type.blueprintCurve, side=self._side,
									   description=self._des+self._jointSuffix, 
									   index=self._index)
			curves.create_curve_on_nodes(self._bpCrv, self._jnts)
			Logger.WARN('Blueprint curve is not given, create curve base on joints')

		# create curve
		self._crv = naming.Namer(type=naming.Type.curve, side=self._side,
								 description=self._des+self._jointSuffix, 
								 index=self._index).name

		cmds.duplicate(self._bpCrv, name=self._crv)

		# create tweak controls and connect with curve

		crvShape = cmds.listRelatives(self._crv, s=True)[0]
		crvInfo = curves.get_curve_info(crvShape)

		pntList = crvInfo['controlVertices']

		for i, pos in enumerate(pntList):
			Control = controls.create(self._des+self._jointSuffix+'Tweak{:03d}'.format(i+1),
									  side=self._side, 
									  index=self._index,
									  offset=self._offsets,
									  pos=[pos,None],
									  lockHide=attributes.Attr.rotate + 
									  		   attributes.Attr.scale + 
									  		   attributes.Attr.rotateOrder,
									  shape=self._ctrlShape,
									  size=self._ctrlSize,
									  color=self._ctrlCol,
									  sub=self._sub,
									  parent=self._controlsGrp)

			decompose = nodeUtils.node(type=naming.Type.decomposeMatrix,
									   side=Control.side,
									   description=Control.description+'Pos',
									   index=Control.index)

			cmds.connectAttr(Control.worldMatrixAttr, decompose+'.inputMatrix')
			for axis in 'XYZ':
				cmds.connectAttr('{}.outputTranslate{}'.format(decompose, axis),
								 '{}.controlPoints[{}].{}Value'.format(crvShape, i, axis.lower()))

			self._ctrls.append(Control.name)

		cmds.parent(self._crv, self._nodesWorldGrp)

		# rebuild curve
		if self._rebuild:
			cvNum = len(pntList)
			rebuildNodes = cmds.rebuildCurve(self._crv, ch=1, rebuildType=0, degree=3, s=cvNum-1, keepRange=0, rpo=False)
			self._crv = cmds.rename(rebuildNodes[0], self._crv+'Rebuild')
			cmds.setAttr(self._crv+'.inheritsTransform', 1)
			cmds.parent(self._crv, self._nodesWorldGrp)

		# ik Handle
		ikHandle = naming.Namer(type=naming.Type.ikHandle, side=self._side,
								description=self._des+self._jointSuffix, 
								index=self._index).name
		cmds.ikHandle(sj=self._jntsLocal[0], ee=self._jntsLocal[-1], sol='ikSplineSolver',
					  ccv=False, scv=False, curve=self._crv, parentCurve=False, 
					  name=ikHandle)

		cmds.parent(ikHandle, self._nodesWorldGrp)

		self._iks = [ikHandle]

		# zero out joints offsets
		cmds.makeIdentity(self._jntsLocal[0], apply=True, t=1, r=1, s=1)
		
		# twist
		for ctrl, jnt, attr, pos in zip([self._ctrls[0], self._ctrls[-1]],
								   		[self._jntsLocal[0], self._jntsLocal[-1]],
								   		['dWorldUpMatrix', 'dWorldUpMatrixEnd'],
								   		['Bot', 'Top']):
			Control = controls.Control(ctrl)
			matrixJnt = cmds.getAttr(jnt+'.worldMatrix[0]')
			matrixLocal = mathUtils.get_local_matrix(matrixJnt, Control.worldMatrix)
			multMatrixAttr = nodeUtils.mult_matrix([matrixLocal, 
												    Control.worldMatrixAttr],
												    side=self._side,
												    description=self._des+pos+'Twist',
												    index=self._index)
			cmds.connectAttr(multMatrixAttr, '{}.{}'.format(ikHandle, attr))

		cmds.setAttr(ikHandle+'.dTwistControlEnable', 1)
		cmds.setAttr(ikHandle+'.dWorldUpType', 4)

		# extra twist
		attributes.add_attrs([self._ctrls[0], self._ctrls[-1]], 'twist')
		cmds.connectAttr(self._ctrls[0]+'.twist', ikHandle+'.roll')
		nodeUtils.equation('-{}.twist + {}.twist'.format(self._ctrls[0], self._ctrls[-1]),
						   side=self._side, description=self._des+'TwistExtra',
						   index=self._index, attrs=ikHandle+'.twist')

		# info
		self._nodesWorld = [self._crv, ikHandle]

		# connect local joints with joints
		for jnt, jntLocal in zip(self._jnts, self._jntsLocal):
			cmds.matchTransform(jnt, jntLocal, pos=True, rot=True)
			cmds.makeIdentity(jnt, apply=True, t=1, r=1, s=1)
			for attr in attributes.Attr.transform:
				cmds.connectAttr('{}.{}'.format(jntLocal, attr),
								 '{}.{}'.format(jnt, attr))