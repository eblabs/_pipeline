## import
import maya.cmds as cmds
import maya.mel as mel
## import libs
import common.transforms as transforms
import namingAPI.naming as naming
import riggingAPI.joints as joints
import riggingAPI.constraints as constraints
import riggingAPI.controls as controls
import riggingAPI.rigLimbs.baseLimbs.ikRPsolverRig as ikRPsolverRig
import modelingAPI.curves as curves
import common.attributes as attributes
## function
class legIkRig(ikRPsolverRig.ikRPsolverRig ):
	"""docstring for legIkRig"""
	def __init__(self, *args, **kwargs):
		super(legIkRig, self).__init__(*args, **kwargs)

		self._sPart = 'leg'
		self._bOrient = False
		self._sName = 'Ik'

	@property
	def lJntsOutput(self):
		return self._lJntsOutput

	def create(self):
		self._lBpJnts = [
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperLeg').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'knee').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ankle').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ball').sName,
							naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'toe').sName,
						]

		self._sBpCtrl = naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'footIk').sName
		self._sBpPv = naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'kneePvIk').sName
		self._sBpRoot = naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'upperLegIk').sName

		self._lBpJntsFootRvs = [
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'footTwistRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'heelRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'toeTipRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'footEndRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'footOutRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'footInnRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ballRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ankleRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'ankleEndRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'toeRvs').sName,
								naming.oName(sType = 'bpJnt', sSide = self._sSide, sPart = 'toeEndRvs').sName,	
								]

		self._lBpJntsFoot = self._lBpJnts[2:5]
		self._lBpJnts = self._lBpJnts[0:3]
		super(legIkRig, self).create()

		## foot joints
		sParent_jnt = self._lJnts[-1]
		for sBpJnt in self._lBpJntsFoot[1:]:
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%s%s' %(oJntName.sPart, self._sName)
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			self._lJnts.append(sJnt)
			sParent_jnt = sJnt

		## ik handle
		oName = naming.oName(self._lJnts[3])
		sIkHnd_ball = naming.oName(sType = 'ikHandle', sSide = oName.sSide, sPart = '%sSCsolver' %oName.sPart, iIndex = oName.iIndex).sName
		cmds.ikHandle(sj = self._lJnts[2], ee = self._lJnts[3], sol = 'ikSCsolver', name = sIkHnd_ball)

		oName = naming.oName(self._lJnts[-1])
		sIkHnd_toe = naming.oName(sType = 'ikHandle', sSide = oName.sSide, sPart = '%sSCsolver' %oName.sPart, iIndex = oName.iIndex).sName
		cmds.ikHandle(sj = self._lJnts[-2], ee = self._lJnts[-1], sol = 'ikSCsolver', name = sIkHnd_toe)

		## foot rvs
		lJntsFootRvs = []
		for sBpJnt in self._lBpJntsFootRvs:
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			lJntsFootRvs.append(sJnt)
			if sBpJnt == self._lBpJntsFootRvs[0]:
				oCtrl = controls.oControl(self._lCtrls[-1])
				cmds.parent(sJnt, oCtrl.sOutput)
				cmds.setAttr('%s.v' %sJnt, 0)
			else:
				sParentBp = cmds.listRelatives(sBpJnt, p = True)[0]
				oJntNameParent = naming.oName(sParentBp)
				oJntNameParent.sType = 'jnt'
				sJntParent = oJntNameParent.sName
				cmds.parent(sJnt, sJntParent)

		sIkGrp = cmds.listRelatives(self._sIkHnd, p = True)[0]
		#### parent ik handles
		cmds.parent(self._sIkHnd, lJntsFootRvs[8])
		cmds.parent(sIkHnd_ball, lJntsFootRvs[6])
		cmds.parent(sIkHnd_toe, lJntsFootRvs[-1])
		cmds.delete(sIkGrp)

		#### foot rig
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
		sClamp_footRoll = cmds.createNode('clamp', name = naming.oName(sType = 'clamp', sSide = self._sSide, sPart = 'footRoll').sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.inputR' %sClamp_footRoll)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.maxR' %sClamp_footRoll) 
		sPlus_ballRoll = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'add', sSide = self._sSide, sPart = 'ballRoll').sName)
		cmds.connectAttr('%s.outputR' %sClamp_footRoll, '%s.input1' %sPlus_ballRoll)
		sRemap_ballRoll = cmds.createNode('remapValue', name = naming.oName(sType = 'remap', sSide = self._sSide, sPart = 'ballRollStraight').sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.inputValue' %sRemap_ballRoll)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.inputMin' %sRemap_ballRoll)
		cmds.connectAttr('%s.toeStraight' %self._lCtrls[2], '%s.inputMax' %sRemap_ballRoll)
		cmds.connectAttr('%s.outValue' %sRemap_ballRoll, '%s.input2' %sPlus_ballRoll)
		sMult_ballRollLift = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = 'ballRollLiftNeg').sName)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.input1' %sMult_ballRollLift)
		cmds.setAttr('%s.input2' %sMult_ballRollLift, -1, lock = True)
		cmds.connectAttr('%s.output' %sMult_ballRollLift, '%s.outputMax' %sRemap_ballRoll)
		sPlus_ballRollSum = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'add', sSide = self._sSide, sPart = 'ballRollSum').sName)
		cmds.connectAttr('%s.output' %sPlus_ballRoll, '%s.input1' %sPlus_ballRollSum)
		cmds.connectAttr('%s.ballRoll' %self._lCtrls[2], '%s.input2' %sPlus_ballRollSum)
		cmds.connectAttr('%s.output' %sPlus_ballRollSum, '%s.rz' %lJntsFootRvs[7])

		#### toe roll
		sRemap_toeRoll = cmds.createNode('remapValue', name = naming.oName(sType = 'remapValue', sSide = self._sSide, sPart = 'toeRoll').sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.inputValue' %sRemap_toeRoll)
		cmds.connectAttr('%s.toeLift' %self._lCtrls[2], '%s.inputMin' %sRemap_toeRoll)
		cmds.connectAttr('%s.toeStraight' %self._lCtrls[2], '%s.inputMax' %sRemap_toeRoll)
		sMult_toeRoll = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = 'toeRoll').sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.input1' %sMult_toeRoll)
		cmds.connectAttr('%s.outValue' %sRemap_toeRoll, '%s.input2' %sMult_toeRoll)
		sPlus_toeRollSum = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'add', sSide = self._sSide, sPart = 'toeRollSum').sName)
		cmds.connectAttr('%s.output' %sMult_toeRoll, '%s.input1' %sPlus_toeRollSum)
		cmds.connectAttr('%s.toeRoll' %self._lCtrls[2], '%s.input2' %sPlus_toeRollSum)
		cmds.connectAttr('%s.output' %sPlus_toeRollSum, '%s.rz' %lJntsFootRvs[2])

		#### heel Roll
		sCond_heel = cmds.createNode('condition', name = naming.oName(sType = 'condition', sSide = self._sSide, sPart = 'heelRoll').sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.firstTerm' %sCond_heel)
		cmds.setAttr('%s.operation' %sCond_heel, 4)
		cmds.setAttr('%s.colorIfFalseR' %sCond_heel, 0)
		sMult_heelRoll = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'multDoubleLinear', sSide = self._sSide, sPart = 'heelRollRvs').sName)
		cmds.connectAttr('%s.footRoll' %self._lCtrls[2], '%s.input1' %sMult_heelRoll)
		cmds.setAttr('%s.input2' %sMult_heelRoll, -1, lock = True)
		cmds.connectAttr('%s.output' %sMult_heelRoll, '%s.colorIfTrueR' %sCond_heel)
		sPlus_heelRollSum = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'addDoubleLinear', sSide = self._sSide, sPart = 'heelRollSum').sName)
		cmds.connectAttr('%s.outColorR' %sCond_heel, '%s.input1' %sPlus_heelRollSum)
		cmds.connectAttr('%s.heelRoll' %self._lCtrls[2], '%s.input2' %sPlus_heelRollSum)
		cmds.connectAttr('%s.output' %sPlus_heelRollSum, '%s.rz' %lJntsFootRvs[1])

		#### toe tap
		cmds.connectAttr('%s.toeTap' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[-2])

		#### foot bank
		sMult_footBank = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'mult', sSide = self._sSide, sPart = 'footBankRvs').sName)
		cmds.connectAttr('%s.footBank' %self._lCtrls[2], '%s.input1' %sMult_footBank)
		cmds.setAttr('%s.input2' %sMult_footBank, -1, lock = True)
		cmds.connectAttr('%s.footBank' %self._lCtrls[2], '%s.rz' %lJntsFootRvs[4])
		cmds.connectAttr('%s.output' %sMult_footBank, '%s.rz' %lJntsFootRvs[5])
		cmds.transformLimits(lJntsFootRvs[4], rz = [0,360], erz = [1,0])
		cmds.transformLimits(lJntsFootRvs[4], rz = [0,360], erz = [1,0])

		#### toeSlide
		cmds.connectAttr('%s.toeSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[2])

		#### heelSlide
		cmds.connectAttr('%s.heelSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[1])

		#### ballSlide ballTwist 
		cmds.connectAttr('%s.ballSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[7])

		#### toeWiggle toeTwist
		cmds.connectAttr('%s.toeWiggle' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[-2])
		cmds.connectAttr('%s.toeTwist' %self._lCtrls[2], '%s.rx' %lJntsFootRvs[-2])

		#### footSlide
		cmds.connectAttr('%s.footSlide' %self._lCtrls[2], '%s.ry' %lJntsFootRvs[0])

		sString_lJntsOutput = self._convertListToString(self._lJnts[:-1])
		lRigInfo = ['legIkRig', sString_lJntsOutput]
		lAttrs = ['sModuleType', 'lJntsOutput']
		self._writeRigInfo(self._sModuleNode, lRigInfo, lAttrs)

		self._getRigInfo(self._sModuleNode)

	def _getRigInfo(self, sModuleNode):
		super(legIkRig, self)._getRigInfo(sModuleNode)
		if cmds.attributeQuery('lJntsOutput', node = sModuleNode, ex = True):
			sJntsOutputString = cmds.getAttr('%s.lJntsOutput' %sModuleNode)
			self._lJntsOutput = sJntsOutputString.split(',')

