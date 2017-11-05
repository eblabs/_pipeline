## External Import
import maya.cmds as cmds
import maya.mel as mel

def createCurveOnNodes(sName, lNodes, iDegree = 3):
	lPnts = []
	for sNode in lNodes:
		lPos = cmds.xform(sNode, q = True, t = True, ws = True)
		lPnts.append(lPos)
	cmds.curve(p = lPnts, d = iDegree, name = sName)
	return sName