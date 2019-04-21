## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import files

#### Functions
def getNodeParent(sNode):
	sParent = cmds.listRelatives(sNode, p = True)
	if sParent:
		sParent = sParent[0]
	else:
		sParent = None
	return sParent

#------------ save & load hierarchy functions -----------
def getNodesHierarchy(lNodes):
	dHierarchy = {}
	for sNode in lNodes:
		sParent = getNodeParent(sNode)
		dNodeParent = {sNode: sParent}
		dHierarchy.update(dNodeParent)
	return dHierarchy

def saveNodesHierarchy(lNodes, sPath):
	dHierarchy = getNodesHierarchy(lNodes)
	files.writeJsonFile(sPath, dHierarchy)

def loadNodesHierarchy(sPath):
	dHierarchy = files.readJsonFile(sPath)
	for sNode in dHierarchy.keys():
		if cmds.objExists(sNode):
			sParent = dHierarchy[sNode]
			if sParent:
				if cmds.objExists(sParent):
					sParentOrig = cmds.listRelatives(sNode, p = True)
					if not sParentOrig or sParent not in sParentOrig:
						cmds.parent(sNode, sParent)
#------------ save & load hierarchy functions end -----------