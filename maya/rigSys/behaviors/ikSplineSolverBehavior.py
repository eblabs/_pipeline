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
import common.nodes as nodes
import rigging.joints as joints
import rigging.controls.controls as controls
import rigging.constraints as constraints
import rigging.deformers as deformers
import modeling.curves as curves
# ---- import end ----

# ---- import components ----
import baseBehavior
# ---- import end ----

class IkSplineSolverBehavior(baseBehavior.BaseBehavior):
	"""IkSplineSolverBehavior template"""
	def __init__(self, **kwargs):
		super(IkSplineSolverBehavior, self).__init__(**kwargs)
		self._ikHandles = []
		self._ikTweakControls = []
		self._ikControls = []
		self._fkRotControls = []
		self._blueprintCurve = kwargs.get('blueprintCurve', '')
		self._jointSuffix = kwargs.get('jointSuffix', 'IkSpline')
		self._blueprintControls = kwargs.get('blueprintControls', [])
		self._topFk = kwargs.get('topFk', '')
		self._botFk = kwargs.get('bottomFk', '')
		# the blueprint controls should be 3, top, mid, bot
	def create(self):
		super(IkSplineSolverBehavior, self).create()

		# generate curve
		self._curve = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
		if not self._blueprintCurve or not cmds.objExists(self._blueprintCurve):
			self._blueprintCurve = naming.Naming(type = 'blueprintCurve', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
			curves.createCurveOnNodes(self._blueprintcurve, self._joints, degree = 3, parent = None)
			logger.WARN('Blueprint curve is not given, create curve base on joints')

		cmds.duplicate(self._blueprintCurve, name = self._curve)

		clsHndList = curves.clusterCurve(self._curve, relatives = False)
		
		# rebuild curve
		cvNum = curves.getCurveCvNum(self._curve)
		cmds.rebuildCurve(self._curve, ch = 1, rebuildType = 0, degree = 3, s = cvNum - 1, keepRange = 0, rpo = True)
		
		# set up ik and match joints to the curve
		ikHandle = naming.Naming(type = 'ikHandle', side = self._side, part = self._part + self._jointSuffix, index = self._index).name
		cmds.ikHandle(sj = self._joints[0], ee = self._joints[-1], sol = 'ikSplineSolver', ccv = False, scv = False, curve = self._curve, name = ikHandle)
		cmds.makeIdentity(self._joints[0], apply = True, t = 1, r = 1, s = 1)

		# parent nodes
		cmds.parent(self._curve, clsHndList, self._nodesHideGrp)
		cmds.parent(ikHandle, self._nodesLocalGrp)

		# controls
		for i, clsHnd in enumerate(clsHndList):
			NamingCtrl = naming.Naming(clsHnd)
			Control = controls.create(self._part + self._jointSuffix + 'Tweak', side = NamingCtrl.side, index = NamingCtrl.index, 
				stacks = self._stacks, parent = self._controlsGrp, lockHide = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
			cmds.delete(cmds.pointConstraint(clsHnd, Control.zero, mo = False))
			constraints.matrixConnect(Control.name, Control.matrixWorldAttr, clsHnd, offset = Control.output, skipRotate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])
			self._controls.append(Control.name)
			self._ikTweakControls.append(Control.name)

		# twist
		for i, ctrl in enumerate([self._controls[0], self._controls[-1]]):
			Control = controls.Control(ctrl)
			matrixLocal = transforms.getLocalMatrix([self._joints[0], self._joints[-1]][i], Control.output)
			multMatrix = nodes.create(type = 'multMatrix', side = self._side, 
									  part = '{}Twist{}'.format(self._part + self._jointSuffix, ['Bot', 'Top'][i]), 
									  index = self._index)
			cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal, type = 'matrix')
			cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[1]'.format(multMatrix))
			cmds.connectAttr('{}.matrixSum'.format(multMatrix), '{}.{}'.format(ikHandle, ['dWorldUpMatrix', 'dWorldUpMatrixEnd'][i]))

		cmds.setAttr('{}.dTwistControlEnable'.format(ikHandle), 1)
		cmds.setAttr('{}.dWorldUpType'.format(ikHandle), 4)

		self._ikHandles.append(ikHandle)

		# check if need drive controls
		if self._blueprintControls:

			pointsList = transforms.getNodeListTransformInfo(self._blueprintControls, 
													translate = True, rotate = False, scale = False)
			
			pointStart = transforms.getNodeTransformInfo(self._controls[0])[0]
			pointEnd = transforms.getNodeTransformInfo(self._controls[-1])[0]

			pointsList = [pointStart] + pointsList + [pointEnd]

			self._curveDrive = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix + 'Drv', index = self._index).name
			curves.createCurveOnNodes(self._curveDrive, pointsList, degree = 3, parent = self._nodesHideGrp)

			self._curveControlDrive = naming.Naming(type = 'curve', side = self._side, part = self._part + self._jointSuffix + 'CtrlDrv', index = self._index).name
			cmds.duplicate(self._blueprintCurve, name = self._curveControlDrive)
			cmds.parent(self._curveControlDrive, self._nodesHideGrp)

			crvInfo = nodes.create(type = 'curveInfo', 
								   side = self._side, 
								   part = self._part + self._jointSuffix + 'CtrlDrv', 
								   index = self._index)
			curveControlDriveShape = cmds.listRelatives(self._curveControlDrive, s = True)[0]
			cmds.connectAttr('{}.worldSpace[0]'.format(curveControlDriveShape), '{}.inputCurve'.format(crvInfo))

			# ik drv ctrl
			for bpCtrl in self._blueprintControls:
				NamingCtrl = naming.Naming(bpCtrl)
				Control = controls.create(NamingCtrl.part + self._jointSuffix, side = NamingCtrl.side, index = NamingCtrl.index, 
					stacks = self._stacks, parent = self._controlsGrp, posParent = bpCtrl, lockHide = ['sx', 'sy', 'sz'])
				
				NamingNode = naming.Naming(type = 'null', side = Control.side, part = Control.part, index = Control.index)
				node = transforms.createTransformNode(NamingNode.name, parent = self._nodesLocalGrp, posParent = Control.output,
												  lockHide=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
				constraints.matrixConnect(Control.name, Control.matrixWorldAttr, node, force = True, quatToEuler = False)
			
				self._nodesLocal.append(node)
				self._ikControls.append(Control.name)

			# cluster curve
			clsHndList = curves.clusterCurve(self._curveDrive, relatives = False)
			cmds.parent(clsHndList[:2], self._nodesLocal[0])
			cmds.parent(clsHndList[-2:], self._nodesLocal[-1])
			cmds.parent(clsHndList[2], self._nodesLocal[1])

			# blend mid control
			ControlMid = controls.Control(self._ikControls[1])
			cmds.addAttr(ControlMid.name, ln = 'weight', at = 'float', min = 0, max = 1, dv = 0.5, keyable = True)
			rvsPlug = attributes.addRvsAttr(ControlMid.name, 'weight')
			
			inputMatrixList = []
			for i, ctrl in enumerate([self._ikControls[0], self._ikControls[-1]]):
				Control = controls.Control(ctrl)
				multMatrix = nodes.create(type = 'multMatrix', 
										  side = ControlMid.side,
										  part = '{}WtBlend{}'.format(ControlMid.part, ['Bot', 'Top'][i]), 
										  index = ControlMid.index)
				# feed in matrix
				matrixLocal = transforms.getLocalMatrix(ControlMid.name, ctrl)
				cmds.setAttr('{}.matrixIn[0]'.format(multMatrix), matrixLocal, type = 'matrix')
				cmds.connectAttr(Control.matrixWorldPlug, '{}.matrixIn[1]'.format(multMatrix))
				inputMatrixList.append('{}.matrixSum'.format(multMatrix))

			constraints.constraintBlend(inputMatrixList, ControlMid.passer, 
						weightList=['{}.weight'.format(ControlMid.name), rvsPlug], scale = False, parentInverseMatrix = '{}.parentInverseMatrix[0]'.format(ControlMid.passer))
			
			parentConstraint = naming.Naming(type = 'parentConstraint', side = ControlMid.side,
								part = '{}WtBlend'.format(ControlMid.part), index = ControlMid.index).name
			
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
			attributes.addAttrs(drvCtrl, 'tweakerVis', attributeType='long', minValue=0, maxValue=1, defaultValue=0, keyable=False, channelBox=True)

			# connect tweak controls
			ctrlList = [[self._ikTweakControls[0], self._ikControls[0]],
						[self._ikTweakControls[-1], self._ikControls[-1]]]
			for ctrls in ctrlList:
				Control = controls.Control(ctrls[1])
				ControlTweak = controls.Control(ctrls[0])
				constraints.matrixConnect(Control.name, Control.matrixWorldAttr, ControlTweak.passer, offset = Control.output, skipScale = ['x', 'y', 'z'])
				cmds.setAttr('{}.v'.format(ControlTweak.zero), 0, lock = True)

			# connect other tweak controls with curveinfo
			self._ikTweakControls = self._ikTweakControls[1: len(self._ikTweakControls) - 1]
			for i, tweak in enumerate(self._ikTweakControls):
				ControlTweak = controls.Control(tweak)
				for axis in 'XYZ':
					cmds.connectAttr('{}.controlPoints[{}].{}Value'.format(crvInfo, i+1, axis.lower()),
									'{}.translate{}'.format(ControlTweak.zero, axis))
				cmds.connectAttr('{}.tweakerVis'.format(drvCtrl), '{}.v'.format(ControlTweak.zero))

			self._ikControls.append(drvCtrl)
			self._controls = self._ikControls + self._ikTweakControls

			# fk rot control
			jointsFk = []
			for i, jnt in enumerate([self._joints[0], self._joints[-1]]):
				fkRot = [self._botFk, self._topFk][i]
				if fkRot:
					bpCtrl = [self._blueprintControls[0], self._blueprintControls[-1]]
					NamingNode = naming.Naming(bpCtrl)
					NamingNode.part += 'FkRot'
					jointRotFk = joints.createOnNode(jnt, jnt, NamingNode.name, parent = jnt)
					Control = controls.create(NamingNode.part, side = NamingNode.side, index = NamingNode.index, 
						stacks = self._stacks, parent = self._controlsGrp, posParent = jnt, lockHide = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz'])
					constraints.matrixConnect(Control.name, Control.matrixLocalAttr, jointRotFk, skipTranslate = ['x', 'y', 'z'], skipScale = ['x', 'y', 'z'])
					if i == 0:
						matrixNode = jnt
						matrixAttr = 'matrix'
					else:
						NamingNode.part += 'CtrlDrv'
						NamingNode.type = 'multMatrix'
						multMatrix = nodes.create(NamingNode.name)
						numJnts = len(self._joints)
						for j in range(numJnts)：
							cmds.connectAttr('{}.matrix'.format(self._joints[numJnts - 1 - j]), '{}.matrixIn[{}]'.format(multMatrix, j))
						matrixNode = multMatrix
						matrixAttr = 'matrixSum'
					constraints.matrixConnect(matrixNode, matrixAttr, Control.zero, skipScale = ['x', 'y', 'z'])
					
					if not cmds.attributeQuery('fkRotControlVis', node = drvCtrl, ex = True):
						attributes.addAttrs(drvCtrl, 'fkRotControlVis', attributeType='long', 
							minValue=0, maxValue=1, defaultValue=0, keyable=False, channelBox=True)
					cmds.connectAttr('{}.fkRotControlVis'.format(drvCtrl), '{}.v'.format(Control.zero))

					# pass info
					self._controls.append(Control.name)
					self._fkRotControls.append(Control.name)
					jointsFk.append(jnt)

			if self._botFk:
				self._joints[0] = jointsFk[0]
			if self._topFk:
				self._joints[-1] = jointsFk[-1]

				

