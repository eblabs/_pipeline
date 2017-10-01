## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import files
import transforms

#### Functions
def getJointInfo(sJnt):
	lTransformInfo = transforms.getNodeTransformInfo(sNode)
	sParent = transforms.getNodeParent(sNode)
	sRotateOrder = cmds.getAttr('%s.rotateOrder' %sJnt)
	dJntInfo = {sJnt:
				{'lTransformInfo': lTransformInfo,
				 'sParent': sParent,
				 'sRotateOrder': sRotateOrder}
				}
	return dJntInfo

def getJointsInfo(lJnts):
	dJntsInfo = {}
	for sJnt in lJnts:
		dJntInfo = getJointInfo(sJnt)
		dJntsInfo.update(dJntInfo)
	return dJntsInfo

def saveJointsInfo(lJnts, sPath):
	dJntsInfo = getJointsInfo(lJnts)
	files.writeJsonFile(sPath, dJntsInfo)

def buildJointsFromJointsInfo(sPath, sGrp = None):
	dJntsInfo = files.readJsonFile(sPath)

	if sGrp:
		cmds.group(empty = True, name = sGrp)

	for sJnt in dJntsInfo.keys():
		if cmds.objExists(sJnt):
			cmds.delete(sJnt)
		cmds.select(clear = True)
		cmds.joint(name = sJnt)
		if sGrp:
			cmds.parent(sJnt, sGrp)

	for sJnt in dJntsInfo.keys():
		lTransformInfo = dJntsInfo[sJnt]['lTransformInfo']
		sParent = dJntsInfo[sJnt]['sParent']
		sRotateOrder = dJntsInfo[sJnt]['sRotateOrder']

		transforms.setNodeTransform(sJnt, lTransformInfo)
		cmds.makeIdentity(sJnt, apply = True, t = 1, r = 1, s = 1)

		if sParent and cmds.objExists(sParent) and sParent != sGrp:
			cmds.parent(sJnt, sParent)

		cmds.setAttr('%s.rotateOrder' %sJnt, sRotateOrder)
