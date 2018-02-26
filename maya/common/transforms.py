## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import os
import json
import time

## libs Import
import files
import maths
import attributes
import apiUtils
import namingAPI.naming as naming

#### Functions
def getNodeTransformInfo(sNode):
	lPos = cmds.xform(sNode, q = True, rp = True, ws = True)
	lRot = cmds.xform(sNode, q = True, ro = True, ws = True)
	lScl = cmds.xform(sNode, q = True, s = True, ws = True)
	return [lPos, lRot, lScl]

def getNodesAvgTransformInfo(lNodes, bCenterPivot = False):
	lTransformInfoAvg = []
	for i in range(3):
		lPos = [[],[],[]]
		for sNode in lNodes:
			lTransformInfo = getNodeTransformInfo(sNode)
			for j, lTransformInfoEach in enumerate(lTransformInfo[i]):
				lPos[j].append(lTransformInfoEach)
		lPosAvg = []
		for lPosEach in lPos:
			fPosAvg = maths.getAvgValueFromList(lPosEach)
			lPosAvg.append(fPosAvg)
		lTransformInfoAvg.append(lPosAvg)
	if bCenterPivot:
		lCp, lPos = getNodesPivotFromBoundingBox(lNodes)
		lTransformInfoAvg[0] = lCp
	return lTransformInfoAvg

def getNodesPivotFromBoundingBox(lNodes):
	lPos = [[], []]
	for i in range(3):
		lPosEach = []
		for sNode in lNodes:
			fTransformInfo = getNodeTransformInfo(sNode)[0][i]
			lPosEach.append(fTransformInfo)
		lPos[0].append(max(lPosEach))
		lPos[1].append(min(lPosEach))
	lCp = []
	for i in range(3):
		lCp.append((lPos[0][i] + lPos[1][i])*0.5)
	return lCp, lPos


def setNodeTransform(sNode, lTransformInfo, bTranslate = True, bRotate = True, bScale = True, lSkipTranslate = None, lSkipRotate = None, lSkipScale = None):
	lTransformInfoNode = getNodeTransformInfo(sNode)
	if bTranslate:
		if lSkipTranslate:
			for i, sAxis in enumerate(['x', 'y', 'z']):
				if sAxis in lSkipTranslate:
					lTransformInfo[0][i] = lTransformInfoNode[0][i]
		cmds.xform(sNode, t = lTransformInfo[0], ws = True)
	if bRotate:
		if lSkipRotate:
			for i, sAxis in enumerate(['x', 'y', 'z']):
				if sAxis in lSkipRotate:
					lTransformInfo[1][i] = lTransformInfoNode[1][i]
		cmds.xform(sNode, ro = lTransformInfo[1], ws = True)
	if bScale:
		if lSkipScale:
			for i, sAxis in enumerate(['x', 'y', 'z']):
				if sAxis in lSkipScale:
					lTransformInfo[2][i] = lTransformInfoNode[2][i]
		cmds.xform(sNode, s = lTransformInfo[2], ws = True)

def transformSnap(lNodes, sType = 'parent', sSnapType = 'oneToAll', lSkipTranslate = None, lSkipRotate = None, lSkipScale = None, bCenterPivot = True):
	if sSnapType == 'oneToAll':
		sDriver = lNodes[0]
		lDriven = lNodes[1:]
		lTransformInfoDriver = getNodeTransformInfo(sDriver)
		for sDriven in lDriven:
			if sType == 'parent':
				transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate)
			elif sType == 'point':
				transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate)
			elif sType == 'orient':
				transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = lSkipRotate)
			elif sType == 'scale':
				transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = lSkipScale)
			elif sType == 'all':
				transformSnapAll(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale)
	elif sSnapType == 'allToOne':
		lDrivers = lNodes[:-1]
		sDriven = lNodes[-1]
		lTransformInfoDriver = getNodesAvgTransformInfo(lDrivers, bCenterPivot = bCenterPivot)
		if sType == 'parent':
			transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate)
		elif sType == 'point':
			transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate)
		elif sType == 'orient':
			transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = lSkipRotate)
		elif sType == 'scale':
			transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = lSkipScale)
		elif sType == 'all':
			transformSnapAll(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale)


def createTransformNode(sName, lLockHideAttrs = [], sParent = None, iRotateOrder = 0, bVis = True, sPos = None, bInheritsTransform = True):
	cmds.group(empty  = True, name = sName)
	cmds.setAttr('%s.ro' %sName, iRotateOrder)
	cmds.setAttr('%s.v' %sName, bVis)
	cmds.setAttr('%s.inheritsTransform' %sName, bInheritsTransform)
	if sPos:
		transformSnap([sPos, sName], sType = 'all')
	if sParent and cmds.objExists(sParent):
		cmds.parent(sName, sParent)
	attributes.lockHideAttrs(lLockHideAttrs, sNode = sName)
	return sName

def createTransformMatcherNode(sNode, sParent = None, bInheritsTransform = True):
	oName = naming.oName(sNode)
	sOffset = naming.oName(sType = 'grp', sSide = oName.sSide, sPart = '%sMatcher' %oName.sPart, iIndex = oName.iIndex, iSuffix = oName.iSuffix).sName
	sMatcher = naming.oName(sType = 'null', sSide = oName.sSide, sPart = '%sMatcher' %oName.sPart, iIndex = oName.iIndex, iSuffix = oName.iSuffix).sName
	iRotateOrder = cmds.getAttr('%s.ro' %sNode)
	sOffset = createTransformNode(sOffset, sParent = sParent, iRotateOrder = iRotateOrder)
	transformSnap([sNode, sOffset], sType = 'all')
	attributes.lockHideAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sNode = sOffset)
	sMatcher = createTransformNode(sMatcher, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sOffset, sPos = sOffset, iRotateOrder = iRotateOrder, bInheritsTransform = bInheritsTransform)
	return sMatcher, sOffset

def worldOrientTransform(sNode, sFoward = 'z', sUp = 'y'):
	lTranslate = cmds.xform(sNode, q = True, t = True, ws = True)

	if sFoward.lower() == 'x':
		lFoward = [1,0,0]
	elif sFoward.lower() == 'y':
		lFoward = [0,1,0]
	else:
		lFoward = [0,0,1]

	if sUp.lower() == 'x':
		lUp = [1,0,0]
	elif sUp.lower() == 'y':
		lUp = [0,1,0]
	else:
		lUp = [0,0,1]

	sLocFoward = cmds.spaceLocator()[0]
	sLocUp = cmds.spaceLocator()[0]
	cmds.xform(sLocFoward, t = [lTranslate[0], lTranslate[1], lTranslate[2] + 10], ws = True)
	cmds.xform(sLocUp, t = [lTranslate[0], lTranslate[1] + 10, lTranslate[2]], ws = True)

	cmds.delete(cmds.aimConstraint(sLocFoward, sNode, aimVector = lFoward, upVector = lUp, worldUpType = 'object', worldUpObject = sLocUp, mo = False))
	cmds.delete(sLocUp, sLocFoward)

def getBoundingBoxInfo(sNode):
	lBBoxMin = cmds.getAttr('%s.boundingBoxMin' %sNode)[0]
	lBBoxMax = cmds.getAttr('%s.boundingBoxMax' %sNode)[0]

	fWidth = lBBoxMax[0] - lBBoxMin[0]
	fHeight = lBBoxMax[1] - lBBoxMin[1]
	fDepth = lBBoxMax[2] - lBBoxMin[2]

	return fWidth, fHeight, fDepth

def convertPointTransformFromObjectToWorld(lTranslate, sParent):
	mMatrixPnt = apiUtils.createMMatrixFromTransformInfo(lTranslate = lTranslate)
	mMatrixParent = apiUtils.createMMatrixFromTransformNode(sParent, sSpace = 'world')
	mMatrixPntWorld = mMatrixPnt * mMatrixParent
	lTransformInfo = apiUtils.decomposeMMatrix(mMatrixPntWorld)
	return lTransformInfo[0]

def convertPointTransformFromWorldToObject(lTranslate, sParent):
	mMatrixPnt = apiUtils.createMMatrixFromTransformInfo(lTranslate = lTranslate)
	mMatrixParent = apiUtils.createMMatrixFromTransformNode(sParent, sSpace = 'world')
	mMatrixPntWorld = mMatrixPnt * mMatrixParent.inverse()
	lTransformInfo = apiUtils.decomposeMMatrix(mMatrixPntWorld)
	return lTransformInfo[0]

#### Sub Functions
def transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = None):
	lPos = lTransformInfoDriver[0]

	lTransformInfoDriven = getNodeTransformInfo(sDriven)
	if lSkipTranslate:
		for i, sAxis in enumerate(['x', 'y', 'z']):
			if sAxis in lSkipTranslate:
				lPos[i] = lTransformInfoDriven[0][i]

	cmds.xform(sDriven, t = lPos, ws = True)

def transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = None):
	lRot = lTransformInfoDriver[1]

	lTransformInfoDriven = getNodeTransformInfo(sDriven)
	if lSkipRotate:
		for i, sAxis in enumerate(['x', 'y', 'z']):
			if sAxis in lSkipRotate:
				lRot[i] = lTransformInfoDriven[1][i]

	cmds.xform(sDriven, ro = lRot, ws = True)

def transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = None):
	lScl = lTransformInfoDriver[2]

	lTransformInfoDriven = getNodeTransformInfo(sDriven)
	if lSkipScale:
		for i, sAxis in enumerate(['x', 'y', 'z']):
			if sAxis in lSkipScale:
				lScl[i] = lTransformInfoDriven[2][i]

	cmds.xform(sDriven, s = lScl, ws = True)

def transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = None, lSkipRotate = None):
	transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate)
	transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = lSkipRotate)

def transformSnapAll(lTransformInfoDriver, sDriven, lSkipTranslate = None, lSkipRotate = None, lSkipScale = None):
	transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate)
	transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = lSkipScale)


