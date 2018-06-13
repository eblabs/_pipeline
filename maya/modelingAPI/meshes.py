## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

## libs Import
import common.apiUtils as apiUtils
import common.debug as debug
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

def getMeshVtxPntArray(sMesh, sSpace = 'object'):
	mFnMesh = __setMFnMesh(sMesh)
	mVtxPntArray = OpenMaya.MPointArray()
	if sSpace == 'object':
		mSpace = OpenMaya.MSpace.kObject
	elif sSpace == 'world':
		mSpace = OpenMaya.MSpace.kWorld 
	mFnMesh.getPoints(mVtxPntArray, mSpace)
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

def getClosestVtxInMesh(sMesh, lPos = None, mPoint = None, sSpace = 'object'):
	mFnMesh = __setMFnMesh(sMesh)
	if not mPoint:
		mPoint = apiUtils.setMPoint(lPos)
	mPointArray = getMeshVtxPntArray(sMesh, sSpace = sSpace)

	mPointClst = OpenMaya.MPoint()
	id_util = OpenMaya.MScriptUtil()
	id_util.createFromInt(0)
	id_param = id_util.asIntPtr()

	if sSpace == 'object':
		mSpace = OpenMaya.MSpace.kObject
	elif sSpace == 'world':
		mSpace = OpenMaya.MSpace.kWorld

	mFnMesh.getClosestPoint(mPoint, mPointClst, mSpace, id_param)

	iFace = OpenMaya.MScriptUtil.getInt(id_param)

	mIntArray = OpenMaya.MIntArray()

	mFnMesh.getPolygonVertices(iFace, mIntArray)

	fDisMin = None
	iVtxClst = 0
	for i in range(mIntArray.length()):
		iVtx = mIntArray[i]
		fDis = mPointArray[iVtx].distanceTo(mPoint)
		if fDisMin == None:
			fDisMin = fDis
			iVtxClst = iVtx
		elif fDis < fDisMin:
			fDisMin = fDis
			iVtxClst = iVtx

	return iVtxClst, mPointArray[iVtxClst], fDisMin

def symEdit(sMesh, sBaseMesh = None, sAxis = 'YZ', iDirection = 1, fTolerance = 0.00001, sSpace = 'object', lBaseMeshInfo = None):
	if lBaseMeshInfo:
		bSymmetrical = lBaseMeshInfo[0]
		lPnts_source = lBaseMeshInfo[1][0]
		lPnts_target = lBaseMeshInfo[1][1]
		lPnts_middle = lBaseMeshInfo[1][2]
	else:
		bSymmetrical, [lPnts_source, lPnts_target, lPnts_middle] = symCheck(sBaseMesh, sAxis = sAxis, iDirection = iDirection, fTolerance = fTolerance, sSpace = sSpace)

	if bSymmetrical:
		if sSpace == 'object':
			mSpace = OpenMaya.MSpace.kObject
		elif sSpace == 'world':
			mSpace = OpenMaya.MSpace.kWorld

		mVtxPntArray = getMeshVtxPntArray(sMesh, sSpace = sSpace)
		mFnMesh = __setMFnMesh(sMesh)

		for i, iVtx in enumerate(lPnts_source):
			print 'symmetrical mirror side %f' %((i + 1)/float(len(lPnts_source)))
			mPnt = mVtxPntArray[iVtx]
			iVtx_mirror = lPnts_target[i]
			if sAxis == 'YZ':
				mVtxPntArray[iVtx_mirror].x = -mPnt.x
				mVtxPntArray[iVtx_mirror].y = mPnt.y
				mVtxPntArray[iVtx_mirror].z = mPnt.z
			elif sAxis == 'XZ':
				mVtxPntArray[iVtx_mirror].x = mPnt.x
				mVtxPntArray[iVtx_mirror].y = -mPnt.y
				mVtxPntArray[iVtx_mirror].z = mPnt.z
			else:
				mVtxPntArray[iVtx_mirror].x = mPnt.x
				mVtxPntArray[iVtx_mirror].y = mPnt.y
				mVtxPntArray[iVtx_mirror].z = -mPnt.z
		for i, iVtx in enumerate(lPnts_middle):
			print 'symmetrical mirror middle %f' %((i + 1)/float(len(lPnts_middle)))
			mPnt = mVtxPntArray[iVtx]
			if sAxis == 'YZ':
				mVtxPntArray[iVtx_mirror].x = 0
				mVtxPntArray[iVtx_mirror].y = mPnt.y
				mVtxPntArray[iVtx_mirror].z = mPnt.z
			elif sAxis == 'XZ':
				mVtxPntArray[iVtx_mirror].x = mPnt.x
				mVtxPntArray[iVtx_mirror].y = 0
				mVtxPntArray[iVtx_mirror].z = mPnt.z
			else:
				mVtxPntArray[iVtx_mirror].x = mPnt.x
				mVtxPntArray[iVtx_mirror].y = mPnt.y
				mVtxPntArray[iVtx_mirror].z = 0

		mFnMesh.setPoints(mVtxPntArray, mSpace)
		print '%s symmetrical mirrored' %sMesh
	else:
		print '%s is not symmetrical, skipped' %sMesh

def symCheck(sMesh, sAxis = 'YZ', iDirection = 1, fTolerance = 0.00001, sSpace = 'object'):
	mVtxPntArray = getMeshVtxPntArray(sMesh, sSpace = sSpace)

	lPnts_source = []
	lPnts_middle = []
	lPnts_target = []
	lPnts_temp = []
	bSymmetrical = True

	iLength = mVtxPntArray.length()
	for i in range(iLength):

		print 'initialize mesh %f' %((i+1)/float(iLength))

		if sAxis == 'YZ':
			fAxis = mVtxPntArray[i].x
		elif sAxis == 'XZ':
			fAxis = mVtxPntArray[i].y
		else:
			fAxis = mVtxPntArray[i].z

		if fAxis <= fTolerance and fAxis >= -fTolerance:
			lPnts_middle.append(i)
		elif iDirection == 1:
			if fAxis > 0:
				lPnts_source.append(i)
			else:
				lPnts_temp.append(i)
		elif iDirection == -1:
			if fAxis < 0:
				lPnts_source.append(i)
			else:
				lPnts_temp.append(i)

	if len(lPnts_source) != len(lPnts_temp):
		bSymmetrical = False
	else:
		iLength_remap = len(lPnts_source)
		for i, iVtx in enumerate(lPnts_source):

			print'remap mesh vtx %f' %((i+1)/float(iLength_remap))

			mPnt = mVtxPntArray[iVtx]

			if sAxis == 'YZ':
				mPnt_mirror = apiUtils.setMPoint([-mPnt.x, mPnt.y, mPnt.z])
			elif sAxis == 'XZ':
				mPnt_mirror = apiUtils.setMPoint([mPnt.x, -mPnt.y, mPnt.z])
			else:
				mPnt_mirror = apiUtils.setMPoint([mPnt.x, mPnt.y, -mPnt.z])

			bSymmetrical_pnt = False
			iVtxClst, mPntClst, fDisClst = getClosestVtxInMesh(sMesh, mPoint = mPnt_mirror, sSpace = sSpace)

			if fDisClst >= -fTolerance and fDisClst <= fTolerance:
				lPnts_target.append(iVtxClst)
				lPnts_temp.remove(iVtxClst)
			else:
				bSymmetrical = False
				break
		if lPnts_temp:
			bSymmetrical = False
		
	if bSymmetrical:
		print '%s is symmetrical' %sMesh
		return bSymmetrical, [lPnts_source, lPnts_target, lPnts_middle]
	else:
		print '%s is not symmetrical' %sMesh
		return bSymmetrical, [None, None, None]

#### Sub Functions
def __setMFnMesh(sMesh):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	mFnMesh = OpenMaya.MFnMesh(mDagPath)
	return mFnMesh
