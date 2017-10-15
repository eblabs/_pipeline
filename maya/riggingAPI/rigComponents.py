## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import common.files as files
import common.transforms as transforms
import common.workspaces as workspaces
import common.hierarchy as hierarchy
import controls
import joints
import deformers

#### Functions
def saveBlueprintJnts(sPath):
	if cmds.objExists(files.sBlueprintGrp):
		lJnts = cmds.listRelatives(files.sBlueprintGrp, c = True, ad = True, type = 'joint')
		joints.saveJointInfo(lJnts, sPath)
	else:
		cmds.warning('%s does not exist, skipped' %files.sBlueprintGrp)

def buildBlueprintJnts(sPath):
	if os.path.exists(sPath):
		joints.buildJointsFromJointsInfo(sPath, sGrp = files.sBlueprintGrp)
	else:
		cmds.warning('blueprint file does not exist, cannot build the joints')


#### rig build functions
def importModel(dData, sProject, sAsset):
	if dData['sProject']:
		sProject = dData['sProject']
	if dData['sAsset']:
		sAsset = dData['sAsset']
	fStartTime = time.time()
	workspaces.loadAsset(dModel['sProject'], dModel['sAsset'], 'model', sLoadType = 'import')
	fEndTime = time.time()
	print 'import %s model sucessfully, took %f seconds' %(sAsset, fEndTime - fStartTime)
	return True

def importBlueprint(dData, sProject, sAsset):
	sPath = generateComponentPath(dData, sProject, sAsset, 'blueprint')
	sPath = os.path.join(sPath, 'blueprint%s' %files.dRiggingComponents['blueprint'])
	if os.path.exists(sPath):
		fStartTime = time.time()
		joints.buildJointsFromJointsInfo(sPath, sGrp = files.sBlueprintGrp)
		fEndTime = time.time()
		print 'build blueprint joints sucessfully, took %f seconds' %(fEndTime - fStartTime)
		bReturn  = True
	else:
		cmds.warning('blueprint file does not exist, skipped')
		bReturn = False
	return bReturn

def importRigGeometry(lData, sProject, sAsset):
	bReturn = False
	for dData in lData:
		sPath = generateComponentPath(dData, sProject, sAsset, 'rigGeometry')
		lFiles = files.getFilesFromPath(sPath, sType = files.sFileType)
		if lFiles:
			for sFile in lFiles:
				fStartTime = time.time()
				cmds.file(sFile, i = True)
				fEndTime = time.time()
				print 'import %s sucessfully, took %f seconds' %(sFile, fEndTime - fStartTime)
			bReturn = True
	if not bReturn:
		cmds.warning('no rigGeometry file found, skipped')
	return bReturn

def importGeoHierarchy(lData, sProject, sAsset):
	bReturn = False
	for dData in lData:
		sPath = generateComponentPath(dData, sProject, sAsset, 'geoHierarchy')
		sPath = os.path.join(sPath, 'geoHierarchy%s' %files.dRiggingComponents['geoHierarchy'])
		if os.path.exists(sPath):
			fStartTime = time.time()
			hierarchy.loadNodesHierarchy(sPath)
			fEndTime = time.time()
			print 'load geoHierarchy from %s sucessfully, took %f seconds' %(sPath, fEndTime - fStartTime)
			bReturn = True
	if not bReturn:
		cmds.warning('no geoHierarchy file found, skipped')
	return bReturn

def importDeformer(lData, sProject, sAsset):
	bReturn = False
	lData.reverse()
	for dData in lData:
		sPath = generateComponentPath(dData, sProject, sAsset, 'deformer')
		lFiles = files.getFilesFromPath(sPath, sType = files.dRiggingComponents['deformer'])
		if lFiles:
			for sFile in lFiles:
				bReturnEach = deformers.loadSkinClusterData(sFile)
				if bReturnEach:
					bReturn = True
	return bReturn

def importControlShape(lData, sProject, sAsset):
	bReturn = False
	for dData in lData:
		sPath = generateComponentPath(dData, sProject, sAsset, 'controlShape')
		sPath = os.path.join(sPath, 'controlShape%s' %files.dRiggingComponents['controlShape'])
		if os.path.exists(sPath):
			fStartTime = time.time()
			controls.buildCtrlShapesFromCtrlShapeInfo(sPath)
			fEndTime = time.time()
			print 'load controlShape from %s sucessfully, took %f seconds' %(sPath, fEndTime - fStartTime)
			bReturn = True
	if not bReturn:
		cmds.warning('no controlShape file found, skipped')
	return bReturn







#### Sub Functions
def generateComponentPath(dData, sProject, sAsset, sComponent):
	if dData['sProject']:
		sProject = dData['sProject']
	if dData['sAsset']:
		sAsset = dData['sAsset']
	sPath, sWipPath = workspaces.getAssetDirectory(sProject = sProject, sAsset = sAsset, sType = 'rig')
	sPath = os.path.join(sPath, 'components')
	sPath = os.path.join(sPath, sComponent)
	return sPath

