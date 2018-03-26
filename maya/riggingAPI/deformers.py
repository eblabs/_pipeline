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
import common.files as files
reload(files)

#### Functions
def getSkinCluster(sNode):
	sSkinCluster = mel.eval('findRelatedSkinCluster("' + sNode + '")')
	return sSkinCluster

def getInfluenceObjects(sSkin):
	lJnts = cmds.skinCluster(sSkin, q = True, inf = True)
	return lJnts

def copySkinCluster(sSourceMesh, lTargetMeshes, bRemove = True, bOverride = True):
	sSkinSource = getSkinCluster(sSourceMesh)
	if sSkinSource:
		lJnts = getInfluenceObjects(sSkinSource)
	for sMesh in lTargetMeshes:
		sSkinTarget = getSkinCluster(sMesh)
		if sSkinTarget:
			if bOverride:
				cmds.delete(sSkinTarget) 
				sSkinTarget = createSkinCluster(sMesh, lJnts)
		else:
			sSkinTarget = createSkinCluster(sMesh, lJnts)
		cmds.copySkinWeights(ss = sSkinSource, ds = sSkinTarget, noMirror = True, surfaceAssociation  = 'closestPoint', influenceAssociation = ['label', 'oneToOne'], normalize = True)
		if bRemove:
			removeUnusedInfluence(sMesh)
			
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
			joints.createJnt(sInfluence)
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

def removeUnusedInfluence(sMesh):
	sSkinCluster = getSkinCluster(sMesh)
	if sSkinCluster:
		lInfluences = cmds.skinCluster(sSkinCluster, q = True, inf = True)
		lInfluencesUsed = cmds.skinCluster(sSkinCluster, q = True, wi = True)
		for sInfluence in lInfluencesUsed:
			lInfluences.remove(sInfluence)
		if lInfluences:
			for sInfluence in lInfluences:
				cmds.skinCluster(sSkinCluster, e = True, removeInfluence = sInfluence)
				print 'remove influenceObject %s from %s' %(sInfluence, sSkinCluster)



def getSkinClusterDataFromMesh(sMesh):
	sSkinCluster = getSkinCluster(sMesh)
	iVtxCount = meshes.getPolyVtxCount(sMesh)
	iSkinMethod = cmds.getAttr('%s.skinningMethod' %sSkinCluster)
	bComponents = cmds.getAttr('%s.useComponents' %sSkinCluster)
	iNormalizeWeights = cmds.getAttr('%s.normalizeWeights' %sSkinCluster)
	dSkinData = __getSkinWeightsData(sMesh)
	lBlendWeights = __getSkinBlendWeights(sMesh)
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



#------------ save & load skinCluster functions -----------
def saveSkinClusterData(sMesh, sPath):
	fStartTime = time.time()

	dSkinData = getSkinClusterDataFromMesh(sMesh)
	files.writePickleFile(sPath, dSkinData)

	fEndTime = time.time()

	print 'saved skinCluster for %s, took %s seconds' %(sMesh, fEndTime - fStartTime)

def loadSkinClusterData(sPath, sMesh = None, sMethod = 'vtxId'):
	bReturn = False

	dSkinData = files.readPickleFile(sPath)

	if not sMesh:
		sMesh = dSkinData['sGeo']

	if cmds.objExists(sMesh):
		sSkinCluster = getSkinCluster(sMesh)
		if not sSkinCluster:
			iVtxCount = meshes.getPolyVtxCount(sMesh)
			if iVtxCount == dSkinData['iVtxCount']:
				fStartTime = time.time()

				lInfluences = dSkinData['dSkinData'].keys()
				sSkinCluster = createSkinCluster(sMesh, lInfluences)
				mFnSkinCluster = __setMFnSkinCluster(sSkinCluster)

				cmds.setAttr('%s.normalizeWeights' %sSkinCluster, 0)
				__setSkinWeights(sMesh, mFnSkinCluster, dSkinData['dSkinData'], sMethod = sMethod, lVtxPos = dSkinData['lVtxPos'])
				__setSkinBlendWeights(sMesh, mFnSkinCluster, dSkinData['lBlendWeights'], sMethod = sMethod, lVtxPos = dSkinData['lVtxPos'])

				cmds.setAttr('%s.skinningMethod' %sSkinCluster, dSkinData['iSkinMethod'])
				cmds.setAttr('%s.useComponents' %sSkinCluster, dSkinData['bComponents'])
				cmds.setAttr('%s.normalizeWeights' %sSkinCluster, dSkinData['iNormalizeWeights'])

				fEndTime = time.time()
				print 'loaded skinCluster for %s, took %s seconds' %(sMesh, fEndTime - fStartTime)

				bReturn = True
			else:
				print '%s has different vertice count, original is %d, current is %s, skipped' %(sMethod, iVtxCount, dSkinData['iVtxCount'])
		else:
			print '%s already has a skinCluster on it, %s, skipped' %(sMesh, skinCluster)
	else:
		print '%s does not exist, skipped' %sMesh

	return bReturn

	

	
#------------ save & load skinCluster functions end -----------

#### Sub Functions
def __setMFnSkinCluster(sSkinCluster):
	mObj = apiUtils.setMObj(sSkinCluster)
	mFnSkinCluster = OpenMayaAnim.MFnSkinCluster(mObj)
	return mFnSkinCluster

def __getSkinWeightArray(mFnSkinCluster):
	mDagPath, mComponents = __getComponentsFromMFnSkinCluster(mFnSkinCluster)
	mWeightArray = OpenMaya.MDoubleArray()
	mUtil = OpenMaya.MScriptUtil()
	mUtil.createFromInt(0)
	uIntPtr = mUtil.asUintPtr()
	mFnSkinCluster.getWeights(mDagPath, mComponents, mWeightArray, uIntPtr)

	return mWeightArray

def __getComponentsFromMFnSkinCluster(mFnSkinCluster):
	mFnSet = OpenMaya.MFnSet(mFnSkinCluster.deformerSet())
	mSel = OpenMaya.MSelectionList()
	mFnSet.getMembers(mSel, False)
	mDagPath = OpenMaya.MDagPath()
	mComponents = OpenMaya.MObject()
	mSel.getDagPath(0, mDagPath, mComponents)
	return mDagPath, mComponents

def __getSkinInfluenceArray(mFnSkinCluster):
	mInfluenceArray = OpenMaya.MDagPathArray()
	iInfluence = mFnSkinCluster.influenceObjects(mInfluenceArray)
	return mInfluenceArray, iInfluence

def __getSkinWeightsData(sMesh):
	sSkinCluster = getSkinCluster(sMesh)
	mFnSkinCluster = __setMFnSkinCluster(sSkinCluster)
	mWeightArray = __getSkinWeightArray(mFnSkinCluster)

	mInfluenceArray, iInfluence = __getSkinInfluenceArray(mFnSkinCluster)

	iComponents = mWeightArray.length() / iInfluence

	dSkinData = {}

	for i in range(iInfluence):
		sInfluence = mInfluenceArray[i].partialPathName()

		dSkinData[sInfluence] = []
		for j in range(iComponents):
			dSkinData[sInfluence].append(mWeightArray[j * iInfluence + i])

	return dSkinData




def __getSkinBlendWeights(sMesh):
	sSkinCluster = getSkinCluster(sMesh)
	mFnSkinCluster = __setMFnSkinCluster(sSkinCluster)
	mDagPath, mComponents = __getComponentsFromMFnSkinCluster(mFnSkinCluster)
	mWeightArray = OpenMaya.MDoubleArray()
	mFnSkinCluster.getBlendWeights(mDagPath, mComponents, mWeightArray)
	lBlendWeights = apiUtils.convertMDoubleArrayToList(mWeightArray)
	return lBlendWeights

def __setSkinWeights(sMesh, mFnSkinCluster, dSkinData, sMethod = 'vtxId', lVtxPos = None, fTolerance = 0.00001):
	mDagPath, mComponents = __getComponentsFromMFnSkinCluster(mFnSkinCluster)
	mWeightArray = __getSkinWeightArray(mFnSkinCluster)
	mInfluenceArray, iInfluence = __getSkinInfluenceArray(mFnSkinCluster)
	iComponents = mWeightArray.length() / iInfluence

	if sMethod == 'vtxPos':
		lComponents = meshes.remapVtxIdToMesh(sMesh, lVtxPosBase = lVtxPos, fTolerance = fTolerance)
	else:
		lComponents = range(iComponents)

	for sInfluence in dSkinData.keys():
		for i in range(iInfluence):
			sInfluenceCurrent = mInfluenceArray[i].partialPathName()
			if sInfluence == sInfluenceCurrent:
				for j, m in enumerate(lComponents):
					mWeightArray.set(dSkinData[sInfluence][m], j * iInfluence + i)
				break

	mIndexArray = OpenMaya.MIntArray(iInfluence)
	for i in range(iInfluence):
		mIndexArray.set(i, i)
	mFnSkinCluster.setWeights(mDagPath, mComponents, mIndexArray, mWeightArray, False)

def __setSkinBlendWeights(sMesh, mFnSkinCluster, lBlendWeights, sMethod = 'vtxId', lVtxPos = None, fTolerance = 0.00001):
	mDagPath, mComponents = __getComponentsFromMFnSkinCluster(mFnSkinCluster)
	iComponents = len(lBlendWeights)
	mBlendWeightsArray = OpenMaya.MDoubleArray(iComponents)

	if sMethod == 'vtxPos':
		lComponents = meshes.remapVtxIdToMesh(sMesh, lVtxPosBase = lVtxPos, fTolerance = fTolerance)
	else:
		lComponents = range(iComponents)
	for i, j in enumerate(lComponents):
		mBlendWeightsArray.set(lBlendWeights[j], i)
	mFnSkinCluster.setBlendWeights(mDagPath, mComponents, mBlendWeightsArray)
