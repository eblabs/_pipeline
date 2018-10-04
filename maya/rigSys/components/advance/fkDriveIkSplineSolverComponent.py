# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import common.naming.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import common.hierarchy as hierarchy
import common.nodes as nodes
import rigging.controls.controls as controls
import rigging.constraints as constraints
import rigging.joints as joints
reload(joints)
reload(transforms)
# ---- import end ----

# -- import component
import components.base.ikSplineSolverComponent as ikSplineSolverComponent
# -- import end ----

class FkDriveIkSplineSolverComponent(ikSplineSolverComponent.IkSplineSolverComponent):
	"""
	FkDriveIkSplineSolverComponent

	create fk drive ik spline solver component
	mainly used for spine rig

	"""
	def __init__(self, *args,**kwargs):
		super(FkDriveIkSplineSolverComponent, self).__init__(*args,**kwargs)
		self._rigComponentType = 'rigSys.components.advance.fkDriveIkSplineSolverComponent'
		self._fkControls = []
		self._fkReverseControls = []

	def _registerDefaultKwargs(self):
		super(FkDriveIkSplineSolverComponent, self)._registerDefaultKwargs()
		kwargs = {'fkControlsNumber': {'value': 3, 'type': list},
				  'reverseFk': {'value': False, 'type': bool}}
		self._kwargs.update(kwargs)

	def _createComponent(self):
		super(FkDriveIkSplineSolverComponent, self)._createComponent()

		bpFkCtrls = joints.createJointsAlongCurve(self._curve, self._fkControlsNumber, 
				suffix = 'FkDrv', startNode = self._blueprintControls[0], endNode = self._blueprintControls[-1])

		# orient bpFkCtrls
		# get aim vectors
		tx = cmds.getAttr('{}.tx'.format(self._joints[1]))
		if tx > 0:
			aimVec = [1, 0, 0]
		else:
			aimVec = [-1, 0, 0]
		for i, bpCtrl in enumerate(bpFkCtrls[:-1]):
			upJnt = transforms.getClosestNode(self._joints, bpCtrl)
			cmds.delete(cmds.aimConstraint(bpFkCtrls[i+1], bpCtrl, aimVector = aimVec, upVector = [0,1,0], 
							worldUpObject = upJnt, worldUpType = 'objectrotation', mo = False))
		cmds.delete(cmds.orientConstraint(bpFkCtrls[-2], bpFkCtrls[-1], mo = False))

		ikVisCtrl = self._ikControls[-1]

		blueprintControls = [bpFkCtrls]

		if self._reverseFk:
			blueprintControlsRvs = bpFkCtrls[:]
			blueprintControlsRvs.reverse()
			blueprintControls.append(blueprintControlsRvs)

		for i, bpCtrlList in enumerate(blueprintControls):
			fkControllist = [self._fkControls, self._fkReverseControls][i]

			visAttr = ['fkControlsVis', 'fkReverseVis'][i]
			attributes.addAttrs(ikVisCtrl, visAttr, attributeType='long', 
				minValue=0, maxValue=1, defaultValue=0, keyable=False, channelBox=True)

			ctrlParent = self._controlsGrp
			partSuffix = ['', 'Rvs'][i]
			ControlIk = controls.Control([self._ikControls[-2], self._ikControls[0]][i])
			for j, bpCtrl in enumerate(bpCtrlList):
				NamingNode = naming.Naming(bpCtrl)
				ControlFk = controls.create(NamingNode.part + partSuffix,
											NamingNode.side, j + 1,
											stacks = self._stacks, 
											parent = ctrlParent, 
											posParent = bpCtrl,
											lockHide=['sx', 'sy', 'sz'])
				cmds.connectAttr('{}.{}'.format(ikVisCtrl, visAttr), '{}.v'.format(ControlFk.zero))
				ctrlParent = ControlFk.output
				fkControllist.append(ControlFk.name)
			
			controls.addCtrlShape(fkControllist, asCtrl = ikVisCtrl)

			multMatrix = nodes.create(type = 'multMatrix', side = ControlIk.side,
									  part = '{}FkDriver'.format(ControlIk.part),
									  index = ControlIk.index)
			cmds.connectAttr('{}.worldMatrix[0]'.format(ctrlParent), 
							 '{}.matrixIn[0]'.format(multMatrix))
			cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self._controlsGrp), 
							 '{}.matrixIn[1]'.format(multMatrix))

			constraints.matrixConnect(multMatrix, 'matrixSum', ControlIk.zero, offset = ctrlParent, 
								skipScale = ['x', 'y', 'z'], force = True, quatToEuler = False)

		cmds.delete(blueprintControls[0])

		# pass info
		self._controls += (self._fkControls + self._fkReverseControls)

	def _writeRigComponentInfo(self):
		super(FkDriveIkSplineSolverComponent, self)._writeRigComponentInfo()

		# fk controls
		self._addListAsStringAttr('fkControls', self._fkControls)

		# fk reverse controls
		self._addListAsStringAttr('fkReverseControls', self._fkReverseControls)

	def _getRigComponentInfo(self):
		super(FkDriveIkSplineSolverComponent, self)._getRigComponentInfo()

		# get fk controls
		self._fkControls = self._getStringAttrAsList('fkControls')

		# get fk controls
		self._fkReverseControls = self._getStringAttrAsList('fkReverseControls')

