## External Import
import maya.cmds as cmds
import maya.mel as mel

## lib import
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import modelingAPI.meshes as meshes
import modelingAPI.surfaces as surfaces
import common.apiUtils as apiUtils
## functions
def constraint(lNodes, sType = 'parent', sConstraintType = 'oneToAll', bMaintainOffset = False, lSkipTranslate = None, lSkipRotate = None, lSkipScale = None, bForce = False):
	if not lSkipTranslate:
		lSkipTranslate = 'none'
	if not lSkipRotate:
		lSkipRotate = 'none'
	if not lSkipScale:
		lSkipScale = 'none'

	if sConstraintType == 'oneToAll':
		sDriver = lNodes[0]
		lDriven = lNodes[1:]
		for sDriven in lDriven:
			lConstraints = __constraint([sDriver], sDriven, bMaintainOffset = bMaintainOffset, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale, bForce = bForce, sType = sType)
	elif sConstraintType == 'allToOne':
		lDrivers = lNodes[:-1]
		sDriven = lNodes[-1]
		lConstraints = __constraint(lDrivers, sDriven, bMaintainOffset = bMaintainOffset, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale, bForce = bForce, sType = sType)

	return lConstraints

def follicleConstraint(sGeo, lNodes, sType = 'parent', bMaintainOffset = True, lSkipTranslate = None, lSkipRotate = None, bForce = False):
	oName = naming.oName(sGeo)
	sGrpFollicle = naming.oName(sType = 'grp', sSide = oName.sSide, sPart = '%sFollicle' %oName.sPart, iIndex = oName.iIndex).sName
	if not cmds.objExists(sGrpFollicle):
		transforms.createTransformNode(sGrpFollicle, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
		cmds.addAttr(sGrpFollicle, ln = 'follicleCount', at = 'long', dv = 0)
		cmds.setAttr('%s.follicleCount' %sGrpFollicle, lock = True)
	sGeoShape = meshes.getShape(sGeo)

	lFollicles = []
	iFollicle = cmds.getAttr('%s.follicleCount' %sGrpFollicle)
	for i, sNode in enumerate(lNodes):
		lPos_node = cmds.xform(sNode, q = True, t = True, ws = True)
		if cmds.objectType(sGeoShape) == 'mesh':
			lPosClst, lPosUv = meshes.getClosestPointOnMesh(lPos_node, sGeo)
			lShapeConnectAttr = ['outMesh', 'inputMesh']
		elif cmds.objectType(sGeoShape) == 'nurbsSurface':
			lPosClst, lPosUv = surfaces.getClosestPointOnSurface(lPos_node, sGeo)
			lShapeConnectAttr = ['local', 'inputSurface']
		else:
			raise RuntimeError('%s is not a mesh or nurbs surface' %sGeo)

		## create follicle
		sFollicleShape = cmds.createNode('follicle')
		sFollicleTrans = cmds.listRelatives(sFollicleShape, p = True)[0]
		sFollicle = naming.oName(sType = 'follicle', sSide = oName.sSide, sPart = '%sFollicle' %oName.sPart, iIndex = oName.iIndex, iSuffix = iFollicle + i + 1).sName
		cmds.rename(sFollicleTrans, sFollicle)
		sFollicleShape = cmds.listRelatives(sFollicle, s = True)[0]

		lFollicles.append(sFollicle)

		## connect
		cmds.connectAttr('%s.%s' %(sGeoShape, lShapeConnectAttr[0]), '%s.%s' %(sFollicleShape, lShapeConnectAttr[1]))
		cmds.connectAttr('%s.worldMatrix[0]' %sGeoShape, '%s.inputWorldMatrix' %sFollicleShape)
		for sAttr in ['X', 'Y', 'Z']:
			cmds.connectAttr('%s.outRotate%s' %(sFollicleShape, sAttr), '%s.rotate%s' %(sFollicle, sAttr))
			cmds.connectAttr('%s.outTranslate%s' %(sFollicleShape, sAttr), '%s.translate%s' %(sFollicle, sAttr))
		cmds.setAttr('%s.parameterU' %sFollicleShape, lPosUv[0])
		cmds.setAttr('%s.parameterV' %sFollicleShape, lPosUv[1])

		cmds.parent(sFollicle, sGrpFollicle)

		## constraint
		constraint([sFollicle, sNode], sType = sType, bMaintainOffset = bMaintainOffset, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, bForce = bForce)

	## update follicle count
	cmds.setAttr('%s.follicleCount' %sGrpFollicle, lock = False)
	cmds.setAttr('%s.follicleCount' %sGrpFollicle, iFollicle + len(lNodes), lock = True)

	return sGrpFollicle, lFollicles

def spaceConstraint(dDrivers, sDriven, sType = 'parent', sCtrl = None, bMaintainOffset = True, sName = 'space', lDefaultVal = None):
	## dDrivers = {'cog': {'iIndex': 0, 'sOutput': 'ctrl_m_cog'}}
	sEnum = ''
	for sSpace in dDrivers.keys():
		sEnum += '%s=%d:' %(sSpace, dDrivers[sSpace]['iIndex'])

	if sType == 'parent':
		sConstraint = cmds.createNode('parentConstraint', name = '%s_parentConstraint1' %sDriven)
		cmds.parent(sConstraint, sDriven)
		for sAttr in ['translate', 'rotate']:
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.constraint%s%s' %(sConstraint, sAttr.title(), sAxis), '%s.%s%s' %(sDriven, sAttr, sAxis))
		for sAttr in ['rotateOrder', 'rotatePivot']:
			cmds.connectAttr('%s.%s' %(sDriven, sAttr), '%s.constraint%s%s' %(sConstraint, sAttr[0].upper(), sAttr[1:]))
		cmds.connectAttr('%s.rotatePivotTranslate' %sDriven, '%s.constraintRotateTranslate' %sConstraint)
		cmds.connectAttr('%s.parentInverseMatrix[0]' %sDriven, '%s.constraintParentInverseMatrix' %sConstraint)
		lAttrs_s = ['translate', 'rotate', 'scale', 'parentMatrix[0]', 'rotateOrder', 'rotatePivot', 'rotatePivotTranslate']
		lAttrs_d = ['targetTranslate', 'targetRotate', 'targetScale', 'targetParentMatrix', 'targetRotateOrder', 'targetRotatePivot', 'targetRotateTranslate']

	elif sType == 'point':
		sConstraint = cmds.createNode('pointConstraint', name = '%s_pointConstraint1' %sDriven)
		cmds.parent(sConstraint, sDriven)
		for sAttr in ['translate']:
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.constraint%s%s' %(sConstraint, sAttr.title(), sAxis), '%s.%s%s' %(sDriven, sAttr, sAxis))
		for sAttr in ['rotatePivot']:
			cmds.connectAttr('%s.%s' %(sDriven, sAttr), '%s.constraint%s%s' %(sConstraint, sAttr[0].upper(), sAttr[1:]))
		cmds.connectAttr('%s.rotatePivotTranslate' %sDriven, '%s.constraintRotateTranslate' %sConstraint)
		cmds.connectAttr('%s.parentInverseMatrix[0]' %sDriven, '%s.constraintParentInverseMatrix' %sConstraint)
		lAttrs_s = ['translate','parentMatrix[0]', 'rotatePivot', 'rotatePivotTranslate']
		lAttrs_d = ['targetTranslate', 'targetParentMatrix', 'targetRotatePivot', 'targetRotateTranslate']

	elif sType == 'orient':
		sConstraint = cmds.createNode('orientConstraint', name = '%s_orientConstraint1' %sDriven)
		cmds.parent(sConstraint, sDriven)
		for sAttr in ['rotate']:
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.constraint%s%s' %(sConstraint, sAttr.title(), sAxis), '%s.%s%s' %(sDriven, sAttr, sAxis))
		for sAttr in ['rotateOrder']:
			cmds.connectAttr('%s.%s' %(sDriven, sAttr), '%s.constraint%s%s' %(sConstraint, sAttr[0].upper(), sAttr[1:]))
		cmds.connectAttr('%s.parentInverseMatrix[0]' %sDriven, '%s.constraintParentInverseMatrix' %sConstraint)
		lAttrs_s = ['rotate', 'parentMatrix[0]', 'rotateOrder']
		lAttrs_d = ['targetRotate', 'targetParentMatrix', 'targetRotateOrder']

	elif sType == 'scale':
		sConstraint = cmds.createNode('scaleConstraint', name = '%s_scaleConstraint1' %sDriven)
		cmds.parent(sConstraint, sDriven)
		for sAttr in [ 'scale']:
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.constraint%s%s' %(sConstraint, sAttr.title(), sAxis), '%s.%s%s' %(sDriven, sAttr, sAxis))
		cmds.connectAttr('%s.parentInverseMatrix[0]' %sDriven, '%s.constraintParentInverseMatrix' %sConstraint)
		lAttrs_s = ['scale', 'parentMatrix[0]']
		lAttrs_d = ['targetScale', 'targetParentMatrix']

	## add attr to ctrl
	if not sCtrl:
		sCtrl = sDriven

	oNameCtrl = naming.oName(sCtrl)
	sRvs = naming.oName(sType = 'reverse', sSide = oNameCtrl.sSide, sPart = '%s%s%sBlend' %(oNameCtrl.sPart, sName[0].upper(), sName[1:]), iIndex = oNameCtrl.iIndex, iSuffix = oNameCtrl.iSuffix).sName

	if not cmds.attributeQuery('%sDivider' %sName, node = sCtrl, exists = True):
		attributes.addDivider([sCtrl], sName)
		cmds.addAttr(sCtrl, ln = '%sModeA' %sName, nn = 'Mode A', at = 'enum', en = sEnum[:-1], keyable = True)
		cmds.addAttr(sCtrl, ln = '%sModeB' %sName, nn = 'Mode B', at = 'enum', en = sEnum[:-1], keyable = True)
		cmds.addAttr(sCtrl, ln = '%sModeBlend' %sName, nn = 'Mode A---B', at = 'float', min = 0, max = 1, keyable = True)
		sRvs = cmds.createNode('reverse', name = sRvs)
		cmds.connectAttr('%s.%sModeBlend' %(sCtrl, sName), '%s.inputX' %sRvs)

	cmds.connectAttr('%s.%sModeBlend' %(sCtrl, sName), '%s.target[1].targetWeight' %sConstraint)
	cmds.connectAttr('%s.outputX' %sRvs, '%s.target[0].targetWeight' %sConstraint)

	oNameDriven = naming.oName(sDriven)
	for i, sAttr_s in enumerate(lAttrs_s):
		sChoiceA = naming.oName(sType = 'choice', sSide = oNameDriven.sSide, sPart = '%s%s%s%s%sA' %(oNameDriven.sPart, sName[0].upper(), sName[1:], lAttrs_d[i][0].upper(), lAttrs_d[i][1:]), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
		sChoiceB = naming.oName(sType = 'choice', sSide = oNameDriven.sSide, sPart = '%s%s%s%s%sB' %(oNameDriven.sPart, sName[0].upper(), sName[1:], lAttrs_d[i][0].upper(), lAttrs_d[i][1:]), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
		sChoiceA = cmds.createNode('choice', name = sChoiceA)
		sChoiceB = cmds.createNode('choice', name = sChoiceB)
		cmds.connectAttr('%s.output' %sChoiceA, '%s.target[0].%s' %(sConstraint, lAttrs_d[i]))
		cmds.connectAttr('%s.output' %sChoiceB, '%s.target[1].%s' %(sConstraint, lAttrs_d[i]))
		cmds.connectAttr('%s.%sModeA' %(sCtrl, sName), '%s.selector' %sChoiceA)
		cmds.connectAttr('%s.%sModeB' %(sCtrl, sName), '%s.selector' %sChoiceB)

		for sSpace in dDrivers.keys():
			sDriver = dDrivers[sSpace]['sOutput']
			iIndex = dDrivers[sSpace]['iIndex']
			if bMaintainOffset:
				oNameDriver = naming.oName(sDriver)
				oNameDriver.sType = 'grp'
				oNameDriver.sPart = '%s%sConstraint' %(oNameDriver.sPart, sType.title())
				sConstraintGrp = oNameDriver.sName
				if not cmds.objExists(sConstraintGrp):
					sConstraintGrp = transforms.createTransformNode(sConstraintGrp, sParent = sDriver)
					transforms.transformSnap([sDriver, sConstraintGrp], sType = 'all')
					cmds.setAttr('%s.v' %sConstraintGrp, 0)
					attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sConstraintGrp)
				sNullOffset = naming.oName(sType = 'null', sSide = oNameDriven.sSide, sPart = '%s%sConstraintOffset'%(oNameDriven.sPart,sType.title()), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
				sNull = naming.oName(sType = 'null', sSide = oNameDriven.sSide, sPart = '%s%sConstraint'%(oNameDriven.sPart,sType.title()), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
				iRotateOrder = cmds.getAttr('%s.ro' %sDriven)
				sNullOffset = transforms.createTransformNode(sNullOffset, sParent = sConstraintGrp, iRotateOrder = iRotateOrder)
				sNull = transforms.createTransformNode(sNull, sParent = sNullOffset, iRotateOrder = iRotateOrder)
				transforms.transformSnap([sDriven, sNullOffset], sType = 'all')
				attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sNullOffset)
				attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sNull)
				sDriver = sNull
			cmds.connectAttr('%s.%s' %(sDriver, sAttr_s), '%s.input[%d]' %(sChoiceA, iIndex))
			cmds.connectAttr('%s.%s' %(sDriver, sAttr_s), '%s.input[%d]' %(sChoiceB, iIndex))

	if lDefaultVal:
		cmds.setAttr('%s.%sModeA' %(sCtrl, sName), lDefaultVal[0])
		cmds.setAttr('%s.%sModeB' %(sCtrl, sName), lDefaultVal[1])

def matrixConnect(sDrvNode, lDrivenNodes, sDrvAttr, lSkipTranslate = [], lSkipRotate = [], lSkipScale = [], bForce = True):
	oName = naming.oName(sDrvNode)
	oName.sType = 'decomposeMatrix'
	sDecomposeMatrix = oName.sName
	if not cmds.objExists(sDecomposeMatrix):
		sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = oName.sName)
		cmds.connectAttr('%s.%s' %(sDrvNode, sDrvAttr), '%s.inputMatrix' %sDecomposeMatrix)
	if len(lSkipRotate) < 3:
		oName.sType = 'quatToEuler'
		sQuatToEuler = oName.sName
		if not cmds.objExists(sQuatToEuler):
			sQuatToEuler = cmds.createNode('quatToEuler', name = oName.sName)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrix, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %lDrivenNodes[0], '%s.inputRotateOrder' %sQuatToEuler)
		if len(lDrivenNodes) > 1:
			for sDriven in lDrivenNodes[1:]:
				cmds.connectAttr('%s.ro' %lDrivenNodes[0], '%s.ro' %sDriven)

	## connect matrix
	for sDriven in lDrivenNodes:
		for sAxis in ['X', 'Y', 'Z']:
			if sAxis not in lSkipTranslate:
				attributes.connectAttrs(['%s.outputTranslate%s' %(sDecomposeMatrix, sAxis)], ['%s.translate%s' %(sDriven, sAxis)], bForce = bForce)
			if sAxis not in lSkipRotate:
				attributes.connectAttrs(['%s.outputRotate%s' %(sQuatToEuler, sAxis)], ['%s.rotate%s' %(sDriven, sAxis)], bForce = bForce)
			if sAxis not in lSkipScale:
				attributes.connectAttrs(['%s.outputScale%s' %(sDecomposeMatrix, sAxis)], ['%s.scale%s' %(sDriven, sAxis)], bForce = bForce)
	attributes.connectAttrs(['%s.outputShear' %sDecomposeMatrix], ['%s.shear' %sDriven], bForce = bForce)

def matrixConnectJnt(sDrvNode, sDrivenJnt, sDrvAttr, lSkipTranslate = [], lSkipRotate = [], lSkipScale = [], bForce = True):
	oName = naming.oName(sDrvNode)
	oName.sType = 'decomposeMatrix'
	sDecomposeMatrix = oName.sName
	sDecomposeMatrixRotScale = None
	if not cmds.objExists(sDecomposeMatrix):
		sDecomposeMatrix = cmds.createNode('decomposeMatrix', name = oName.sName)
		cmds.connectAttr('%s.%s' %(sDrvNode, sDrvAttr), '%s.inputMatrix' %sDecomposeMatrix)
	if len(lSkipRotate) < 3 or len(lSkipScale) < 3:
		oNameDriven = naming.oName(sDrivenJnt)
		sMultMatrix = naming.oName(sType = 'multMatrix', sSide = oNameDriven.sSide, sPart = '%sMatrixRotScale' %oNameDriven.sPart, iIndex = oNameDriven.iIndex).sName
		cmds.createNode('multMatrix', name = sMultMatrix)
		cmds.connectAttr('%s.%s' %(sDrvNode, sDrvAttr), '%s.matrixIn[0]' %sMultMatrix)
		fOrientX = cmds.getAttr('%s.jointOrientX' %sDrivenJnt)
		fOrientY = cmds.getAttr('%s.jointOrientY' %sDrivenJnt)
		fOrientZ = cmds.getAttr('%s.jointOrientZ' %sDrivenJnt)
		mMatrix = apiUtils.createMMatrixFromTransformInfo(lRotate = [fOrientX, fOrientY, fOrientZ])
		lMatrixInverse = apiUtils.convertMMatrixToList(mMatrix.inverse())
		cmds.setAttr('%s.matrixIn[1]' %sMultMatrix, lMatrixInverse, type = 'matrix')
		sDecomposeMatrixRotScale = naming.oName(sType = 'decomposeMatrix', sSide = oNameDriven.sSide, sPart = '%sRotScale' %oNameDriven.sPart, iIndex = oNameDriven.iIndex).sName
		cmds.createNode('decomposeMatrix', name = sDecomposeMatrixRotScale)
		cmds.connectAttr('%s.matrixSum' %sMultMatrix, '%s.inputMatrix' %sDecomposeMatrixRotScale)
		if len(lSkipRotate) < 3:
			sQuatToEuler = naming.oName(sType = 'quatToEuler', sSide = oNameDriven.sSide, sPart = '%sRot' %oNameDriven.sPart, iIndex = oNameDriven.iIndex).sName
			cmds.createNode('quatToEuler', name = sQuatToEuler)
			cmds.connectAttr('%s.outputQuat' %sDecomposeMatrixRotScale, '%s.inputQuat' %sQuatToEuler)
			cmds.connectAttr('%s.ro' %sDrivenJnt, '%s.inputRotateOrder' %sQuatToEuler)

	## connect matrix
	for sAxis in ['X', 'Y', 'Z']:
		if sAxis not in lSkipTranslate:
			attributes.connectAttrs(['%s.outputTranslate%s' %(sDecomposeMatrix, sAxis)], ['%s.translate%s' %(sDrivenJnt, sAxis)], bForce = bForce)
		if sAxis not in lSkipRotate:
			attributes.connectAttrs(['%s.outputRotate%s' %(sQuatToEuler, sAxis)], ['%s.rotate%s' %(sDrivenJnt, sAxis)], bForce = bForce)
		if sAxis not in lSkipScale:
			attributes.connectAttrs(['%s.outputScale%s' %(sDecomposeMatrixRotScale, sAxis)], ['%s.scale%s' %(sDrivenJnt, sAxis)], bForce = bForce)
	if sDecomposeMatrixRotScale:
		attributes.connectAttrs(['%s.outputShear' %sDecomposeMatrixRotScale], ['%s.shear' %sDrivenJnt], bForce = bForce)
	else:
		attributes.connectAttrs(['%s.outputShear' %sDecomposeMatrix], ['%s.shear' %sDrivenJnt], bForce = bForce)

def getWeightAliasList(sConstraint):
	sConstraintType = cmds.objectType(sConstraint)
	if sConstraintType == 'pointConstraint':
		lWeightAliasList = cmds.pointConstraint(sConstraint, q = True, wal = True)
	elif sConstraintType == 'orientConstraint':
		lWeightAliasList = cmds.orientConstraint(sConstraint, q = True, wal = True)
	elif sConstraintType == 'scaleConstraint':
		lWeightAliasList = cmds.scaleConstraint(sConstraint, q = True, wal = True)
	elif sConstraintType == 'parentConstraint':
		lWeightAliasList = cmds.parentConstraint(sConstraint, q = True, wal = True)
	return lWeightAliasList
## sub functions
def __constraint(lDrivers, sDriven, bMaintainOffset = False, lSkipTranslate = None, lSkipRotate = None, lSkipScale = None, bForce = False, sType = 'parent'):
	lConnections = []
	lLocks = []
	lReturn = []

	if sType == 'parent':
		lAttrConnect = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 't', 'r']
	elif sType == 'point':
		lAttrConnect = ['tx', 'ty', 'tz', 't']
	elif sType == 'orient':
		lAttrConnect = ['rx', 'ry', 'rz', 'r']
	elif sType == 'scale':
		lAttrConnect = ['sx', 'sy', 'sz', 's']
	elif sType == 'all':
		lAttrConnect = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 't', 'r', 's']
	for sAttr in lAttrConnect:
		lConnectionsAttr = cmds.listConnections('%s.%s'%(sDriven, sAttr), s = True, scn = True, p = True)
		if lConnectionsAttr:
			for sConnection in lConnectionsAttr:
				lConnections.append([sConnection, sAttr])
		bLock = cmds.getAttr('%s.%s'%(sDriven, sAttr), lock = True)
		if bLock:
			lLocks.append(sAttr)

	bConstraint = True

	if not bForce:
		if lConnections or lLocks:
			cmds.warning('%s already has input connections, skipped' %sDriven)
			bConstraint = False
			lReturn = None

	if bConstraint:
		for lConnectionAttr in lConnections:
			cmds.disconnectAttr('%s.%s' %(sDriven, lConnectionAttr[1]), lConnectionAttr[0])
		for sLockAttr in lLocks:
			cmds.setAttr('%s.%s' %(sDriven, sLockAttr), lock = False)
		if bMaintainOffset:
			oNameDriven = naming.oName(sDriven)
			lNulls = []
			for i, sDriver in enumerate(lDrivers):
				oNameDriver = naming.oName(sDriver)
				oNameDriver.sType = 'grp'
				oNameDriver.sPart = '%s%sConstraint' %(oNameDriver.sPart, sType.title())
				sConstraintGrp = oNameDriver.sName
				if not cmds.objExists(sConstraintGrp):
					sConstraintGrp = transforms.createTransformNode(sConstraintGrp, sParent = sDriver)
					transforms.transformSnap([sDriver, sConstraintGrp], sType = 'all')
					cmds.setAttr('%s.v' %sConstraintGrp, 0)
					attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sConstraintGrp)
				sNullOffset = naming.oName(sType = 'null', sSide = oNameDriven.sSide, sPart = '%s%sConstraintOffsetW%d'%(oNameDriven.sPart,sType.title(), i), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
				sNull = naming.oName(sType = 'null', sSide = oNameDriven.sSide, sPart = '%s%sConstraintW%d'%(oNameDriven.sPart,sType.title(), i), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
				iRotateOrder = cmds.getAttr('%s.ro' %sDriven)
				sNullOffset = transforms.createTransformNode(sNullOffset, sParent = sConstraintGrp, iRotateOrder = iRotateOrder)
				sNull = transforms.createTransformNode(sNull, sParent = sNullOffset, iRotateOrder = iRotateOrder)
				transforms.transformSnap([sDriven, sNullOffset], sType = 'all')
				attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sNullOffset)
				attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sNull)
				lNulls.append(sNull)
			lConstraints = lNulls
		else:
			lConstraints = lDrivers
		if sType == 'parent':
			sConstraint = cmds.parentConstraint(lConstraints, sDriven, mo = False, st = lSkipTranslate, sr = lSkipRotate)[0]
			cmds.setAttr('%s.interpType' %sConstraint, 2)
			lReturn.append(sConstraint)
		elif sType == 'point':
			sConstraint = cmds.pointConstraint(lConstraints, sDriven, mo = False, sk = lSkipTranslate)[0]
			lReturn.append(sConstraint)
		elif sType == 'orient':
			sConstraint = cmds.orientConstraint(lConstraints, sDriven, mo = False, sk = lSkipRotate)[0]
			cmds.setAttr('%s.interpType' %sConstraint, 2)
			lReturn.append(sConstraint)
		elif sType == 'scale':
			sConstraint = cmds.scaleConstraint(lConstraints, sDriven, mo = False, sk = lSkipScale)[0]
			lReturn.append(sConstraint)
		elif sType == 'all':
			sConstraint = cmds.parentConstraint(lConstraints, sDriven, mo = False, st = lSkipTranslate, sr = lSkipRotate)[0]
			cmds.setAttr('%s.interpType' %sConstraint, 2)
			lReturn.append(sConstraint)
			sConstraint = cmds.scaleConstraint(lConstraints, sDriven, mo = False, sk = lSkipScale)[0]
			lReturn.append(sConstraint)

		bConstraintInfo = cmds.attributeQuery('%sConstraints' %sType, node = sDriven, exists = True)
		if not bConstraintInfo:
			cmds.addAttr(sDriven, ln = '%sConstraints' %sType, dt = 'string')
		sConstraintInfo = ''
		for sDriver in lDrivers:
			sConstraintInfo += '%s,'%sDriver
		cmds.setAttr('%s.%sConstraints' %(sDriven, sType), lock = False)
		cmds.setAttr('%s.%sConstraints' %(sDriven, sType), sConstraintInfo, type = 'string', lock = True)

		for sLockAttr in lLocks:
			cmds.setAttr('%s.%s' %(sDriven, sLockAttr), lock = True)
	return lReturn		

