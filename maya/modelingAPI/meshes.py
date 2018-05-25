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

def getClosestVtxInMesh(lPos, sMesh):
	mFnMesh = __setMFnMesh(sMesh)
	mPoint = apiUtils.setMPoint(lPos)
	mPointArray = getMeshVtxPntArray(sMesh)

	mPointClst = OpenMaya.MPoint()
	id_util = OpenMaya.MScriptUtil()
	id_util.createFromInt(0)
	id_param = id_util.asIntPtr()

	mFnMesh.getClosestPoint(mPoint, mPointClst, OpenMaya.MSpace.kWorld, id_param)

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

	return iVtxClst, [mPointArray[iVtxClst].x, mPointArray[iVtxClst].y, mPointArray[iVtxClst].z], fDisMin




def meshSymmetrical(sMesh, sBaseMesh, sAxis = 'YZ', iDirection = 1, fTolerance = 0.00001, sSymmtrical = 'world', bMirrorMesh = True, bCheck = False):
	if sSymmtrical == 'world' or sSymmtrical == 'object':
		bSymmetrical, lPnts_source, lPnts_target, lPnts_middle = __meshVtxSymRemap(sBaseMesh, sAxis = sAxis, iDirection = iDirection, fTolerance = fTolerance, sSpace = sSymmtrical)
	else:
		pass

	if sSymmtrical == 'world':
		sSpace = 'world'
		mSpace = OpenMaya.MSpace.kWorld 
	else:
		sSpace = 'object'
		mSpace = OpenMaya.MSpace.kObject
		
	lPnts_nonSym = []
	mVtxPntArray = getMeshVtxPntArray(sMesh, sSpace = sSpace)
	mFnMesh = __setMFnMesh(sMesh)
	iLength_sym = len(lPnts_source)
	if not bCheck:
		for i, iVtx in enumerate(lPnts_source):
			print 'symmetrical check %f' %((i + 1)/float(iLength_sym))
			if iVtx:
				fPntX = mVtxPntArray[iVtx].x
				fPntY = mVtxPntArray[iVtx].y
				fPntZ = mVtxPntArray[iVtx].z

				iVtx_mirror = lPnts_target[i]
				if iVtx_mirror != None:
					fPntX_target = mVtxPntArray[iVtx_mirror].x
					fPntY_target = mVtxPntArray[iVtx_mirror].y
					fPntZ_target = mVtxPntArray[iVtx_mirror].z

					fPntX_source = fPntX
					fPntY_source = fPntY
					fPntZ_source = fPntZ

					if sAxis == 'YZ':
						fPntX_source = -fPntX
					elif sAxis == 'XZ':
						fPntY_source = -fPntY
					else:
						fPntZ_source = -fPntZ

					mVtxPntArray[iVtx_mirror].x = fPntX_source
					mVtxPntArray[iVtx_mirror].y = fPntY_source
					mVtxPntArray[iVtx_mirror].z = fPntZ_source

	else:
		for i, iVtx in enumerate(lPnts_source):
			print 'symmetrical check %f' %((i + 1)/float(iLength_sym))
			if iVtx:
				fPntX = mVtxPntArray[iVtx].x
				fPntY = mVtxPntArray[iVtx].y
				fPntZ = mVtxPntArray[iVtx].z

				iVtx_mirror = lPnts_target[i]
				if iVtx_mirror != None:
					fPntX_target = mVtxPntArray[iVtx_mirror].x
					fPntY_target = mVtxPntArray[iVtx_mirror].y
					fPntZ_target = mVtxPntArray[iVtx_mirror].z

					fPntX_source = fPntX
					fPntY_source = fPntY
					fPntZ_source = fPntZ

					if sAxis == 'YZ':
						fPntX_source = -fPntX
					elif sAxis == 'XZ':
						fPntY_source = -fPntY
					else:
						fPntZ_source = -fPntZ

					bPntX = (fPntX_source >= fPntX_target - fTolerance and fPntX_source <= fPntX_target + fTolerance)
					bPntY = (fPntY_source >= fPntY_target - fTolerance and fPntY_source <= fPntY_target + fTolerance)
					bPntZ = (fPntZ_source >= fPntZ_target - fTolerance and fPntZ_source <= fPntZ_target + fTolerance)

					if not bPntX or not bPntY or not bPntZ:
						lPnts_nonSym.append(iVtx)

						mVtxPntArray[iVtx_mirror].x = fPntX_source
						mVtxPntArray[iVtx_mirror].y = fPntY_source
						mVtxPntArray[iVtx_mirror].z = fPntZ_source

	if bMirrorMesh:
		mFnMesh.setPoints(mVtxPntArray, mSpace)

	return lPnts_nonSym

#### Sub Functions
def __setMFnMesh(sMesh):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	mFnMesh = OpenMaya.MFnMesh(mDagPath)
	return mFnMesh

def __meshVtxSymRemap(sMesh, sAxis = 'YZ', iDirection = 1, fTolerance = 0.00001, sSpace = 'world'):
	mVtxPntArray = getMeshVtxPntArray(sMesh, sSpace = sSpace)

	lPnts_source = []
	lPnts_middle = []
	lPnts_target = []
	lPnts_temp = []
	bSymmetrical = True

	iLength = mVtxPntArray.length()
	for i in range(iLength):

		print 'initialize mesh %f' %((i+1)/float(iLength))

		fPntX = mVtxPntArray[i].x
		fPntY = mVtxPntArray[i].y
		fPntZ = mVtxPntArray[i].z

		if sAxis == 'YZ':
			fAxis = fPntX
		elif sAxis == 'XZ':
			fAxis = fPntY
		else:
			fAxis = fPntZ

		if fAxis == 0:
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

	iLength_remap = len(lPnts_source)
	for i, iVtx in enumerate(lPnts_source):

		print'remap mesh vtx %f' %((i+1)/float(iLength_remap))

		fPntX = mVtxPntArray[iVtx].x
		fPntY = mVtxPntArray[iVtx].y
		fPntZ = mVtxPntArray[iVtx].z

		if sAxis == 'YZ':
			lPos = [-fPntX, fPntY, fPntZ]
		elif sAxis == 'XZ':
			lPos = [fPntX, -fPntY, fPntZ]
		else:
			lPos = [-fPntX, fPntY, -fPntZ]

		bSymmetrical_pnt = False
		iVtxClst, lPosClst, fDisClst = getClosestVtxInMesh(lPos, sMesh)

		if fDisClst > -fTolerance and fDisClst < fTolerance:
			lPnts_target.append(iVtxClst)
		else:
			lPnts_target.append(None)
			bSymmetrical = False

	for j in lPnts_temp:
		if j not in lPnts_target:
			lPnts_target.append(j)
			lPnts_source.append(None)
			bSymmetrical = False

	return bSymmetrical, lPnts_source, lPnts_target, lPnts_middle