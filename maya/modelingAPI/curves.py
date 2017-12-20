## External Import
import maya.cmds as cmds
import maya.mel as mel
import namingAPI.naming as naming
import common.transforms as transforms

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

def createCurveOnNodes(sName, lNodes, iDegree = 3, sParent = None):
	lPnts = []
	for sNode in lNodes:
		lPos = cmds.xform(sNode, q = True, t = True, ws = True)
		lPnts.append(lPos)
	cmds.curve(p = lPnts, d = iDegree, name = sName)
	sShape = getShape(sName)
	cmds.rename(sShape, '%sShape' %sName)
	if sParent and cmds.objExists(sParent):
		cmds.parent(sName, sParent)
	return sName

def createCurveLine(sName, lNodes, sParent = None):
	oName = naming.oName(sName)
	sGrp = transforms.createTransformNode(naming.oName(sType = 'grp', sSide = oName.sSide, sPart = oName.sPart, iIndex = oName.iIndex).sName, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sParent)
	sCrv = createCurveOnNodes(sName, lNodes, iDegree = 1, sParent = sGrp)
	sCrvShape = getShape(sCrv)
	cmds.setAttr('%s.overrideEnabled' %sCrvShape, 1)
	cmds.setAttr('%s.overrideDisplayType' %sCrvShape, 2)
	cmds.setAttr('%s.inheritsTransform' %sCrv, 0)
	for i, sNode in enumerate(lNodes):
		lCls = cmds.cluster('%s.cv[%i]' %(sCrv, i), name = naming.oName(sType = 'cluster', sSide = oName.sSide, sPart = oName.sPart, iindex = i + 1).sName)
		cmds.setAttr('%s.v' %lCls[1], 0)
		cmds.pointConstraint(sNode, lCls[1], mo = False)
		cmds.parent(lCls[1], sGrp)
	return sCrv, sGrp

def getCurveCvNum(sCrv):
	sShape = getShape(sCrv)
	iSpan = cmds.getAttr('%s.spans' %sShape)
	iDegree = cmds.getAttr('%s.degree' %sShape)
	iCvNum = iSpan + iDegree
	return iCvNum

def clusterCurve(sCrv):
	oName = naming.oName(sCrv)
	iCvNum = getCurveCvNum(sCrv)
	lClsHnds = []
	for i in range(iCvNum):
		lCls = cmds.cluster('%s.cv[%d]' %(sCrv, i), name = naming.oName(sType = 'cluster', sSide = oName.sSide, sPart = oName.sPart, iIndex = oName.iIndex, iSuffix = i + 1).sName, rel = False)
		sClsHnd = naming.oName(sType = 'cluster', sSide = oName.sSide, sPart = '%sHandle' %oName.sPart, iIndex = oName.iIndex, iSuffix = i + 1).sName
		cmds.rename(lCls[1], sClsHnd)
		cmds.setAttr('%s.v' %sClsHnd, 0)
		lClsHnds.append(sClsHnd)
	return lClsHnds

def rebuildCurveWithSameCvNum(sCrv):
	sShape = getShape(sCrv)
	iDegree = cmds.getAttr('%s.degree' %sShape)
	iCvNum = getCurveCvNum(sCrv)
	cmds.rebuildCurve(sCrv, s = iCvNum - 1, d = iDegree, ch = True)

