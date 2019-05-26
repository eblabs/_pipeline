#=================#
# IMPORT PACKAGES #
#=================#

## import system packages
import sys
import os

## import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

## import utils
import utils.common.naming as naming
import utils.common.attributes as attributes
import utils.common.apiUtils as apiUtils
import utils.common.variables as variables
import utils.common.hierarchy as hierarchy
#=================#
#   GLOBAL VARS   #
#=================#

#=================#
#      CLASS      #
#=================#

#=================#
#    FUNCTION     #
#=================#
def create_curve(name, controlVertices, knots, **kwargs):
	'''
	create curve with given information

	Args:
		name(str): curve name
		controlVertices(list): control vertices
		knots(list): knots
		degree(int)[1]: curve's degree
		form(int)[1]: curve's form
	Returns:
		transform, shape node
	'''
	# vars
	degree = variables.kwargs('degree', 1, kwargs, shortName='d')
	form = variables.kwargs('form', 1, kwargs)

	if not cmds.objExists(name):
		cmds.createNode('transform', name=name)
	MObj = apiUtils.set_MObj(name)
	MFnNurbsCurve = OpenMaya.MFnNurbsCurve()
	MObj = MFnNurbsCurve.create(controlVertices, knots, degree, form,
						 		False, True, MObj)

	# rename shape
	MDagPath = OpenMaya.MDagPath.getAPathTo(MObj)
	shape = MDagPath.partialPathName()
	shape = cmds.rename(shape, name+'Shape')

	return name, shape

def create_guide_line(name, attrs, reference=True, parent=None):
	'''
	create guide line

	Args:
		name(str): guide line's name
		attrs(list): input connections to the cv points
					example: [['node1.tx', 'node1.ty', 'node1.tz'],
							  ['node2.tx', 'node2.ty', 'node2.tz']]
	Kwargs:
		reference(bool)[True]: if set shape to reference
		parent(str)[None]: parent guide line to the given node
	Returns:
		curve(str): guide line's transform
	'''
	crv = cmds.curve(d=1, p=[[0,0,0],[0,0,0]], name=name)
	crvShape = cmds.listRelatives(crv, s=True)[0]
	crvShape = cmds.rename(crvShape, crv+'Shape')
	if reference:
		cmds.setAttr(crvShape+'.overrideEnabled', 1)
		cmds.setAttr(crvShape+'.overrideDisplayType', 2)
	attributes.lock_hide_attrs(crv, attributes.Attr.all)

	hierarchy.parent_node(crv, parent)
	attributes.connect_attrs(attrs[0]+attrs[1],
							 [crvShape+'.controlPoints[0].xValue',
							  crvShape+'.controlPoints[0].yValue',
							  crvShape+'.controlPoints[0].zValue',
							  crvShape+'.controlPoints[1].xValue',
							  crvShape+'.controlPoints[1].yValue',
							  crvShape+'.controlPoints[1].zValue'])
	return crv

def get_curve_info(curve):
	'''
	get curve shape info

	Args:
		curve: nurbs curve shape node
	Returns:
		curveInfo(dict): name
						 controlVertices
						 knots
						 degree
						 form
	'''
	MFnCurve = __setMFnNurbsCurve(curve)

	MPntArray_cvs = MFnCurve.cvPositions(OpenMaya.MSpace.kObject)
	MDoubleArray_knots = MFnCurve.knots()

	degree = MFnCurve.degree

	form = MFnCurve.form
	
	controlVertices = apiUtils.convert_MPointArray_to_list(MPntArray_cvs)
	knots = apiUtils.convert_MDoubleArray_to_list(MDoubleArray_knots)

	curveInfo = {'name': curve,
			     'controlVertices': controlVertices,
			     'knots': knots,
			     'degree': degree,
			     'form': form}

	return curveInfo

def set_curve_points(curve, points):
	'''
	set curve shape points positions

	Args:
		curve(str): curve shape node
		points(list): curve cv positions
	'''
	MPointArray = OpenMaya.MPointArray(points)

	# get MFnNurbsCurve
	MFnNurbsCurve = __setMFnNurbsCurve(curve)

	# set pos
	MFnNurbsCurve.setCVPositions(MPointArray)

#=================#
#  SUB FUNCTION   #
#=================#
def __setMFnNurbsCurve(curve):
	MDagPath = apiUtils.set_MDagPath(curve)
	MFnCurve = OpenMaya.MFnNurbsCurve(MDagPath)
	return MFnCurve