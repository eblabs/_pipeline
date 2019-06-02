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
class RotatePlaneIk(behavior.Behavior):
	"""
	rotate plane ik rig behavior

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
		@rotatePlaneIk
			ikType(str): rp (spring is not availble due to maya issue)
			blueprintControl(str): control blueprint position
			poleVectorDistance(float)
		
	"""
	def __init__(self, **kwargs):
		super(RotatePlaneIk, self).__init__(**kwargs)
		self._ikType = variables.kwargs('ikType', 'rp', kwargs, shortName='ik')
		self._jointSuffix = variables.kwargs('jointSuffix', 'Ik'+self._ikType.title(),
											 kwargs, shortName='jntSfx')
		self._bpCtrl = variables.kwargs('blueprintControl', '', kwargs, shortName='bpCtrl')
		self._distance = variables.kwargs('poleVectorDistance', 1, kwargs, shortName='pvDis')
		self._iks = []

	def create(self):
		super(RotatePlaneIk, self).create()

		if isinstance(self._ctrlShape, basestring):
			self._ctrlShape = [self._ctrlShape]*3

		Ctrls = []
		
		# controls
		for bpJnt, sfx, rot, shape in zip([self._bpJnts[0], self._bpJnts[1], self._bpCtrl],
							  	          ['Pos', 'Pv', ''],
							  	   		  [self._bpJnts[0], None, self._bpCtrl],
							  	   		  self._ctrlShape):
			Control = controls.create(self._des+sfx, side=self._side,
									  index=self._index, offset=self._offsets,
									  pos=[bpJnt, rot],
									  lockHide=attributes.Attr.rotate + 
									  		   attributes.Attr.scale + 
									  		   attributes.Attr.rotateOrder,
									  shape=shape,
									  size=self._ctrlSize,
									  color=self._ctrlCol,
									  sub=self._sub,
									  parent=self._controlsGrp)
			self._ctrls.append(Control.name)
			Ctrls.append(Control)

		# unlock rotate for ik ctrl
		Ctrls[-1].unlock_attrs(attributes.Attr.rotate)
		Ctrls[-1].unlock_attrs(attributes.Attr.rotateOrder, keyable=False, channelBox=True)

		# ik handle name
		ikHandle = naming.Namer(type=naming.Type.ikHandle,
								side=self._side,
								description=self._des+self._ikType.title(),
								index=self._index).name

		# connect root with jnt translate
		constraints.matrix_connect(Ctrls[0].worldMatrixAttr, self._jnts[0],
								   skip=attributes.Attr.rotate+attributes.Attr.scale)

		# transform
		for Ctrl in Ctrls[1:]:
			Namer = naming.Namer(Ctrl.name)
			Namer.type = naming.Type.null
			trans = transforms.create(Namer.name, pos=Ctrl.name, 
									  parent=self._nodesHideGrp,
									  lockHide=attributes.Attr.all,
									  vis=True)
			constraints.matrix_connect(Ctrl.worldMatrixAttr, trans)
			self._nodesHide.append(trans)

		# set up ik handle
		ikSolver = 'ikRPsolver'
		# if self._ikType != 'spring':
		# 	ikSolver = 'ikRPsolver'
		# else:
		# 	ikSolver = 'ikSpringSolver'
		# 	mel.eval('ikSpringSolver')

		cmds.ikHandle(sj=self._jnts[0], ee=self._jnts[-1],
					  sol=ikSolver, name=ikHandle)

		cmds.parent(ikHandle, self._nodesHide[1])
		self._iks.append(ikHandle)

		# connect twist attr
		cmds.addAttr(self._ctrls[-1], ln='twist', at='float', dv=0, keyable=True)
		cmds.connectAttr(self._ctrls[-1]+'.twist', ikHandle+'.twist')

		# pole vector position
		pvVec = cmds.getAttr(ikHandle+'.poleVector')[0]
		pvVecUnit = mathUtils.get_unit_vector(pvVec)
		posRoot = cmds.xform(self._jnts[1], q=True, t=True, ws=True)
		posDisStart = cmds.xform(self._jnts[0], q=True, t=True, ws=True)
		posDisEnd = cmds.xform(self._jnts[-1], q=True, t=True, ws=True)
		dis = mathUtils.distance(posDisStart, posDisEnd)
		posPv = mathUtils.get_point_from_vector(posRoot, pvVecUnit, 
												distance=self._distance*dis)

		cmds.xform(Ctrls[1].zero, t=posPv, ws=True)

		# pv constraint
		constraints.matrix_pole_vector_constraint(self._nodesHide[0]+'.matrix', 
							ikHandle, self._jnts[0], 
							parentInverseMatrix=self._nodesHide[1]+'.inverseMatrix')

		# pv line
		guideLine = naming.Namer(type=naming.Type.guideLine, side=self._side,
								 description=self._des+'Pv', index=self._index).name
		guideLine = curves.create_guide_line(guideLine, [[self._jnts[0]+'.tx',
														  self._jnts[0]+'.ty',
														  self._jnts[0]+'.tz'],
														 [self._nodesHide[0]+'.tx',
														  self._nodesHide[0]+'.ty',
														  self._nodesHide[0]+'.tz']],
											 parent=self._nodesShowGrp)

		self._nodesShow.append(guideLine)

		# angle bias
		# if self._ikType == 'spring':
		# 	Ctrls[-1].add_attrs('angleBias', range=[0,1], defaultValue=0.5)
		# 	cmds.connectAttr(self._ctrls[-1]+'.angleBias',
		# 					 ikHandle+'.springAngleBias[0].springAngleBias_FloatValue')
		# 	expr = '~{}.angleBias'.format(self._ctrls[-1])
		# 	attr = ikHandle+'.springAngleBias[1].springAngleBias_FloatValue'
		# 	nodeUtils.equation(expr, side=self._side, description=self._des+'AngleBias', 
		# 					   index=self._index, attrs=attr)

# Notes:
'''
  for some reason, in maya2018, ikSpring solver's bias angle dosen't give realtime feedback,
  it has to be back to default pose to change the behavior, 
  so comment out the spring option until the problem fixed
'''