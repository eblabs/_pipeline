# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)


# -- import maya lib
import maya.cmds as cmds
import maya.mel as mel
# -- import lib
import common.naming.naming as naming
import common.naming.namingDict as namingDict
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import rigging.joints as joints
import baseBehavior

class IkSplineSolverBehavior(baseBehavior.BaseBehavior):
	"""IkSplineSolverBehavior template"""
	_ikTweakControls = []
	_ikControls = []
	def __init__(self, **kwargs):
		super(IkSplineSolverBehavior, self).__init__(**kwargs)
		self._blueprintCurve = kwargs.get('blueprintCurve', '')
		self._jointSuffix = kwargs.get('jointSuffix', 'IkSpline')
		self._blueprintControls = kwargs.get('blueprintControls': [])
		# the blueprint controls should be 3, top, mid, bot
	def create(self):
		super(IkSplineSolverBehavior, self).create()

		# generate curve
		self._curve = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
		if not self._blueprintCurve or not cmds.objExists(self._blueprintCurve):
			self._blueprintCurve = naming.Naming(type = 'blueprintCurve', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
			curves.createCurveOnNodes(self._blueprintcurve, self._joints, degree = 3, parent = None)
			logger.WARN('Blueprint curve is not given, create curve base on joints')

		cmds.duplicate(self._blueprintJoints, name = self._curve)[0]

		clsHndList = curves.clusterCurve(self._curve, bRelatives = True)
		
		# rebuild curve
		cvNum = curves.getCurveCvNum(self._curve)
		cmds.rebuildCurve(self._curve, ch = 1, rebuildType = 0, degree = 3, s = cvNum - 1, keepRange = 0, rpo = True)
		
		# set up ik and match joints to the curve
		self._ikHandle = naming.Naming(type = 'ikHandle', side = self._side, sPart = self._part + self._jointSuffix, iIndex = self._index).name
		cmds.ikHandle(sj = self._joints[0], ee = self._joints[-1], sol = 'ikSplineSolver', ccv = False, scv = False, curve = self._curve, name = self._ikHandle)
		cmds.makeIdentity(self._joints[0], apply = True, t = 1, r = 1, s = 1)

		# parent nodes
		cmds.parent(self._curve, clsHndList, self._nodesHideGrp)
		cmds.parent(self._ikHandle, self._nodesLocalGrp)

		# controls
		for i, clsHnd in enumerate(clsHndList):
			Control = controls.create(self._part + self._jointSuffix + 'Tweak', side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, lockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
			cmds.delete(cmds.pointConstraint(clsHnd, Control.zero, mo = False))
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, clsHnd, offset = True, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])
			self._controls.append(Control.name)
			self._ikTweakControls.append(Control.name)

		# twist
		cmds.setAttr('{}.dTwistControlEnable'.format(self._ikHandle), 1)
		cmds.setAttr('{}.dWorldUpType'.format(self._ikHandle), 4)

		for i, ctrl in enumerate([self._controls[0], self._controls[-1]]):
			Control = controls.Control(ctrl)
			matrixLocal = transforms.getLocalMatrix([self._joints[0], self._joints[-1]][i], Control.output)
			multMatrix = cmds.createNode('multMatrix', name = naming.Naming(type = 'multMatrix', side = self._side, 
										 part = '{}Twist{}'.format(self._part + self._jointSuffix, ['Bot', 'Top'][i]), index = self._index).name)
			cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal)
			cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[1]'.format(multMatrix))
			cmds.connectAttr('{}.matrixSum',format(multMatrix), '{}.{}'.format(self._ikHandle, ['dWorldUpMatrix', 'dWorldUpMatrixEnd'][i]))

		# check if need drive controls
		if self._blueprintControls:

			pointsList = transforms.getNodeListTransformInfo(self._blueprintControls, 
													translate = True, rotate = False, scale = False)
			
			pointStart = transforms.getNodeTransformInfo(self._controls[0])[0]
			pointEnd = transforms.getNodeTransformInfo(self._controls[-1])[0]

			pointsList = [pointStart] + pointsList + [pointEnd]

			disStart = apiUtils.distance(pointStart, pointsList[0])
			disEnd = apiUtils.distance(pointEnd, pointsList[-1])

			self._curveDrive = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix + 'Drv', index = self._index).name
			curves.createCurveOnNodes(self._curveDrive, pointsList, degree = 3, parent = self._nodesHideGrp)

			self._curveControlDrive = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix + 'CtrlDrv', index = self._index).name
			cmds.duplicate(self._blueprintCurve, name = self._curveControlDrive)
			cmds.parent(self._curveControlDrive, self._nodesHideGrp)

			crvInfo = naming.Naming(type = 'curveInfo', side = self._side, part = self._part + self._jointSuffix + 'CtrlDrv', index = self._index).name
			cmds.createNode('curveInfo', name = crvInfo)
			curveControlDriveShape = cmds.listRelatives(self._curveControlDrive, s = True)[0]
			cmds.connectAttr('{}.worldSpace[0]'.format(curveControlDriveShape), '{}.inputCurve'.format(crvInfo))

			# ik drv ctrl
			for bpCtrl in self._blueprintControls:
				Control = controls.create(self._part + self._jointSuffix, side = NamingCtrl.side, index = NamingCtrl.index, 
					stacks = self._stacks, parent = self._controlsGrp, posParent = bpCtrl, lockHideAttrs = ['sx', 'sy', 'sz'])
				
				NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index).name
				node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = Control.output,
												  lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
				constraints.matrixConnect(Control.name, matrixWorldAttr, node, force = True, quatToEuler = False)
			
				self._nodesLocal.append(node)
				self._ikControls.append(Control.name)

			# cluster curve
			clsHndList = curves.clusterCurve(self._curveDrive, bRelatives = True)
			cmds.parent(clsHndList[:2], self._nodesLocal[0])
			cmds.parent(clsHndList[-2:], self._nodesLocal[-1])
			cmds.parent(clsHndList[2], self._nodesLocal[1])

			# blend mid control
			ControlMid = controls.Control(self._ikControls[1])
			parentConstraint = naming.Naming(type = 'parentConstraint', side = ControlMid.side,
								part = '{}WtBlend'.format(ControlMid.part), index = ControlMid.index).name
			cmds.createNode('parentConstraint', name = parentConstraint)
			cmds.parent(parentConstraint, ControlMid.passer)
			for i, ctrl in enumerate([self._ikControls[0], self._ikControls[-1]]):
				Control = controls.Control(ctrl)
				
				NamingMatrix = naming.Naming(type = 'multMatrix', side = ControlMid.side,
							part = '{}WtBlend{}'.format(ControlMid.part, ['Top', 'Bot'][i]), 
							index = ControlMid.index)
				multMatrix = cmds.createNode('multMatrix', name = NamingMatrix.name)
				NamingMatrix.type = 'decomposeMatrix'
				decompose = cmds.createNode('decomposeMatrix', name = NamingMatrix.name)

				# feed in matrix
				matrixLocal = transforms.getLocalMatrix(ControlMid.name, ctrl)
				cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal)
				cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[1]'.format(multMatrix))
				# connect decomposeMatrix
				cmds.connectAttr('{}.matrixSum'.format(multMatrix), '{}.inputMatrix'.format(decompose))

				# feed in constraint
				for attr in ['Translate', 'Rotate']:
					for axis in 'XYZ':
						cmds.connectAttr('{}.output{}{}'.format(decompose, attr, axis), 
										 '{}.target[{}].target{}{}'.format(parentConstraint, i, attr, axis))

			# feed in mid control
			for attr in ['Translate', 'Rotate']:
				for axis in 'XYZ':
					cmds.connectAttr('{}.constraint{}{}'.format(parentConstraint, attr, axis),
									'{}.{}{}'.format(ControlMid.passer, attr, axis))
			cmds.connectAttr('{}.parentInverseMatrix[0]'.format(ControlMid.passer),
							'{}.constraintParentInverseMatrix'.format(parentConstraint))
			cmds.setAttr('{}.interpType'.format(parentConstraint), 2)

			# add weight attr
			cmds.addAttr(ControlMid.name, ln = 'weight', at = 'float', min = 0, max = 1, dv = 0.5, keyable = True)
			cmds.connectAttr('{}.weight'.format(ControlMid.name), '{}.target[0].targetWeight'.format(parentConstraint))
			rvs = naming.Naming(type = 'reverse', side = ControlMid.side,
								part = '{}WtBlend'.format(ControlMid.part), index = ControlMid.index).name
			cmds.createNode('reverse', name = rvs)
			cmds.connectAttr('{}.weight'.format(ControlMid.name), '{}.inputX'.format(rvs))
			cmds.connectAttr('{}.outputX'.format(rvs), '{}.target[1].targetWeight'.format(parentConstraint))

			# wire drive curve
			wire = naming.Naming(type = 'wire', side = self._side, 
				part = self._part + self._jointSuffix + 'CtrlDrv', index = self._index).name
			wireNodes = deformers.createWireDeformer(self._curveControlDrive, 
													 self._curveDrive, 
													 wire, dropoffDistance = 200)

			# add ik drv control
			drvCtrl = naming.Naming(type = 'control', side = self._side, 
									part = self._part + self._jointSuffix, index = self._index).name
		
			controls.addCtrlShape(self._ikControls, asCtrl = drvCtrl)
			attributes.addAttrsaddAttrs(drvCtrl, 'tweakerVis', attributeType='long', minValue=0, maxValue=1, defaultValue=0, keyable=False, channelBox=True)

			# connect tweak controls
			ctrlList = [[[self._ikTweakControls[:2]], self._ikControls[0]],
						[[self._ikTweakControls[-2:]], self._ikControls[-1]]]
			for ctrls in ctrlList:
				Control = controls.Control(ctrls[1])
				for tweak in ctrls[0]:
					ControlTweak = controls.Control(tweak)
					cmds.parent(ControlTweak.zero, Control.output)
					cmds.setAttr('{}.v'.format(ControlTweak.zero), 0, lock = True)

			# connect other tweak controls with curveinfo
			self._ikTweakControls = self._ikTweakControls[2: len(self._ikTweakControls) - 2]
			for i, tweak in enumerate(self._ikTweakControls):
				ControlTweak = controls.Control(tweak)
				for axis in 'XYZ':
					cmds.connectAttr('{}.controlPoints[{}].{}Value'.format(crvInfo, i+2, axis.lower()),
									'{}.translate{}'.format(ControlTweak.zero, axis))
				cmds.connectAttr('{}.tweakerVis'.format(drvCtrl), '{}.v'.format(ControlTweak.zero))

			self._ikControls.append(drvCtrl)
			self._controls = self._ikControls + self._ikTweakControls