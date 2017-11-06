## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
## lib import
import curves
import common.apiUtils as apiUtils
reload(apiUtils)

def createRibbonFromNodes(sName, lNodes, sDirection = 'x', fWidth = 1):
	sCrvA = curves.createCurveOnNodes('RIBBON_TEMP_01', lNodes, iDegree = 3)
	sCrvB = curves.createCurveOnNodes('RIBBON_TEMP_02', lNodes, iDegree = 3)
	cmds.setAttr('%s.t%s' %(sCrvA, sDirection), fWidth * 0.5)
	cmds.setAttr('%s.t%s' %(sCrvB, sDirection), -fWidth * 0.5)
	cmds.loft(sCrvA, sCrvB, ch=False, rn=True, ar=True, name = sName)
	cmds.rebuildSurface(sName, ch = False, sv = len(lNodes) - 1, su = 1, dv = 3, du = 3)
	cmds.delete(sCrvA, sCrvB)
	return sName

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