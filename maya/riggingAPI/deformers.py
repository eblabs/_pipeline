## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import time
## libs Import
import common.apiUtils as apiUtils
import modelingAPI.meshes as meshes
import joints
import namingAPI.naming as naming

#### Functions
def getSkinCluster(sNode):
	sSkinCluster = mel.eval('findRelatedSkinCluster("' + sNode + '")')
	return sSkinCluster

def createSkinCluster(sNode, lInfluences):
	lJnts = []
	lGeos = []
	lCrvs = []
	sGrp = '_missedSkinJoints_'
	oName = naming.oName(sNode)
	oName.sType = 'skinCluster'
	for sInfluence in lInfluences:
		if cmds.objExists(sInfluence):
			if cmds.objectType(sInfluence) == 'joint':
				lJnts.append(sInfluence)
			elif cmds.objExists(sInfluence) == 'nurbsCurve':
				lCrvs.append(sInfluence)
			else:
				lGeos.append(sInfluence)
		else:
			createJnt(sInfluence)
			lJnts.append(sInfluence)
			if not cmds.objExists(sGrp):
				cmds.group(empty = True, name = sGrp)
				cmds.setAttr('%s.v' %sGrp, 0)
			cmds.parent(sInfluence, sGrp)

	cmds.skinCluster(lJnts, sNode, tsb = True, bindMethod = 0, skinMethod = 0, name = oName.sName)

	for i, lComponents in enumerate([lCrvs, lGeos]):
		if lComponents:
			for sComponent in lComponents:
				cmds.skinCluster(oName.sName, e = True, ug = i, ai = sComponent)
				oNameGeo = naming.oName(sComponent)
				oNameGeo.sPart += 'Base'
				cmds.rename('%sBase' %sComponent, oNameGeo.sName)
			cmds.setAttr('%s.useComponents' %oName.sName, 1)

	return oName.sName

def removeUnusedInfluences(sNode):
	cmds.select(sNode)
	mel.eval('removeUnusedInfluences')


def getSkinClusterDataFromMesh(sMesh):
	try:
		removeUnusedInfluences(sMesh)
	except:
		pass

	sSkinCluster = getSkinCluster(sMesh)
	iVtxCount = meshes.getPolyVetexCount(sMesh)
	iSkinMethod = cmds.getAttr('%s.skinningMethod' %sSkinCluster)
	bComponents = cmds.getAttr('%s.useComponents' %sSkinCluster)
	iNormalizeWeights = cmds.getAttr('%s.normalizeWeights' %sSkinCluster)
	dSkinData = _getSkinWeights(sMesh)
	lBlendWeights = _getSkinBlendWeights(sMesh)
	mVtxPntArray = meshes.getMeshVtxPntArray(sMesh)
	lVtxPos = apiUtils.convertMPointArrayToList(mVtxPntArray)
	dSkinData = {
					'sGeo' : sMesh,
					'iVtxCount': iVtxCount,
					'iSkinMethod': iSkinMethod,
					'bComponents': bComponents,
					'iNormalizeWeights': iNormalizeWeights,
					'dSkinData': dSkinData,
					'lBlendWeights': lBlendWeights,
					'lVtxPos': lVtxPos
				}
	return dSkinData

def saveSkinClusterData(sMesh, sPath):
	fStartTime = time.time()

	dSkinData = getSkinClusterDataFromMesh(sMesh)
	files.writePickleFile(sPath, dSkinData)

	fEndTime = time.time()

	print 'saved skinCluster for %s, took %s seconds' %(sMesh, fEndTime - fStartTime)

def loadSkinClusterData(sPath, sMesh = None, sMethod = 'vtxId'):
	fStartTime = time.time()

	dSkinData = files.readPickleFile(sPath)

	if not sMesh:
		sMesh = dSkinData['sGeo']

	if cmds.objExists(sMesh):
		iVtxCount = meshes.getPolyVetexCount(sMesh)
		if iVtxCount == dSkinData['iVtxCount']:
			lInfluences = dSkinData['dSkinData'].keys()
			sSkinCluster = createSkinCluster(sMesh, lInfluences)
			mFnSkinCluster = _setMFnSkinCluster(sSkinCluster)

			cmds.setAttr('%s.normalizeWeights' %sSkinCluster, 0)
			_setSkinWeights(sMesh, mFnSkinCluster, dSkinData['dSkinData'], sMethod = sMethod, lVtxPos = lVtxPos)
			_setSkinBlendWeights(sMesh, mFnSkinCluster, dSkinData['lBlendWeights'], sMethod = sMethod, lVtxPos = lVtxPos)

			cmds.setAttr('%s.skinningMethod' %sSkinCluster, dSkinData['iSkinMethod'])
			cmds.setAttr('%s.useComponents' %sSkinCluster, dSkinData['bComponents'])
			cmds.setAttr('%s.normalizeWeights' %sSkinCluster, dSkinData['iNormalizeWeights'])

	fEndTime = time.time()

	print 'loaded skinCluster for %s, took %s seconds' %(sMesh, fEndTime - fStartTime)

#### Sub Functions
def _setMFnSkinCluster(sSkinCluster):
	mObj = apiUtils.setMObj(sSkinCluster)
	mFnSkinCluster = OpenMayaAnim.MFnSkinCluster(mObj)
	return mFnSkinCluster

def _getSkinWeightArray(sMesh, mFnSkinCluster):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	mWeightArray = OpenMaya.MDoubleArray()
	uIntPtr = apiUtils.createUintPtr()
	mFnSkinCluster.getWeights(mDagPath, mComponents, mWeightArray, uIntPtr)

	return mWeightArray

def _getSkinInfluenceArray(sMesh, mFnSkinCluster):
	mInfluenceArray = OpenMaya.MDagPathArray()
	iInfluence = mFnSkinCluster.influenceObjects(mInfluenceArray)
	return mInfluenceArray

def _getSkinWeightsData(sMesh):
	sSkinCluster = getSkinCluster(sMesh)
	mFnSkinCluster = _setMFnSkinCluster(sSkinCluster)
	mWeightArray = _getSkinWeightArray(sMesh, mFnSkinCluster)
	mInfluenceArray = _getSkinInfluenceArray(sMesh, mFnSkinCluster)
	iComponents = mWeightArray.length() / mInfluenceArray.length()

	dSkinData = {}

	for i in range(mInfluenceArray.length()):
		sInfluence = mInfluenceArray[i].partialPathName()
		dSkinData[sInfluence] = []
		for j in range(iComponents):
			dSkinData[sInfluence].append(mWeightArray[j * mInfluenceArray.length() + i])

	return dSkinData

def _getSkinBlendWeights(sMesh):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	sSkinCluster = getSkinCluster(sMesh)
	mFnSkinCluster = _setMFnSkinCluster(sSkinCluster)
	mWeightArray = OpenMaya.MDoubleArray()
	mFnSkinCluster.getBlendWeights(mDagPath, mComponents, mWeightArray)
	lBlendWeights = apiUtils.convertMDoubleArrayToList(mWeightArray)
	return lBlendWeights

def _setSkinWeights(sMesh, mFnSkinCluster, dSkinData, sMethod = 'vtxId', lVtxPos = None, fTolerance = 0.00001):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	mWeightArray = _getSkinWeightArray(sMesh, mFnSkinCluster)
	mInfluenceArray = _getSkinInfluenceArray(sMesh, mFnSkinCluster)
	iComponents = mWeightArray.length() / mInfluenceArray.length()

	lComponents = []
	if sMethod == 'vtxPos':
		mVtxPntArray = getMeshVtxPntArray(sMesh)
		lVtxPosNew = apiUtils.convertMPointArrayToList(mVtxPntArray)
		for lNew in lVtxPosNew:
			fPntX = lNew[0]
			fPntY = lNew[1]
			fPntZ = lNew[2]
			for i, lOld in enumerate(lVtxPos):
				if lOld[0] in range(fPntX - fTolerance, fPntX + fTolerance) and lOld[1] in range(fPntY - fTolerance, fPntY + fTolerance) and lOld[2] in range(fPntZ - fTolerance, fPntZ + fTolerance):
					lComponents.append(i)
					break
	else:
		lComponents = range(iComponents)

	for sInfluence in dSkinData.keys():
		for i in range(mInfluenceArray.length()):
			sInfluenceCurrent = mInfluenceArray[i].partialPathName()
			if sInfluence == sInfluenceCurrent:
				for j, m in enumerate(lComponents):
					mWeightArray.set(dSkinData[sInfluence][m], j * mInfluenceArray.length() + i)
				break

	mIndexArray = OpenMaya.MIntArray(mInfluenceArray.length())
    for i in range(mInfluenceArray.length()):
        mIndexArray.set(i, i)
    mFnSkinCluster.setWeights(mDagPath, mComponents, mIndexArray, mWeightArray, False)

def _setSkinBlendWeights(sMesh, mFnSkinCluster, lBlendWeights, sMethod = 'vtxId', lVtxPos = None, fTolerance = 0.00001):
	mDagPath, mComponents = apiUtils.setDagPath(sMesh)
	iComponents = len(lBlendWeights)
	mBlendWeightsArray = OpenMaya.MDoubleArray(iComponents)

	lComponents = []
	if sMethod == 'vtxPos':
		mVtxPntArray = getMeshVtxPntArray(sMesh)
		lVtxPosNew = apiUtils.convertMPointArrayToList(mVtxPntArray)
		for lNew in lVtxPosNew:
			fPntX = lNew[0]
			fPntY = lNew[1]
			fPntZ = lNew[2]
			for i, lOld in enumerate(lVtxPos):
				if lOld[0] in range(fPntX - fTolerance, fPntX + fTolerance) and lOld[1] in range(fPntY - fTolerance, fPntY + fTolerance) and lOld[2] in range(fPntZ - fTolerance, fPntZ + fTolerance):
					lComponents.append(i)
					break
	else:
		lComponents = range(iComponents)
	for i, j in enumerate(lComponents):
        mBlendWeightsArray.set(lBlendWeights[j], i)
    mFnSkinCluster.setBlendWeights(mDagPath, mComponents, mBlendWeightsArray)
