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
	cmds.rebuildSurface(sName, ch = False, su = len(lNodes) - 1, sv = 1, dv = 3, du = 3)
	cmds.delete(sCrvA, sCrvB)
	return sName

def getClosetPointOnSurface(lPos, sSurface):
	mFnNurbsSurface = __setMFnNurbsSurface(sSurface)
	mPoint = apiUtils.setMPoint(lPos)

	u_util = OpenMaya.MScriptUtil()
	u_util.createFromDouble(0)
	u_param = u_util.asDoublePtr()

	v_util = OpenMaya.MScriptUtil()
	v_util.createFromDouble(0)
	v_param = v_util.asDoublePtr()

	mPointCls = mFnNurbsSurface.closestPoint(mPoint, False, u_param, v_param,  False, 1.0, OpenMaya.MSpace.kWorld)
	return [(mPointCls[0], mPointCls[1], mPointCls[2]), (OpenMaya.MScriptUtil.getDouble(u_param), OpenMaya.MScriptUtil.getDouble(v_param))]


#### Sub Functions
def __setMFnNurbsSurface(sSurface):
	mDagPath, mComponents = apiUtils.setDagPath(sSurface)
	mFnNurbsSurface = OpenMaya.MFnNurbsSurface(mDagPath)
	return mFnNurbsSurface