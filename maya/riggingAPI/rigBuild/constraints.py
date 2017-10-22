## External Import
import maya.cmds as cmds
import maya.mel as mel

## lib import
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes

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
	for sAttr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 't', 'r']:
		lConnectionsAttr = cmds.listConnections('%s.%s'%(sDriven, sAttr), s = True, scn = True, p = True)
		if lConnectionsAttr:
			for sConnection in lConnectionsAttr:
				lConnections.append([sConnection, sAttr])
		bLock = cmds.getAttr('%s.%s'%(sDriven, sAttr), lock = True)
		if bLock:
			lLocks.append(sAttr)

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
				sNull = naming.oName(sType = 'null', sSide = oNameDriven.sSide, sPart = '%s%sConstraintW%d'%(oNameDriven.sSide,sType.title(), i), iIndex = oNameDriven.iIndex, iSuffix = oNameDriven.iSuffix).sName
				sNull = transforms.createTransformNode(sNull, sParent = sConstraintGrp)
				transforms.transformSnap([sDriven, sNull], sType = 'all')
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

