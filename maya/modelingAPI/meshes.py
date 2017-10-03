## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

## libs Import
import common.apiUtils as apiUtils

#### Functions

def getShape(sNode, bIntermediate = False):
	lShapes = cmds.listRelatives(sNode, s = True, path = True)
	if lShapes:
		if not bIntermediate:
			sShape = lShapes[0]
		else:
			sShape = None
			for sShapeEach in lShapes:
				bIntermediateEach = cmds.getAttr('%s.intermediate' %sShapeEach)
				if bIntermediateEach and cmds.listConnections(sShapeEach, s = False):
					sShape = sShapeEach
	else:
		sShape = None
	return sShape

def removeInermediateShapes(sNode, bIntermediate = False):
	lShapes = cmds.listRelatives(sNode, s = True, path = True)
	if lShapes:
		for sShapeEach in lShapes:
			bIntermediateEach = cmds.getAttr('%s.intermediate' %sShapeEach)
			if bIntermediateEach:
				if not bIntermediate or not cmds.listConnections(sShapeEach, s = False):
					cmds.delete(sShapeEach)

def getPolyVtxCount(sMesh):
	mFnMesh = _setMFnMesh(sMesh)
	iVtxCount = mFnMesh.numVertices()
	return iVtxCount

def getMeshVtxPntArray(sMesh):
	mFnMesh = _setMFnMesh(sMesh)
	mVtxPntArray = OpenMaya.MPointArray()
	mFnMesh.getPoints(mVtxPntArray, OpenMaya.MSpace.kObject)
	return mVtxPntArray


#### Sub Functions
def _setMFnMesh(sMesh):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	mFnMesh = OpenMaya.MFnMesh(mDagPath)
	return mFnMesh