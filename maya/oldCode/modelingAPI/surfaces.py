## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
## lib import
import curves
import namingAPI.naming as naming
import common.transforms as transforms
import common.apiUtils as apiUtils
import riggingAPI.joints as joints

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

def createRibbonFromNodes(sName, lNodes, bAuto = False, sDirection = 'x', fWidth = 1, bNormalize = True, sParent = None):
	sCrvA = curves.createCurveOnNodes('RIBBON_TEMP_001', lNodes, iDegree = 3)
	sCrvB = curves.createCurveOnNodes('RIBBON_TEMP_002', lNodes, iDegree = 3)
	if bAuto:
		sJntA = joints.createJntOnExistingNode(lNodes[0], lNodes[0], 'RIBBON_TEMP_AIM_001')
		sJntB = joints.createJntOnExistingNode(lNodes[-1], lNodes[-1], 'RIBBON_TEMP_AIM_002')
		cmds.parent(sJntB, sJntA)
		cmds.joint(sJntA, edit = True, oj = 'xyz', secondaryAxisOrient = 'yup', ch = True, zso = True)
		sOffsetA = transforms.createTransformNode('RIBBON_TEMP_OFFSET_001', sParent = sJntA, sPos = sJntA)
		sOffsetB = transforms.createTransformNode('RIBBON_TEMP_OFFSET_002', sParent = sJntA, sPos = sJntA)
		cmds.parent(sCrvA, sOffsetA)
		cmds.parent(sCrvB, sOffsetB)
		cmds.setAttr('%s.tz' %sOffsetA, fWidth * 0.5)
		cmds.setAttr('%s.tz' %sOffsetB, -fWidth * 0.5)
		cmds.parent(sCrvA, world = True)
		cmds.parent(sCrvB, world = True)
		cmds.makeIdentity(sCrvA, t = 1, r = 1, s = 1, apply = True)
		cmds.makeIdentity(sCrvB, t = 1, r = 1, s = 1, apply = True)
		cmds.delete(sJntA)
	else:
		cmds.setAttr('%s.t%s' %(sCrvA, sDirection), fWidth * 0.5)
		cmds.setAttr('%s.t%s' %(sCrvB, sDirection), -fWidth * 0.5)
	cmds.loft(sCrvA, sCrvB, ch=False, u = True, c = False, rn=False, ar=True, d = 3, ss = 1, rsn = True,name = sName)

	if bNormalize:
		cmds.rebuildSurface(sName, ch = False, su = len(lNodes) - 1, sv = 1, dv = 3, du = 3)
	cmds.delete(sCrvA, sCrvB)
	if sParent and cmds.objExists(sParent):
		cmds.parent(sName, sParent)

	return sName

def getSurfaceCvNum(sSurface):
	sShape = getShape(sSurface)
	lSpans = cmds.getAttr('%s.spansUV' %sShape)[0]
	lDegree = cmds.getAttr('%s.degreeUV' %sShape)[0]

	iCvU = lSpans[0] + lDegree[0]
	iCvV = lSpans[1] + lDegree[1]

	return [iCvU, iCvV]

def clusterSurface(sSurface, sUV = 'u'):
	oName = naming.oName(sSurface)
	lCvNum = getSurfaceCvNum(sSurface)
	lClsHnds = []
	if sUV.lower() == 'u':
		iCvNum = lCvNum[0]
	else:
		iCvNum = lCvNum[1]
	for i in range(iCvNum):
		if sUV.lower() == 'u':
			sClusterCV = '%s.cv[%d][0:%d]' %(sSurface, i, lCvNum[1] - 1)
		else:
			sClusterCV = '%s.cv[0:%d][%d]' %(sSurface, lCvNum[0] - 1, i)
		lCls = cmds.cluster(sClusterCV, name = naming.oName(sType = 'cluster', sSide = oName.sSide, sPart = oName.sPart, iIndex = oName.iIndex, iSuffix = i + 1).sName, rel = False)
		sClsHnd = naming.oName(sType = 'cluster', sSide = oName.sSide, sPart = '%sHandle' %oName.sPart, iIndex = oName.iIndex, iSuffix = i + 1).sName
		cmds.rename(lCls[1], sClsHnd)
		cmds.setAttr('%s.v' %sClsHnd, 0)
		lClsHnds.append(sClsHnd)
	return lClsHnds

def getClosestPointOnSurface(lPos, sSurface):
	mFnNurbsSurface = __setMFnNurbsSurface(sSurface)
	mPoint = apiUtils.setMPoint(lPos)

	u_util = OpenMaya.MScriptUtil()
	u_util.createFromDouble(0)
	u_param = u_util.asDoublePtr()

	v_util = OpenMaya.MScriptUtil()
	v_util.createFromDouble(0)
	v_param = v_util.asDoublePtr()

	mPointCls = mFnNurbsSurface.closestPoint(mPoint, False, u_param, v_param,  False, 1.0, OpenMaya.MSpace.kWorld)

	fVal_u = OpenMaya.MScriptUtil.getDouble(u_param)
	fVal_v = OpenMaya.MScriptUtil.getDouble(v_param)

	## normalize uv
	sShape = cmds.listRelatives(sSurface, s = True)[0]
	lRangeU = cmds.getAttr('%s.minMaxRangeU' %sShape)[0]
	lRangeV = cmds.getAttr('%s.minMaxRangeV' %sShape)[0]

	fVal_u = (fVal_u - lRangeU[0])/float(lRangeU[1] - lRangeU[0])
	fVal_v = (fVal_v - lRangeV[0])/float(lRangeV[1] - lRangeV[0])
	return (mPointCls[0], mPointCls[1], mPointCls[2]), [fVal_u, fVal_v]


#### Sub Functions
def __setMFnNurbsSurface(sSurface):
	mDagPath, mComponents = apiUtils.setDagPath(sSurface)
	mFnNurbsSurface = OpenMaya.MFnNurbsSurface(mDagPath)
	return mFnNurbsSurface