## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import files

#### Functions
def getNodeTransformInfo(sNode):
	lPos = cmds.xform(sNode, q = True, t = True, ws = True)
	lRot = cmds.xform(sNode, q = True, ro = True, ws = True)
	lScl = cmds.xform(sNode, q = True, s = True, ws = True)
	return [lPos, lRot, lScl]

def getNodesAvgTransformInfo(lNodes):
	lTransformInfoAvg = [[0,0,0], [0,0,0], [0,0,0]]
	for sNode in lNodes:
		lTransformInfo = getNodeTransformInfo(sNode)
		for i in range(0,3):
			for j in range(0,3):
				lTransformInfoAvg[i][j] += lTransformInfo[i][j]
	return lTransformInfoAvg

def setNodeTransform(sNode, lTransformInfo, bTranslate = True, bRotate = True, bScale = True, lSkipTranslate = None, lSkipRotate = None, lSkipScale = None):
	lTransformInfoNode = getNodeTransformInfo(sNode)
	if bTranslate:
		if lSkipTranslate:
			for i, sAxis in enumerate(['x', 'y', 'z']):
				if sAxis in lSkipTranslate:
					lTransformInf[0][i] = lTransformInfoNode[0][i]
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

def transformSnap(lNodes, sType = 'parent', sSnapType = 'oneToAll', lSkipTranslate = None, lSkipRotate = None, lSkipScale = None):
	if sSnapType == 'oneToAll':
		sDriver = lNodes[0]
		lDriven = lNodes[1:]
		lTransformInfoDriver = getNodeTransformInfo(sDriver)
		for sDriven in lDriven:
			if sType == 'parent':
				_transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate)
			elif sType == 'point':
				_transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate)
			elif sType == 'orient':
				_transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = lSkipRotate)
			elif sType == 'scale':
				_transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = lSkipScale)
			elif sType == 'all':
				_transformSnapAll(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale)
	elif sSnapType == 'allToOne':
		lDrivers = lNodes[:-1]
		sDriven = lNodes[-1]
		lTransformInfoDriver = getNodesAvgTransformInfo(lDrivers)
		if sType == 'parent':
			_transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate)
		elif sType == 'point':
			_transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate)
		elif sType == 'orient':
			_transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = lSkipRotate)
		elif sType == 'scale':
			_transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = lSkipScale)
		elif sType == 'all':
			_transformSnapAll(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate, lSkipScale = lSkipScale)




def getNodeParent(sNode):
	sParent = cmds.listRelatives(sNode, p = True)
	if sParent:
		sParent = sParent[0]
	else:
		sParent = None
	return sParent

def getNodesHierarchy(lNodes):
	dHierarchy = {}
	for sNode in lNodes:
		sParent = getNodeParent(sNode)
		dNodeParent = {sNode: sParent}
		dHierarchy.update(dNodeParent)
	return dHierarchy

def saveNodesHierarchy(lNodes, sPath):
	dHierarchy = getNodesHierarchy(lNodes)
	files.writeJsonFile(sPath, dHierarchy)

def loadNodesHierarchy(sPath):
	dHierarchy = files.readJsonFile(sPath)
	for sNode in dHierarchy.keys():
		if cmds.objExists(sNode):
			sParent = dHierarchy[sNode]
			if sParent:
				if cmds.objExists(sParent):
					sParentOrig = cmds.listRelatives(sNode, p = True)
					if not sParentOrig or sParent not in sParentOrig:
						cmds.parent(sNode, sParent)



#### Sub Functions
def _transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = None):
	lPos = lTransformInfoDriver[0]

	lTransformInfoDriven = getNodeTransformInfo(sDriven)
	if lSkipTranslate:
		for i, sAxis in enumerate(['x', 'y', 'z']):
			if sAxis in lSkipTranslate:
				lPos[i] = lTransformInfoDriven[0][i]

	cmds.xform(sDriven, t = lPos, ws = True)

def _transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = None):
	lRot = lTransformInfoDriver[1]

	lTransformInfoDriven = getNodeTransformInfo(sDriven)
	if lSkipRotate:
		for i, sAxis in enumerate(['x', 'y', 'z']):
			if sAxis in lSkipRotate:
				lRot[i] = lTransformInfoDriven[1][i]

	cmds.xform(sDriven, ro = lRot, ws = True)

def _transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = None):
	lScl = lTransformInfoDriver[2]

	lTransformInfoDriven = getNodeTransformInfo(sDriven)
	if lSkipScale:
		for i, sAxis in enumerate(['x', 'y', 'z']):
			if sAxis in lSkipScale:
				lScl[i] = lTransformInfoDriven[2][i]

	cmds.xform(sDriven, s = lScl, ws = True)

def _transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = None, lSkipRotate = None):
	_transformSnapPoint(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate)
	_transformSnapOrient(lTransformInfoDriver, sDriven, lSkipRotate = lSkipRotate)

def _transformSnapAll(lTransformInfoDriver, sDriven, lSkipTranslate = None, lSkipRotate = None, lSkipScale = None):
	_transformSnapParent(lTransformInfoDriver, sDriven, lSkipTranslate = lSkipTranslate, lSkipRotate = lSkipRotate)
	_transformSnapScale(lTransformInfoDriver, sDriven, lSkipScale = lSkipScale)


