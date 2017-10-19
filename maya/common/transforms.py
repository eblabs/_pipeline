## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import files
import maths
import attributes

#### Functions
def getNodeTransformInfo(sNode):
	lPos = cmds.xform(sNode, q = True, t = True, ws = True)
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
				lPos[j].append(lTransformInfoEach[j])
		lPosAvg = []
		for j, lPosEach in lPos:
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
			iPosEach.append(fTransformInfo)
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


def createTransformNode(sName, lLockHideAttrs = [], sParent = None):
	cmds.group(empty  = True, name = sName)
	attributes.lockHideAttrs(lLockHideAttrs, sNode = sName)
	if sParent:
		cmds.parent(sName, sParent)
	return sName


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


