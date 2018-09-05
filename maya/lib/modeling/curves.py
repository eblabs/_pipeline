# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import os
import os

# -- import time
import time

# -- import maya lib
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import math

# -- import lib
import common.apiUtils as apiUtils
import common.files.files as files
# ---- import end ----

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
	MFnSurface.getKnots(knots)

	degree = MFnSurface.degree()

	form = MFnSurface.form()
	
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
	controlVertices = apiUtils.convertListToMPointArray(curveInfo['controlVertices'])
	knots = apiUtils.convertListToMArray(curveInfo['knots'])

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