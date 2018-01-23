########################################################
# base ik spline solver limb
# this limb should do the ik spline solver rig functions
########################################################
## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.apiUtils as apiUtils
import riggingAPI.joints as joints
import riggingAPI.controls as controls
import modelingAPI.curves as curves

import riggingAPI.rigComponents.baseComponent as baseComponent

class baseIkSplineSolverLimb(baseComponent.baseComponent):
	"""docstring for baseIkSplineSolverLimb"""
	def __init__(self, *args, **kwargs):
		super(baseIkSplineSolverLimb, self).__init__(*args, **kwargs)
		if args:
			self._getComponentInfo(args[0])
		else:
			self._lBpJnts = kwargs.get('lBpJnts', None)
			self._iStacks = kwargs.get('iStacks', 1)
			self._bBind = kwargs.get('bBind', False)

	def createComponent(self):
		super(baseIkSplineSolverLimb, self).createComponent()

		sParent_jnt = self._sComponentDrvJoints		
		lJnts = []
		

		for i, sBpJnt in enumerate(self._lBpJnts):
			## jnt
			oJntName = naming.oName(sBpJnt)
			oJntName.sType = 'jnt'
			oJntName.sPart = '%sIkSpline' %oJntName.sPart
			sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent_jnt)
			sParent_jnt = sJnt
			lJnts.append(sJnt)

		## generate curve
		sIkHnd = naming.oName(sType = 'ikHandle', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = self._iIndex).sName
		sCurve = naming.oName(sType = 'curve', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = self._iIndex).sName
		lIkNodes = cmds.ikHandle(sj = lJnts[0], ee = lJnts[-1], sol = 'ikSplineSolver', ccv = True, scv = False)
		cmds.rename(lIkNodes[-1], sCurve)
		cmds.delete(lIkNodes[:-1])
		lClsHnds = curves.clusterCurve(sCurve, bRelatives = True)
		#### rebuild curve
		iCvs = curves.getCurveCvNum(sCurve)
		cmds.rebuild(sCurve, ch = 1, rebuildType = 0, degree = 3, s = iCvs - 3, keepRange = 0, rpo = True)
		#### set up ik
		cmds.ikHandle(sj = lJnts[0], ee = lJnts[-1], sol = 'ikSplineSolver', ccv = False, scv = False, curve = sCurve, name = sIkHnd)
		cmds.makeIdentity(lJnts[0], apply = True, t = 1, r = 1, s = 1)

		## bind jnt
		sParent_bind = self._sComponentBindJoints
		lBindJnts = []

		if self._bBind:
			for i, sJnt in enumerate(lJnts):
				oJntName = namingAPI.oName(sJnt)
				oJntName.sType = 'bindJoint'
				sBindJnt = joints.createJntOnExistingNode(sJnt, sJnt, oJntName.sName, sParent = sParent_bind)
				sParent_bind = sBindJnt
				lBindJnts.append(sBindJnt)
				for sAxis in ['X', 'Y', 'Z']:
					cmds.connectAttr('%s.translate%s' %(sJnt, sAxis), '%s.translate%s' %(sBindJnt, sAxis))
					cmds.connectAttr('%s.rotate%s' %(sJnt, sAxis), '%s.rotate%s' %(sBindJnt, sAxis))
					cmds.connectAttr('%s.scale%s' %(sJnt, sAxis), '%s.scale%s' %(sBindJnt, sAxis))

		## rig setup
		cmds.parent(sCurve, lClsHnds, sIkHnd, self._sComponentRigNodesLocal)

		#### controls
		lCtrls = []
		iNum = 1
		for i, sClsHnd in enumerate(lClsHnds):
			if i != 1 and i != len(lClsHnds) - 2:
				oCtrl = controls.create('%sSplineSolver' %self._sName, sSide = self._sSide, iIndex = iNum, iStacks = self._iStacks, bSub = True, sParent = self._sComponentControls, sPos = sClsHnd, sShape = 'cube', fSize = 4, lLockHideAttrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
				sMultMatrix  = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = i).sName)
				sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = i).sName)
				cmds.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[0]' %sMultMatrix)
				lPos = cmds.xform(sClsHnd, q = True, rp = True)
				mMatrix = apiUtils.createMMatrixFromTransformInfo(lTranslate = lPos)
				lMatrixInverse = apiUtils.convertMMatrixToList(mMatrix.inverse())
				cmds.setAttr('%s.matrixIn[1]' %sMultMatrix, lMatrixInverse, type = 'matrix')
				cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %sDecomposeMatrix)
				cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.t' %sClsHnd)
				lCtrls.append(oCtrl.sName)
				iNum += 1
			elif i == 1:
				lPosChild = cmds.xform(sClsHnd, q = True, rp = True)
				mMatrixChild = apiUtils.createMMatrixFromTransformInfo(lTranslate = lPosChild)
				mMatrixChildLocal = mMatrixChild * mMatrix.inverse()
				lMatrixChildLocal = apiUtils.convertMMatrixToList(mMatrixChildLocal)
				sMultMatrix  = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = i).sName)
				sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = i).sName)				
				cmds.setAttr('%s.matrixIn[0]' %sMultMatrix, lMatrixChildLocal, type = 'matrix')
				cmds.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[1]' %sMultMatrix)
				lMatrixChildInverse = apiUtils.convertMMatrixToList(mMatrixChild.inverse())
				cmds.setAttr('%s.matrixIn[2]' %sMultMatrix, lMatrixChildInverse, type = 'matrix')
				cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %sDecomposeMatrix)
				cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.t' %sClsHnd)
		#### do with the second last one, should be controlled by the last control
		lPosChild = cmds.xform(lClsHnds[-2], q = True, rp = True)
		mMatrixChild = apiUtils.createMMatrixFromTransformInfo(lTranslate = lPosChild)
		mMatrixChildLocal = mMatrixChild * mMatrix.inverse()
		lMatrixChildLocal = apiUtils.convertMMatrixToList(mMatrixChildLocal)
		sMultMatrix  = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = len(lClsHnds) - 2).sName)
		sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = naming.oName(sType = 'decomposeMatrix', sSide = self._sSide, sPart = '%sSplineSolver' %self._sName, iIndex = len(lClsHnds) - 2).sName)				
		cmds.setAttr('%s.matrixIn[0]' %sMultMatrix, lMatrixChildLocal, type = 'matrix')
		cmds.connectAttr('%s.matrixOutputWorld' %oCtrl.sName, '%s.matrixIn[1]' %sMultMatrix)
		lMatrixChildInverse = apiUtils.convertMMatrixToList(mMatrixChild.inverse())
		cmds.setAttr('%s.matrixIn[2]' %sMultMatrix, lMatrixChildInverse, type = 'matrix')
		cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %sDecomposeMatrix)
		cmds.connectAttr('%s.outputTranslate' %sDecomposeMatrix, '%s.t' %lClsHnds[-2])

		## pass info to class
		self._lJnts = lJnts
		self._lCtrls = lCtrls
		self._lBindJnts = lBindJnts
		self._sIkHnd = sIkHnd

		## write component info
		cmds.setAttr('%s.sComponentType' %self._sComponentMaster, 'baseIkSplineSolverLimb', type = 'string', lock = True)
		cmds.setAttr('%s.iJointCount' %self._sComponentMaster, len(lJnts), lock = True)
		sControlsString = ''
		for sCtrl in lCtrls:
			sControlsString += '%s,' %sCtrl
		cmds.setAttr('%s.sControls' %self._sComponentMaster, sControlsString[:-1], type = 'string', lock = True)
		if self._bBind:
			sBindString = ''
			for sBind in lBindJnts:
				sBindString += '%s,' %sBind
			cmds.setAttr('%s.sBindJoints' %self._sComponentMaster, sBindString[:-1], type = 'string', lock = True)

		## output matrix
		self._writeOutputMatrixInfo(lJnts, bHierarchy = True)

		self._getComponentInfo(self._sComponentMaster)

