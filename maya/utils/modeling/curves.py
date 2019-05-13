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
reload(apiUtils)
#=================#
#   GLOBAL VARS   #
#=================#

#=================#
#      CLASS      #
#=================#

#=================#
#    FUNCTION     #
#=================#
def create_curve(name, controlVertices, knots, degree=1, form=1):
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

#=================#
#  SUB FUNCTION   #
#=================#
def __setMFnNurbsCurve(curve):
	MDagPath = apiUtils.set_MDagPath(curve)
	MFnCurve = OpenMaya.MFnNurbsCurve(MDagPath)
	return MFnCurve