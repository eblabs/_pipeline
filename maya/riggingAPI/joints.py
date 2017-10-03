## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json

## libs Import
import common.files as files
import common.transforms as transforms

#### Functions
def createJnt(sName):
	cmds.select(clear = True)
	sJnt = cmds.joint(name = sName)
	return sJnt

def getJointInfo(sJnt):
	lTransformInfo = transforms.getNodeTransformInfo(sJnt)
	sParent = transforms.getNodeParent(sJnt)
	sRotateOrder = cmds.getAttr('%s.rotateOrder' %sJnt)
	dJntInfo = {sJnt:
				{'lTransformInfo': lTransformInfo,
				 'sParent': sParent,
				 'sRotateOrder': sRotateOrder}
				}
	return dJntInfo

def getJointsInfoFromList(lJnts):
	dJntsInfo = {}
	for sJnt in lJnts:
		dJntInfo = getJointInfo(sJnt)
		dJntsInfo.update(dJntInfo)
	return dJntsInfo

def saveJointInfo(lJnts, sPath):
	dJntsInfo = getJointsInfoFromList(lJnts)
	files.writeJsonFile(sPath, dJntsInfo)

def buildJointsFromJointsInfo(sPath, sGrp = None):
	dJntsInfo = files.readJsonFile(sPath)

	if sGrp:
		if not cmds.objExists(sGrp):
			cmds.group(empty = True, name = sGrp)

	for sJnt in dJntsInfo.keys():
		if cmds.objExists(sJnt):
			cmds.delete(sJnt)
		createJnt(sJnt)

		lTransformInfo = dJntsInfo[sJnt]['lTransformInfo']
		transforms.setNodeTransform(sJnt, lTransformInfo)
		cmds.makeIdentity(sJnt, apply = True, t = 1, r = 1, s = 1)

		if sGrp:
			cmds.parent(sJnt, sGrp)

	for sJnt in dJntsInfo.keys():
		sParent = dJntsInfo[sJnt]['sParent']
		sRotateOrder = dJntsInfo[sJnt]['sRotateOrder']

		if sParent and cmds.objExists(sParent) and sParent != sGrp:
			cmds.parent(sJnt, sParent)

		cmds.setAttr('%s.rotateOrder' %sJnt, sRotateOrder)
