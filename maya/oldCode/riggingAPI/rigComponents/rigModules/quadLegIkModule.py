#################################################
# quad leg ik module
# this module should do the base quadruped leg ik rig
#################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import riggingAPI.constraints as constraints

import riggingAPI.rigComponents.baseLimbs.baseIkSpringSolverLimb as baseIkSpringSolverLimb
import riggingAPI.rigComponents.rigUtils.createDriveJoints as createDriveJoints
## kwarg class
class kwargsGenerator(baseIkSpringSolverLimb.kwargsGenerator):
	"""docstring for kwargsGenerator"""
	def __init__(self):
		super(kwargsGenerator, self).__init__()
		self.dKwargs = {'lBpJntsFootRvs': None}
		self.addKwargs()

class quadLegIkModule(baseIkSpringSolverLimb.baseIkSpringSolverLimb):
	"""docstring for quadLegIkModule"""
	def __init__(self, *args, **kwargs):
		super(quadLegIkModule, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJntsFootRvs = kwargs.get('lBpJntsFootRvs', None)

			## lBpJntsFootRvs Structure
			# ball twist
			# -- heel roll
			# ---- toe roll
			# ------ side out
			# -------- side inn
			# ---------- ball end
		
	def createComponent(self):
		lBpJnts = self._lBpJnts
		self._lBpJnts = lBpJnts[:-1]
		sBpJntBall = lBpJnts[-2]
		sBpJntBallEnd = lBpJnts[-1]

		super(quadLegIkModule, self).createComponent()

		## ik driver
		lJntsDrv, lBindJnts = createDriveJoints.createDriveJoints(self._lBpJnts, sParent = self._sGrp_ikJnts, sSuffix = 'IkSpringDriverLocal', bBind = False)
		for sAxis in ['X', 'Y', 'Z']:
			cmds.connectAttr('%s.translate%s' %(self._lJntsLocal[0], sAxis), '%s.translate%s' %(lJntsDrv[0], sAxis))
		#### ik rp solver
		sIkHnd_rp = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sUpperRPsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJntsDrv[0], ee = lJntsDrv[2], sol = 'ikRPsolver', name = sIkHnd_rp)
		#### ik sc solver
		sIkHnd_sc = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sLowerSCsolver' %self._sName, iIndex = self._iIndex).sName
		cmds.ikHandle(sj = lJntsDrv[2], ee = lJntsDrv[-1], sol = 'ikSCsolver', name = sIkHnd_sc)

		for i, sJntDrv in enumerate(lJntsDrv):
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntDrv, sAxis), '%s.translate%s' %(self._lJnts[i], sAxis), f = True)
				cmds.connectAttr('%s.rotate%s' %(sJntDrv, sAxis), '%s.rotate%s' %(self._lJnts[i], sAxis), f = True)
				cmds.connectAttr('%s.scale%s' %(sJntDrv, sAxis), '%s.scale%s' %(self._lJnts[i], sAxis), f = True)

		#### rig ik handle
		cmds.parent(sIkHnd_sc, self._sGrpIk)

		oCtrl_leg = controls.oControl(self._lCtrls[2])
		iRotateOrder = cmds.getAttr('%s.ro' %self._lBpJnts[-1])
		oCtrl_bend = controls.create('%sBend' %oCtrl_leg.sPart, sSide = oCtrl_leg.sSide, iIndex = oCtrl_leg.iIndex, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = self._lBpJnts[-1], iRotateOrder = iRotateOrder, sShape = 'cube', fSize = 4, lLockHideAttrs = ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'])

		sMultMatrix_ctrl = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oCtrl_leg.sSide, sPart = '%sBendPos' %oCtrl_leg.sPart, iIndex = oCtrl_leg.iIndex).sName)
		cmds.connectAttr('%s.worldMatrix[0]' %self._lJntsLocal[-1], '%s.matrixIn[0]' %sMultMatrix_ctrl)
		lMatrix_zero = cmds.getAttr('%s.inverseMatrix' %oCtrl_bend.sZero)
		cmds.setAttr('%s.matrixIn[1]' %sMultMatrix_ctrl, lMatrix_zero, type = 'matrix')
		constraints.matrixConnect(sMultMatrix_ctrl, [oCtrl_bend.sPasser], 'matrixSum', lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		sGrpIk_bend = transforms.createTransformNode(naming.oName(sType = 'group', sSide = self._sSide, sPart = '%sSpringSolverBend' %self._sName, iIndex = self._iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = self._sComponentRigNodesWorld, sPos = oCtrl_bend.sName)
		constraints.matrixConnect(oCtrl_bend.sName, [sGrpIk_bend], 'matrixOutputWorld', lSkipScale = ['X', 'Y', 'Z'], bForce = True)
		cmds.parent(sIkHnd_rp, sGrpIk_bend)

		cmds.addAttr(oCtrl_bend.sName, ln = 'twist', at = 'float', keyable = True)
		cmds.connectAttr('%s.twist' %oCtrl_bend.sName, '%s.twist' %sIkHnd_rp)

		cmds.poleVectorConstraint(self._sGrpPv, sIkHnd_rp)

		self._lCtrls.append(oCtrl_bend.sName)
		self._lJntsLocal = lJntsDrv		

		## create foot ik rig
		## jnt
		lJntsFoot = []
		lJntsFootLocal = []
		sJntParent = self._lJnts[-1]
		sJntParentLocal = lJntsDrv[-1]
		oJntName = naming.oName(sBpJntBallEnd)
		oJntName.sType = 'jnt'
		oJntName.sPart = '%sIkSC' %oJntName.sPart
		sJnt = joints.createJntOnExistingNode(sBpJntBallEnd, sBpJntBallEnd, oJntName.sName, sParent = sJntParent)
		lJntsFoot.append(sJnt)

		sJntLocal = joints.createJntOnExistingNode(sJnt, 'IkSC', 'IkSCLocal', sParent = sJntParentLocal)
		lJntsFootLocal.append(sJntLocal)

		for sAxis in ['X', 'Y', 'Z']:
			cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(sJnt, sAxis))
			cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(sJnt, sAxis))
			cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(sJnt, sAxis))

		
		## ik handle
		sIkHndToe = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sToeSCsolver' %self._sName, iIndex = self._iIndex).sName
		
		cmds.ikHandle(sj = lJntsDrv[-1], ee = lJntsFootLocal[0], sol = 'ikSCsolver', name = sIkHndToe)
		cmds.parent(sIkHndToe, self._sGrpIk)

		self._lJnts += lJntsFoot
		self._lJntsLocal += lJntsFootLocal

		## reverse foot setup
		lJntsFootRvs = []
		for sBpJnt in self._lBpJntsFootRvs:
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'

			if sBpJnt != self._lBpJntsFootRvs[0]:
				sJntParent = cmds.listRelatives(sBpJnt, p = True)[0]
				oJntParentName = naming.oName(sJntParent)
				oJntParentName.sType = 'jnt'
				sJntParentRvs = oJntParentName.sName
			else:
				sJntParentRvs = self._sGrpIk

			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sJntParentRvs)
			lJntsFootRvs.append(sJnt)

		cmds.parent(self._sIkHnd,sIkHndToe, sIkHnd_sc,lJntsFootRvs[-1])

		## reverse foot connections
		###### add attrs
		attributes.addDivider([self._lCtrls[2]], 'footCtrl')
		for sAttr in ['toeRoll', 'heelRoll',  'footBank', 'toeSlide', 'heelSlide', 'footSlide']:
			cmds.addAttr(self._lCtrls[2], ln = sAttr, at = 'float', keyable = True)

		#### foot bank
		sMult_footBank = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = '%sFootBankRvs' %self._sName).sName)
		cmds.connectAttr('%s.footBank' %self._lCtrls[2], '%s.input1' %sMult_footBank)
		cmds.setAttr('%s.input2' %sMult_footBank, -1, lock = True)
		cmds.connectAttr('%s.footBank' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[3])
		cmds.connectAttr('%s.output' %sMult_footBank, '%s.rz' %lJntsFootRvs[4])
		cmds.transformLimits(lJntsFootRvs[3], rz = [0,360], erz = [1,0])
		cmds.transformLimits(lJntsFootRvs[4], rz = [0,360], erz = [1,0])

		#### toe roll
		cmds.connectAttr('%s.toeRoll' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[2])

		#### toeSlide
		cmds.connectAttr('%s.toeSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[2])

		#### heel Roll
		cmds.connectAttr('%s.heelRoll' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[1])

		#### heelSlide
		cmds.connectAttr('%s.heelSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[1])

		#### footSlide
		cmds.connectAttr('%s.footSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[0])

		#### bind joints
		if self._bBind:
			oJntName = naming.oName(sBpJntBall)
			oJntName.sType = 'bindJoint'
			sBindJnt = joints.createJntOnExistingNode(sBpJntBall, sBpJntBall, oJntName.sName, sParent = self._lBpJnts[-1])
			self._lBindJnts.append(sBindJnt)
			createDriveJoints.tagBindJoint(sBindJnt, lJntsFoot[0])
			createDriveJoints.labelBindJoint(sBindJnt)

		## write component info
		self._writeGeneralComponentInfo('quadLegIkModule', self._lJnts, self._lCtrls, self._lBindJnts, self._lBindRootJnts)

		## writeOutputMatrixInfo

		if self._bInfo:
			sMultMatrixLocalParent = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = len(self._lJnts) - 2).sName

			cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixLocal%03d' %(len(self._lJnts) - 1), at = 'matrix')
			cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixWorld%03d' %(len(self._lJnts) - 1), at = 'matrix')

			sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = len(self._lJnts) - 1).sName)
			cmds.connectAttr('%s.matrix' %lJntsFoot[0], '%s.matrixIn[0]' %sMultMatrixLocal)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixLocalParent, '%s.matrixIn[1]' %sMultMatrixLocal)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, len(self._lJnts) - 1))
			sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = len(self._lJnts) - 1).sName)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixIn[0]' %sMultMatrixWorld)
			cmds.connectAttr(self._sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
			cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, len(self._lJnts) - 1))

		self._getComponentInfo(self._sComponentMaster)

		