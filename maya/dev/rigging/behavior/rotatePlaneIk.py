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
import utils.common.hierarchy as hierarchy
import utils.common.nodeUtils as nodeUtils
import utils.common.mathUtils as mathUtils
import utils.modeling.curves as curves
import utils.rigging.joints as joints
import utils.rigging.constraints as constraints
import utils.rigging.controls as controls

## import behavior
import behavior
import fkChain as fkChainBhv

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
			singleChainIk(int)[0]: if need to set some joints as single chain ik
						like ik leg
						it will define the number of joints going to be
						set to scIk, maxium is 2
			reverseJoints(list): blueprint of the reverse joints
								 structure: [heel, toe, sideInn, sideOut, ball]
			reverseDescription(list): each reverse joint position's description
	"""
	def __init__(self, **kwargs):
		super(RotatePlaneIk, self).__init__(**kwargs)
		self._ikType = variables.kwargs('ikType', 'rp', kwargs, shortName='ik')
		self._jointSuffix = variables.kwargs('jointSuffix', 'Ik'+self._ikType.title(),
											 kwargs, shortName='jntSfx')
		self._bpCtrl = variables.kwargs('blueprintControl', '', kwargs, shortName='bpCtrl')
		self._distance = variables.kwargs('poleVectorDistance', 1, kwargs, shortName='pvDis')
		self._sc = variables.kwargs('singleChainIk', 0, kwargs, 'sc')
		self._rvsJnts = variables.kwargs('reverseJoints', [], kwargs, 'rvsJnts')
		self._rvsDes = variables.kwargs('reverseDescription', ['heel', 'toe', 'sideInn', 
										'sideOut', 'ball'], kwargs, 'rvsDes')
		self._iks = []
		self._rvsCtrls = []

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

		# ik solvers
		if self._sc == 0:
			self._scJnts = []
			self._rpJnts = self._jnts
		elif self._sc == 1:
			self._scJnts = self._jnts[-2:]
			self._rpJnts = self._jnts[:-1]
		else:
			self._scJnts = self._jnts[-3:]
			self._rpJnts = self._jnts[:-2]

		# rp ik handle
		ikHandle = naming.Namer(type=naming.Type.ikHandle,
								side=self._side,
								description=self._des+self._ikType.title(),
								index=self._index).name

		cmds.ikHandle(sj=self._rpJnts[0], ee=self._rpJnts[-1],
					  sol=ikSolver, name=ikHandle)

		cmds.parent(ikHandle, self._nodesHide[1])
		self._iks = [ikHandle]

		# get pole vector position in world space
		pvVec = cmds.getAttr(self._iks[0]+'.poleVector')[0]
		pvVecUnit = mathUtils.get_unit_vector(pvVec)
		posRoot = cmds.xform(self._jnts[1], q=True, t=True, ws=True)
		posDisStart = cmds.xform(self._jnts[0], q=True, t=True, ws=True)
		posDisEnd = cmds.xform(self._jnts[-1], q=True, t=True, ws=True)
		dis = mathUtils.distance(posDisStart, posDisEnd)
		posPv = mathUtils.get_point_from_vector(posRoot, pvVecUnit, 
												distance=self._distance*dis)

		parentInverseMatrix = self._nodesHide[1]+'.inverseMatrix'
		
		# sc ik handle
		if self._sc:
			jntBase = self._rpJnts[-1]
			for jnt, sfx in zip(self._scJnts[1:], ['A', 'B']):
				ikHandle = naming.Namer(type=naming.Type.ikHandle,
										side=self._side,
										description='{}IkSc{}'.format(self._des, sfx),
										index=self._index).name
				cmds.ikHandle(sj=jntBase, ee=jnt, sol='ikSCsolver', name=ikHandle)						
				cmds.parent(ikHandle, self._nodesHide[1])
				jntBase = jnt

				self._iks.append(ikHandle)

			# reverse joints
			# [heel, toe, sideInn, sideOut, ball]
			if self._rvsJnts and self._sc > 1:

				# get descriptor for each pivot
				rvsJntsDes = [self._rvsDes[-1]+'Twist',
							  self._rvsDes[0]+'Roll',
							  self._rvsDes[1]+'Roll',
							  self._rvsDes[2],
							  self._rvsDes[-2],
							  self._rvsDes[1]+'Tap',
							  self._rvsDes[-1]+'Roll']

				rvsBpJnts = [self._rvsJnts[-1],
							 self._rvsJnts[0],
							 self._rvsJnts[1],
							 self._rvsJnts[2],
							 self._rvsJnts[-2],
							 self._rvsJnts[-1],
							 self._rvsJnts[-1]]

				rvsJnts = []
				for des, jnt in zip(rvsJntsDes, rvsBpJnts):
					Namer = naming.Namer(jnt)
					Namer.type = naming.Type.joint
					Namer.description = des
					rvsJnt = joints.create(Namer.name, pos=[jnt,None], parent=self._nodesHide[1])
					rvsJnts.append(rvsJnt)

				# orient jnts
				# get tx to check if it's a mirrored joint chain
				txJnt = cmds.getAttr(self._jnts[-2]+'.tx')
				if txJnt >= 0:
					aimVector = [1,0,0]
				else:
					aimVector = [-1,0,0]

				aimList = [rvsJnts[2], rvsJnts[2], rvsJnts[1],
						   rvsJnts[4], rvsJnts[3], self._jnts[-1], self._jnts[-3]]

				for jnt, target in zip(rvsJnts, aimList):
					if jnt not in rvsJnts[3:5]:
						upVector = self._jnts[-2]
					else:
						upVector = rvsJnts[0]
					cmds.delete(cmds.aimConstraint(target, jnt, aimVector=aimVector,
												   upVector=[0,1,0], worldUpType='objectrotation',
												   worldUpObject=upVector, mo=False))
					cmds.makeIdentity(jnt, apply=True, t=1, r=1, s=1)

				# parent rvs joints
				rvsJntChain = [rvsJnts[0], rvsJnts[1], rvsJnts[2],
							   rvsJnts[4], rvsJnts[3], rvsJnts[-1]]
				hierarchy.parent_chain(rvsJntChain, reverse=True)
				cmds.parent(rvsJnts[-2], rvsJnts[3])
				# fk rig for the rvs chain
				kwargs = {'side': self._side,
						  'description': self._des,
						  'index': self._index,
						  'blueprintJoints': rvsJntChain,
						  'offsets': self._offsets,
						  'jointSuffix': '',
						  'createJoints': False,
						  'lockHide': attributes.Attr.translate+attributes.Attr.scale,
						  'controlShape': 'rotate',
						  'controlSize': self._ctrlSize,
						  'controlsGrp': Ctrls[-1].output}

				RvsRig = fkChainBhv.FkChain(**kwargs)
				RvsRig.create()

				self._rvsCtrls = RvsRig._ctrls

				ctrlGrp = controls.Control(self._rvsCtrls[-2]).output
				kwargs.update({'blueprintJoints': [rvsJnts[-2]],
							   'controlsGrp': ctrlGrp})

				RvsRig = fkChainBhv.FkChain(**kwargs)
				RvsRig.create()

				self._rvsCtrls.insert(-1, RvsRig._ctrls[0])

				# parent ik handles
				cmds.parent(self._iks[:-1], rvsJnts[-1])
				cmds.parent(self._iks[-1], rvsJnts[-2])

				self._ctrls += self._rvsCtrls

				# get pole vector constraint parent inverse matrix
				multMatrixAttr = nodeUtils.mult_matrix([rvsJnts[-1]+'.worldMatrix[0]', 
												   self._nodesHide[0]+'.worldInverseMatrix[0]'],
												   side=self._side,
												   description=self._des+'PvConstraint',
												   index=self._index)
				parentInverseMatrix = nodeUtils.inverse_matrix(multMatrixAttr,
															   side=self._side,
															   description=self._des+'PvConstraint',
															   index=self._index)

		# connect twist attr
		cmds.addAttr(Ctrls[-1].name, ln='twist', at='float', dv=0, keyable=True)
		cmds.connectAttr(Ctrls[-1].name+'.twist', self._iks[0]+'.twist')
		
		# place pv control
		cmds.xform(Ctrls[1].zero, t=posPv, ws=True)

		# pv constraint

		constraints.matrix_pole_vector_constraint(self._nodesHide[0]+'.matrix', 
							self._iks[0], self._jnts[0], 
							parentInverseMatrix=parentInverseMatrix)

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