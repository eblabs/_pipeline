## add twist joint function

## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.rigComponents.rigUtils.componentInfo as componentInfo

def twistJointsForLimb(iTwistJntNum, lSkipSections, lJnts, lBpJnts, bBind = False, sNode = None, bInfo = True):
	lTwistBindJnts_all = []
	lTwistJntSections = []
	if iTwistJntNum > 0:
		for i, sJnt in enumerate(lJnts[:-1]):
			if i not in lSkipSections:
				lTwistJntSections.append(i)
				lTwistJnts, lTwistBindJnts = _addTwistJointsForSection(sJnt, lJnts[i + 1], lBpJnts[i], iTwistJntNum, bBind = bBind)
				lTwistJntsBindAll += lTwistBindJnts
				if bInfo:
					_writeTwistJointsMatrixInfo(lTwistJnts, i, sNode = sNode)

		sTwistSections = componentInfo.composeListToString(lTwistJntSections)
		sTwistBindJoints = componentInfo.composeListToString(lTwistBindJnts_all)

		cmds.setAttr('%s.sTwistSections' %sNode, lock = False, type = 'string')
		cmds.setAttr('%s.sTwistSections' %sNode, sTwistSections, type = 'string', lock = True)
		cmds.setAttr('%s.iTwistJointCount' %sNode, lock = False)
		cmds.setAttr('%s.iTwistJointCount' %sNode, iTwistJntNum, lock = True)
		cmds.setAttr('%s.sTwistBindJoints' %sNode, lock = False, type = 'string')
		cmds.setAttr('%s.sTwistBindJoints' %sNode, sTwistBindJoints, type = 'string', lock = True)

def _writeTwistJointsMatrixInfo(lTwistJnts, iSection, sNode = None):
	for i, sJnt in enumerate(lTwistJnts):
		## naming info
		oName = naming.oName(sJnt)
		sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oName.sSide, sPart = '%sOutputMatrixLocal' %oName.sPart, iIndex = oName.iIndex).sName)
		sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oName.sSide, sPart = '%sOutputMatrixWorld' %oName.sPart, iIndex = oName.iIndex).sName)
		cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixLocal)
		cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrixWorld)

		#### plug parent joint local matrix and world matrix
		cmds.connectAttr('%s.outputMatrixLocal%03d' %(sNode, iSection), '%s.matrixIn[1]' %sMultMatrixLocal)
		cmds.connectAttr('%s.outputMatrixWorld%03d' %(sNode, iSection), '%s.matrixIn[1]' %sMultMatrixWorld)

		#### add attr
		cmds.addAttr(sNode, ln = 'output%03dTwistMatrixLocal%03d' %(iSection, i), at = 'matrix')
		cmds.addAttr(sNode, ln = 'output%03dTwistMatrixWorld%03d' %(iSection, i), at = 'matrix')

		#### connect attr
		cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.output%03dTwistMatrixLocal%03d' %(sNode, iSection, i))
		cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.output%03dTwistMatrixWorld%03d' %(sNode, iSection, i))

def _addTwistJointsForSection(sJntStart, sJntEnd, sBpJnt, iTwistJntNum, bBind = False):
	## naming info
	oTwistName = naming.oName(sBpJnt)

	## start end twist driver
	sTwistPlug_start = _twistMatrixDriver(sJntStart, oTwistName, sPart = 'Start')
	sTwistPlug_end = _twistMatrixDriver(sJntEnd, oTwistName, sPart = 'End', sRotateReference = sJntStart)

	## create twist joints
	lTwistJnts = []
	lTwistBindJnts = []
	for i in range(iTwistJntNum):
		## create twist joint
		oJntName = naming.oName(sBpJnt)
		oJntName.sType = 'joint'
		oJntName.sPart = '%sTwist%03d' %(oJntName.sPart, i)
		sTwist = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sJntStart)
		lTwistJnts.append(sTwist)

		if bBind:
			oJntName.sType = 'bindJoint'
			oBindName = naming.oName(sBpJnt)
			oBindName.sType = 'bindJoint'
			sBindJnt = joints.createJntOnExistingNode(sTwist, sTwist, oJntName.sName, sParent = oBindName.sName)
			lTwistBindJnts.append(sBindJnt)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sTwist, sAxis), '%s.translate%s' %(sBindJnt, sAxis))
				cmds.connectAttr('%s.rotate%s' %(sTwist, sAxis), '%s.rotate%s' %(sBindJnt, sAxis))
				cmds.connectAttr('%s.scale%s' %(sTwist, sAxis), '%s.scale%s' %(sBindJnt, sAxis))

		if i > 0 and i < iTwistJntNum - 1:
			fWeight = i/float(iTwistJntNum - 1)
			## position
			sMult = cmds.createNode('multiplyDivide', name = naming.oName(sType = 'multiplyDivide', sSide = oJntName.sSide, sPart = '%sPos' %oJntName.sPart, iIndex = oJntName.iIndex).sName)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntEnd, sAxis), '%s.input1%s' %(sMult, sAxis))
				cmds.setAttr('%s.input2%s' %(sMult, sAxis), fWeight)
				cmds.connectAttr('%s.output%s' %(sMult, sAxis), '%s.translate%s' %(sTwist, sAxis))

			## twist
			sPlus = cmds.createNode('addDoubleLinear', name = naming.oName(sType = 'addDoubleLinear', sSide = oJntName.sSide, sPart = '%sTwistSum' %oJntName.sPart, iIndex = oJntName.iIndex).sName)
			sMultTwistStart = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'multDoubleLinear', sSide = oJntName.sSide, sPart = '%sTwistStartWeight' %oJntName.sPart, iIndex = oJntName.iIndex).sName)
			sMultTwistEnd = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'multDoubleLinear', sSide = oJntName.sSide, sPart = '%sTwistEndWeight' %oJntName.sPart, iIndex = oJntName.iIndex).sName)
			cmds.connectAttr(sTwistStartPlug, '%s.input1' %sMultTwistStart)
			cmds.connectAttr(sTwistEndPlug, '%s.input1' %sMultTwistEnd)
			cmds.setAttr('%s.input2' %sMultTwistStart, 1 - fWeight)
			cmds.setAttr('%s.input2' %sMultTwistEnd, fWeight)
			cmds.connectAttr('%s.output' %sMultTwistStart, '%s.input1' %sPlus)
			cmds.connectAttr('%s.output' %sMultTwistEnd, '%s.input2' %sPlus)
			cmds.connectAttr('%s.output' %sPlus, '%s.rx' %sTwist)

		elif i == iTwistJntNum - 1:
			fWeight = 1
			cmds.connectAttr(sTwistEndPlug, '%s.rx' %sTwist)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.translate%s' %(sJntEnd, sAxis), '%s.translate%s' %(sTwist, sAxis))
		else:
			fWeight = 0
			cmds.connectAttr(sTwistStartPlug, '%s.rx' %sTwist)
	return lTwistJnts, lTwistBindJnts


def _twistMatrixDriver(sJnt, oName, sPos = 'Start', sRotateReference = None):
	else:
		sMultMatrix = '%s.matrix' %sJnt

	sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = oName.sSide, sPart = '%sTwist%s' %(oName.sPart, sPart), iIndex = oName.iIndex).sName)
	cmds.connectAttr('%s.matrixSum' %sMultMatrixStart, '%s.inputMatrix' %sDecomposeMatrixStart)
	sQuatToEuler = cmds.createNode('quatToEuler', name = naming.oName(sType = 'quatToEuler', sSide = oName.sSide, sPart = '%sTwist%s' %(oName.sPart, sPart), iIndex = oName.iIndex).sName)
	cmds.connectAttr('%s.outputQuatX' %sDecomposeMatrix, '%s.inputQuatX' %sQuatToEuler)
	cmds.connectAttr('%s.outputQuatW' %sDecomposeMatrix, '%s.inputQuatW' %sQuatToEuler)
	if not sRotateReference:
		sRotateReference = sJnt
	cmds.connectAttr('%s.rotateOrder' %sRotateReference, '%s.inputRotateOrder' %sQuatToEuler)

	if sPos == 'Start':
		sMultMatrix = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = oName.sSide, sPart = '%sTwist%s' %(oName.sPart, sPos), iIndex = oName.iIndex).sName)
		cmds.connectAttr('%s.matrix' %sJnt, '%s.matrixIn[0]' %sMultMatrix)
		lJntOrient = joints.getJointOrient(sJnt)
		mMatrix = apiUtils.createMMatrixFromTransformInfo(lRotate = lJntOrient)
		lMatrixInInverse = apiUtils.convertMMatrixToList(mMatrix.inverse())
		cmds.setAttr('%s.matrixIn[1]' %sMultMatrix, lMatrixInInverse, type = 'matrix')
		cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %sDecomposeMatrix)

		sMultTwist = cmds.createNode('multDoubleLinear', name = naming.oName(sType = 'multDoubleLinear', sSide = oTwist.sSide, sPart = '%sTwist%s' %(oName.sPart, sPos), iIndex = oName.iIndex).sName)
		cmds.connectAttr('%s.outputRotateX' %sQuatToEuler, '%s.input1' %sMultTwist)
		cmds.setAttr('%s.input2' %sMultTwist, -1)
		sTwistPlug = '%s.output' %sMultTwist
	else:
		cmds.connectAttr('%s.matrix' %sJnt, '%s.inputMatrix' %sDecomposeMatrix)
		sTwistPlug = '%s.outputRotateX' %sQuatToEuler

	return sTwistPlug


