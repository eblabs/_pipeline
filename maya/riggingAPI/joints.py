## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json

## libs Import
import common.files as files
import common.transforms as transforms
import common.hierarchy as hierarchy

#### Functions
def createJnt(sName, iRotateOrder = 0):
	cmds.select(clear = True)
	sJnt = cmds.joint(name = sName)
	cmds.setAttr('%s.ro' %sJnt, iRotateOrder)
	return sJnt

def createJntOnExistingNode(sNode, sSearch, sReplace, sParent = None):
	lTransformInfo = transforms.getNodeTransformInfo(sNode)
	iRotateOrder = cmds.getAttr('%s.rotateOrder' %sNode)
	sJnt = createJnt(sNode.replace(sSearch, sReplace))
	cmds.setAttr('%s.rotateOrder' %sJnt, iRotateOrder)
	transforms.setNodeTransform(sJnt, lTransformInfo)
	cmds.makeIdentity(sJnt, apply = True, t = 1, r = 1, s = 1)
	if sParent and cmds.objExists(sParent):
		cmds.parent(sJnt, sParent)
	return sJnt

def createJntOnTransformInfo(sName, lTransformInfo, iRotateOrder = 0, sParent = None):
	sJnt = createJnt(sName, iRotateOrder = iRotateOrder)
	transforms.setNodeTransform(sJnt, lTransformInfo)
	cmds.makeIdentity(sJnt, apply = True, t = 1, r = 1, s = 1)
	if sParent and cmds.objExists(sParent):
		cmds.parent(sJnt, sParent)
	return sJnt

def getJointOrient(sJnt):
	lJointOrient = []
	for sAxis in ['X', 'Y', 'Z']:
		fOrient = cmds.getAttr('%s.jointOrient%s' %(sJnt, sAxis))
		lJointOrient.append(fOrient)
	return lJointOrient

#------------ save & load joints functions -----------
def getJointInfo(sJnt):
	lTransformInfo = transforms.getNodeTransformInfo(sJnt)
	sParent =  hierarchy.getNodeParent(sJnt)
	iRotateOrder = cmds.getAttr('%s.rotateOrder' %sJnt)
	dJntInfo = {sJnt:
				{'lTransformInfo': lTransformInfo,
				 'sParent': sParent,
				 'iRotateOrder': iRotateOrder}
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
		iRotateOrder = dJntsInfo[sJnt]['iRotateOrder']
		lTransformInfo = dJntsInfo[sJnt]['lTransformInfo']

		createJntOnTransformInfo(sJnt, lTransformInfo, iRotateOrder = iRotateOrder, sParent = sGrp)

	for sJnt in dJntsInfo.keys():
		sParent = dJntsInfo[sJnt]['sParent']

		if sParent and cmds.objExists(sParent) and sParent != sGrp:
			cmds.parent(sJnt, sParent)

#------------ save & load joints functions end -----------