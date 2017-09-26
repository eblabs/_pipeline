## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import files

#### Functions
def getNodeTransformInfo(sNode):
	lPos = cmds.xform(sNode, q = True, t = True, ws = True)
	lRot = cmds.xform(sNode, q = True, ro = True, ws = True)
	lScl = cmds.xform(sNode, q = True, s = True, ws = True)
	return [lPos, lRot, lScl]

def getNodeParent(sNode):
	sParent = cmds.listRelatives(sNode, p = True)
	if sParent:
		sParent = sParent[0]
	else:
		sParent = None
	return sParent

def getNodesHierarchy(lNodes):
	dHierarchy = {}
	for sNode in lNodes:
		sParent = transforms.getNodeParent(sNode)
		dNodeParent = {sNode: sParent}
		dHierarchy.update(dNodeParent)
	return dHierarchy

#### Sub Functions
