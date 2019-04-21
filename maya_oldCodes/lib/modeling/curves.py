# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

# -- import lib
import lib.common.naming.naming as naming
import lib.common.apiUtils as apiUtils
import lib.common.attributes as attributes
# ---- import end ----

# create curve line
def createCurveLine(name, nodes):
	CrvName = naming.Naming(name)
	crv = cmds.curve(d = 1, p = [[0,0,0],[0,0,0]], name = name)
	crvShape = cmds.listRelatives(crv, s = True)[0]
	crvShape = cmds.rename(crvShape, '{}Shape'.format(crv))
	cmds.setAttr('{}.overrideEnabled'.format(crvShape), 1)
	cmds.setAttr('{}.overrideDisplayType'.format(crvShape), 2)
	cmds.setAttr('{}.inheritsTransform'.format(crv), 0)
	attributes.lockHideAttrs(crv, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
	clsHndList = []
	for i, node in enumerate(nodes):
		clsNodes = cmds.cluster('{}.cv[{}]'.format(crv, i), name = naming.Naming(type = 'cluster', side = CrvName.side, part = CrvName.part, index = i+1).name)
		cmds.setAttr('{}.v'.format(clsNodes[1]), 0)
		clsHnd = cmds.rename(clsNodes[1], naming.Naming(type = 'clusterHandle', side = CrvName.side, part = CrvName.part, index = i+1).name)
		cmds.delete(cmds.pointConstraint(node, clsHnd, mo = False))
		clsHndList.append(clsHnd)		
	return crv, clsHndList

# create curve on nodes
def createCurveOnNodes(name, nodes, degree = 3, parent = None):
	if isinstance(nodes[0], basestring):
		pnts = []
		for n in nodes:
			pos = cmds.xform(node, q = True, t = True, ws = True)
			pnts.append(pos)
	else:
		pnts = nodes
	crv = cmds.curve(p = pnts, d = degree, name = name)
	crvShape = cmds.listRelatives(crv, s = True)[0]
	crvShape = cmds.rename(crvShape, '{}Shape'.format(crv))
	if parent and cmds.objExists(parent):
		cmds.parent(crv, parent)
	return crv

# get curve cv number
def getCurveCvNum(crv):
	crvShape = cmds.listRelatives(crv, s = True)[0]
	span = cmds.getAttr('{}.spans'.format(crvShape))
	degree = cmds.getAttr('{}.degree'.format(crvShape))
	cvNum = span + degree
	return cvNum

# cluster curve
def clusterCurve(crv, relatives = False):
	CrvName = naming.Naming(crv)
	cvNum = getCurveCvNum(crv)
	clsHndList = []
	for i in range(cvNum):
		NamingCls = naming.Naming(type = 'cluster', side = CrvName.side, part = CrvName.part, index = CrvName.index, suffix = i + 1)
		clsNodes = cmds.cluster('{}.cv[{}]'.format(crv, i), rel = relatives)
		cmds.rename(clsNodes[0], NamingCls.name)
		NamingCls.type = 'clusterHandle'
		clsHnd = cmds.rename(clsNodes[1], NamingCls.name)
		cmds.setAttr('{}.v'.format(clsHnd), 0)
		clsHndList.append(clsHnd)
	return clsHndList

# get closest point on curve
def getClosestPointOnCurve(curve, pos, space='world'):
	if space == 'world':
		MSpace = OpenMaya.MSpace.kWorld
	else:
		MSpace = OpenMaya.MSpace.kObject
	if isinstance(pos, basestring):
		pos = cmds.xform(pos, q = True, t = True, ws = True)
	MPoint = apiUtils.setMPoint(pos)
	MFnCurve = __setMFnNurbsCurve(curve)
	paramUtill = OpenMaya.MScriptUtil()
	paramPtr = paramUtill.asDoublePtr()

	if not MFnCurve.isPointOnCurve(MPoint):
		# given pos is not on curve
		# find closest point
		MPoint = MFnCurve.closestPoint(MPoint, paramPtr, 0.001, MSpace)
	MFnCurve.getParamAtPoint(MPoint, paramPtr, 0.001, MSpace)

	param = paramUtill.getDouble(paramPtr)
	pos = [MPoint.x, MPoint.y, MPoint.z]
	return param, pos

# get point at curve's param
def getPointAtParam(curve, param, space='object'):
	if space == 'world':
		MSpace = OpenMaya.MSpace.kWorld
	else:
		MSpace = OpenMaya.MSpace.kObject
	MFnCurve = __setMFnNurbsCurve(curve)
	MPoint = OpenMaya.MPoint()
	if not MFnCurve.isParamOnCurve(param):
		logger.warn('given param {} is not on curve {}, skipped'.format(param, curve))
		return None
	else:
		MFnCurve.getPointAtParam(param, MPoint, MSpace)
		return [MPoint.x, MPoint.y, MPoint.z] 

# get curve param range
def getCurveParamRange(curve):
	shapeNode = cmds.listRelatives(curve, s = True)[0]
	minMax = cmds.getAttr('{}.minMaxValue'.format(shapeNode))[0]
	return [minMax[0], minMax[1]]

# sub functions
# get nurbs curve info
def __getCurveInfo(curve, type='python'):
	'''
	return curve info:
	- controlVertices: an array of control vertices
	- knots: an array of knots
	- degree: the degree to create the curve with
	- form : either kOpen, kClosed, kPeriodic
	- name: curve name
	- type: shape type, nurbsCurve

	paramters:

	type(string): return type, python/MObj, default is python
	'''

	MFnCurve = __setMFnNurbsCurve(curve) # set MFnNurbsCurve to query

	controlVertices = OpenMaya.MPointArray()
	MFnCurve.getCVs(controlVertices, OpenMaya.MSpace.kObject)

	knots = OpenMaya.MDoubleArray()
	MFnCurve.getKnots(knots)

	degree = MFnCurve.degree()

	form = MFnCurve.form()
	
	if type != 'MObj':
		controlVertices = apiUtils.convertMPointArrayToList(controlVertices)
		knots = apiUtils.convertMArrayToList(knots)

	curveInfo = {'name': curve,
			     'controlVertices': controlVertices,
			     'knots': knots,
			     'degree': degree,
			     'form': form,
			     'type': 'nurbsCurve'}

	return curveInfo

# load nurbs curve info
def __convertCurveInfo(curveInfo):
	# convert everything to MObj
	curveInfo['controlVertices'] = apiUtils.convertListToMPointArray(curveInfo['controlVertices'])
	curveInfo['knots'] = apiUtils.convertListToMArray(curveInfo['knots'])

	return curveInfo

# create nurbs surface
def __createCurve(curveInfo, curveName):
	# create curve
	MObj = apiUtils.setMObj(curveName)
	MFnNurbsCurve = OpenMaya.MFnNurbsCurve()
	MFnNurbsCurve.create(curveInfo['controlVertices'], curveInfo['knots'], 
				   curveInfo['degree'], curveInfo['form'], 
				   False, True, MObj)

	return curveName

# set MFnNurbsSurface
def __setMFnNurbsCurve(curve):
	MDagPath, MComponents = apiUtils.setMDagPath(curve)
	MFnCurve = OpenMaya.MFnNurbsCurve(MDagPath)
	return MFnCurve