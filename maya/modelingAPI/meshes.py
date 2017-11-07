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
	mFnMesh = __setMFnMesh(sMesh)
	iVtxCount = mFnMesh.numVertices()
	return iVtxCount

def getMeshVtxPntArray(sMesh):
	mFnMesh = __setMFnMesh(sMesh)
	mVtxPntArray = OpenMaya.MPointArray()
	mFnMesh.getPoints(mVtxPntArray, OpenMaya.MSpace.kObject)
	return mVtxPntArray

def remapVtxIdToMesh(sTargetMesh, sBaseMesh = None, lVtxPosBase = None, fTolerance = 0.00001):
	lComponents = []
	mVtxPntArrayTargt = getMeshVtxPntArray(sTargetMesh)
	if not lVtxPosBase:
		mVtxPntArrayBase = getMeshVtxPntArray(sBaseMesh)
		lVtxPosBase = apiUtils.convertMPointArrayToList(mVtxPntArrayBase)

	for i in range(mVtxPntArrayTargt.length()):
		fPntX = mVtxPntArrayTargt[i].x
		fPntY = mVtxPntArrayTargt[i].y
		fPntZ = mVtxPntArrayTargt[i].z

		for j, lPntBase in enumerate(lVtxPosBase):
			bPntX = (lPntBase[0] >= fPntX - fTolerance and lPntBase[0] <= fPntX + fTolerance)
			bPntY = (lPntBase[1] >= fPntY - fTolerance and lPntBase[1] <= fPntY + fTolerance)
			bPntZ = (lPntBase[2] >= fPntZ - fTolerance and lPntBase[2] <= fPntZ + fTolerance)
			if bPntX and bPntY and bPntZ:
				lComponents.append(j)
				break
	return lComponents

def getMeshesFromGrp(sGrp):
	lMeshes = []
	lChilds = cmds.listRelatives(sGrp, c = True, ad = True, type = 'mesh')
	if lChilds:
		for sChild in lChilds:
			sNode = cmds.listRelatives(sChild, p = True)[0]
			if sNode not in lMeshes:
				lMeshes.append(sNode)
	return lMeshes

def getClosestPointOnMesh(lPos, sMesh):
	mFnMesh = __setMFnMesh(sMesh)
	mPoint = apiUtils.setMPoint(lPos)

	mPointClst = OpenMaya.MPoint()
	id_util = OpenMaya.MScriptUtil()
	id_util.createFromInt(0)
	id_param = id_util.asIntPtr()

	mFnMesh.getClosestPoint(mPoint, mPointClst, OpenMaya.MSpace.kWorld, id_param)

	uv_util = OpenMaya.MScriptUtil()
	uv_util.createFromList([0.0, 0.0], 2)
	uv_param = uv_util.asFloat2Ptr()

	sUvSetCurrent = cmds.polyUVSet(sMesh, q = True, cuv = True)[0]
	mFnMesh.getUVAtPoint(mPointClst, uv_param, OpenMaya.MSpace.kWorld, sUvSetCurrent, id_param)

	fVal_u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_param, 0, 0)
	fVal_v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_param, 0, 1)
	
	return (mPointClst[0], mPointClst[1], mPointClst[2]), [fVal_u, fVal_v]




#### Sub Functions
def __setMFnMesh(sMesh):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	mFnMesh = OpenMaya.MFnMesh(mDagPath)
	return mFnMesh