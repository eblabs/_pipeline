#################################################
# leg ik module
# this module should do the base biped leg ik rig
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

import riggingAPI.rigComponents.baseComponent as baseComponent
import riggingAPI.rigComponents.baseLimbs.baseIkRPsolverLimb as baseIkRPsolverLimb
import riggingAPI.rigComponents.baseLimbs.baseIkSCsolverLimb as baseIkSCsolverLimb

class legIkModule(baseIkRPsolverLimb.baseIkRPsolverLimb):
	"""docstring for armIkModule"""
	def __init__(self, *args, **kwargs):
		super(legIkModule, self).__init__(*args, **kwargs)
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
			# ---------- ball roll
			# ------------- ball roll end
			# ---------- toe tap
			# ------------- toe tap end
		
	def createComponent(self):
		lBpJnts = self._lBpJnts
		self._lBpJnts = lBpJnts[:-2]
		sBpJntBall = lBpJnts[-2]
		sBpJntBallEnd = lBpJnts[-1]

		super(legIkModule, self).createComponent()

		## create foot ik rig
		## jnt
		lJntsFoot = []
		lJntsFootLocal = []
		sJntParent = self._lJnts[-1]
		sJntParentLocal = self._lJntsLocal[-1]
		for sBpJnt in [sBpJntBall, sBpJntBallEnd]:
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%sIkSC' %oJntName.sPart
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sJntParent)
			sJntParent = sJnt
			lJntsFoot.append(sJnt)

			sJntLocal = joints.createJntOnExistingNode(sJnt, 'IkSC', 'IkSCLocal', sParent = sJntParentLocal)
			sJntParentLocal = sJntLocal
			lJntsFootLocal.append(sJntLocal)

			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntLocal, sAxis), '%s.translate%s' %(sJnt, sAxis))
				cmds.connectAttr('%s.rotate%s' %(sJntLocal, sAxis), '%s.rotate%s' %(sJnt, sAxis))
				cmds.connectAttr('%s.scale%s' %(sJntLocal, sAxis), '%s.scale%s' %(sJnt, sAxis))

		
		## ik handle
		sIkHndBall = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sBallSCsolver' %self._sName, iIndex = self._iIndex).sName
		sIkHndToe = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sToeSCsolver' %self._sName, iIndex = self._iIndex).sName
		
		cmds.ikHandle(sj = self._lJntsLocal[-1], ee = lJntsFootLocal[0], sol = 'ikSCsolver', name = sIkHndBall)
		cmds.ikHandle(sj = lJntsFootLocal[0], ee = lJntsFootLocal[1], sol = 'ikSCsolver', name = sIkHndToe)
		cmds.parent(sIkHndBall, sIkHndToe, self._sGrpIk)

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

		cmds.parent(self._sIkHnd, lJntsFootRvs[6])
		cmds.parent(sIkHndBall, lJntsFootRvs[5])
		cmds.parent(sIkHndToe, lJntsFootRvs[-1])

		## reverse foot connections
		###### add attrs
		attributes.addDivider([self._lCtrls[2]], 'footCtrl')
		for sAttr in ['footRoll', 'toeTap', 'ballRoll', 'toeRoll', 'heelRoll',  'footBank', 'toeSlide', 'heelSlide', 'ballSlide', 'toeWiggle', 'toeTwist', 'footSlide']:
			cmds.addAttr(self._lCtrls[2], ln = sAttr, at = 'float', keyable = True)
		attributes.addDivider([self._lCtrls[2]], 'footExtraCtrl')
		for sAttr in ['toeLift', 'toeStraight']:
			cmds.addAttr(self._lCtrls[2], ln = sAttr, at = 'float', min = 0, max = 90, keyable = True)
		cmds.setAttr('%s.toeLift' %self._lCtrls[2], 30)
		cmds.setAttr('%s.toeStraight' %self._lCtrls[2], 45)

		#### ball Roll
		sClamp_footRoll = cmds.createNode('clamp', name = naming.oName(sType = 'clamp', sSide = self._sSide, sPart = '%sFootRoll' %self._sName).sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.inputR' %sClamp_footRoll)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.maxR' %sClamp_footRoll) 
		sPlus_ballRoll = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'add', sSide = self._sSide, sPart = '%sBallRoll' %self._sName).sName)
		cmds.connectAttr('%s.outputR' %sClamp_footRoll, '%s.input1' %sPlus_ballRoll)
		sRemap_ballRoll = cmds.createNode('remapValue', name = naming.oName(sType = 'remap', sSide = self._sSide, sPart = '%sBallRollStraight' %self._sName).sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.inputValue' %sRemap_ballRoll)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.inputMin' %sRemap_ballRoll)
		cmds.connectAttr('%s.toeStraight' %self._lCtrls[2], '%s.inputMax' %sRemap_ballRoll)
		cmds.connectAttr('%s.outValue' %sRemap_ballRoll, '%s.input2' %sPlus_ballRoll)
		sMult_ballRollLift = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = '%sBallRollLiftNeg' %self._sName).sName)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.input1' %sMult_ballRollLift)
		cmds.setAttr('%s.input2' %sMult_ballRollLift, -1, lock = True)
		cmds.connectAttr('%s.output' %sMult_ballRollLift, '%s.outputMax' %sRemap_ballRoll)
		sPlus_ballRollSum = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'add', sSide = self._sSide, sPart = '%sBallRollSum' %self._sName).sName)
		cmds.connectAttr('%s.output' %sPlus_ballRoll, '%s.input1' %sPlus_ballRollSum)
		cmds.connectAttr('%s.ballRoll' %self._lCtrls[2], '%s.input2' %sPlus_ballRollSum)
		cmds.connectAttr('%s.output' %sPlus_ballRollSum, '%s.rz' %lJntsFootRvs[5])

		#### toe roll
		sRemap_toeRoll = cmds.createNode('remapValue', name = naming.oName(sType = 'remapValue', sSide = self._sSide, sPart = '%sToeRoll' %self._sName).sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.inputValue' %sRemap_toeRoll)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.inputMin' %sRemap_toeRoll)
		cmds.connectAttr('%s.toeStraight' %self._lCtrls[2], '%s.inputMax' %sRemap_toeRoll)
		sMult_toeRoll = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = '%sToeRoll' %self._sName).sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.input1' %sMult_toeRoll)
		cmds.connectAttr('%s.outValue' %sRemap_toeRoll, '%s.input2' %sMult_toeRoll)
		sPlus_toeRollSum = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'add', sSide = self._sSide, sPart = '%sToeRollSum' %self._sName).sName)
		cmds.connectAttr('%s.output' %sMult_toeRoll, '%s.input1' %sPlus_toeRollSum)
		cmds.connectAttr('%s.toeRoll' %self._lCtrls[2], '%s.input2' %sPlus_toeRollSum)
		cmds.connectAttr('%s.output' %sPlus_toeRollSum, '%s.rz' %lJntsFootRvs[2])

		#### heel Roll
		sCond_heel = cmds.createNode('condition', name = naming.oName(sType = 'condition', sSide = self._sSide, sPart = '%sHeelRoll' %self._sName).sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.firstTerm' %sCond_heel)
		cmds.setAttr('%s.operation' %sCond_heel, 4)
		cmds.setAttr('%s.colorIfFalseR' %sCond_heel, 0)
		sMult_heelRoll = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'multDoubleLinear', sSide = self._sSide, sPart = '%sHeelRollRvs' %self._sName).sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.input1' %sMult_heelRoll)
		cmds.setAttr('%s.input2' %sMult_heelRoll, -1, lock = True)
		cmds.connectAttr('%s.output' %sMult_heelRoll, '%s.colorIfTrueR' %sCond_heel)
		sPlus_heelRollSum = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'addDoubleLinear', sSide = self._sSide, sPart = '%sHeelRollSum' %self._sName).sName)
		cmds.connectAttr('%s.outColorR' %sCond_heel, '%s.input1' %sPlus_heelRollSum)
		cmds.connectAttr('%s.heelRoll' %self._lCtrls[2], '%s.input2' %sPlus_heelRollSum)
		cmds.connectAttr('%s.output' %sPlus_heelRollSum, '%s.rz' %lJntsFootRvs[1])

		#### toe tap
		cmds.connectAttr('%s.toeTap' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[-2])

		#### foot bank
		sMult_footBank = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = '%sFootBankRvs' %self._sName).sName)
		cmds.connectAttr('%s.footBank' %self._lCtrls[2], '%s.input1' %sMult_footBank)
		cmds.setAttr('%s.input2' %sMult_footBank, -1, lock = True)
		cmds.connectAttr('%s.footBank' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[3])
		cmds.connectAttr('%s.output' %sMult_footBank, '%s.rz' %lJntsFootRvs[4])
		cmds.transformLimits(lJntsFootRvs[3], rz = [0,360], erz = [1,0])
		cmds.transformLimits(lJntsFootRvs[4], rz = [0,360], erz = [1,0])

		#### toeSlide
		cmds.connectAttr('%s.toeSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[2])

		#### heelSlide
		cmds.connectAttr('%s.heelSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[1])

		#### ballSlide ballTwist 
		cmds.connectAttr('%s.ballSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[5])

		#### toeWiggle toeTwist
		cmds.connectAttr('%s.toeWiggle' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[-2])
		cmds.connectAttr('%s.toeTwist' %self._lCtrls[2], '%s.rx' %lJntsFootRvs[-2])

		#### footSlide
		cmds.connectAttr('%s.footSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[0])

		#### bind joints
		if self._bBind:
			oJntName = naming.oName(sBpJntBall)
			oJntName.sType = 'bindJoint'
			sBindJnt = joints.createJntOnExistingNode(sBpJntBall, sBpJntBall, oJntName.sName, sParent = self._lBpJnts[-1])
			self._lBindJnts.append(sBindJnt)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(lJntsFoot[0], sAxis), '%s.translate%s' %(sBindJnt, sAxis))
				cmds.connectAttr('%s.rotate%s' %(lJntsFoot[0], sAxis), '%s.rotate%s' %(sBindJnt, sAxis))
				cmds.connectAttr('%s.scale%s' %(lJntsFoot[0], sAxis), '%s.scale%s' %(sBindJnt, sAxis))


		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, lock = False)
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'legIkModule', type = 'string', lock = True)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, lock = False)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, len(self._lJnts), lock = True)
		sBindString = ''
		for sBind in self._lBindJnts:
			sBindString += '%s,' %sBind
		cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, lock = False, type = 'string')
		cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString[:-1], type = 'string', lock = True)


		## writeOutputMatrixInfo

		if self._bInfo:
		
			sMultMatrixWorldParent = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = len(self._lJnts) - 3).sName					
			sMultMatrixLocalParent = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = len(self._lJnts) - 3).sName

			for i, sJnt in enumerate(lJntsFoot):
				cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixLocal%03d' %(len(self._lJnts) - 2 + i), at = 'matrix')
				cmds.addAttr(self._sComponentMaster, ln = 'outputMatrixWorld%03d' %(len(self._lJnts) - 2 + i), at = 'matrix')

				sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixLocal' %self._sName, iIndex = len(self._lJnts) - 2 + i).sName)
				cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixLocal)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixLocalParent, '%s.matrixIn[1]' %sMultMatrixLocal)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.outputMatrixLocal%03d' %(self._sComponentMaster, len(self._lJnts) - 2 + i))
				sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sOutputMatrixWorld' %self._sName, iIndex = len(self._lJnts) - 2 + i).sName)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixIn[0]' %sMultMatrixWorld)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixWorldParent, '%s.matrixIn[1]' %sMultMatrixWorld)
				cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.outputMatrixWorld%03d' %(self._sComponentMaster, len(self._lJnts) - 2 + i))

				sMultMatrixWorldParent = sMultMatrixWorld
				sMultMatrixLocalParent = sMultMatrixLocal

		self._getComponentInfo(self._sComponentMaster)

		