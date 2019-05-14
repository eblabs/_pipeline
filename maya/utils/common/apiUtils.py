#=================#
# IMPORT PACKAGES #
#=================#

## import maya packages
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

## import math
import math

## import utils
import naming
import attributes
import variables

#=================#
#   GLOBAL VARS   #
#=================#
from . import Logger

#=================#
#    FUNCTION     #
#=================#
def set_MObj(node):
	'''
	return MObject

	Args:
		node
	'''
	MSel = OpenMaya.MSelectionList()
	MSel.add(node)
	MObj = MSel.getDependNode(0)
	return MObj

def set_MDagPath(node):
	'''
	return MDagPath

	Args:
		node
	'''
	MSel = OpenMaya.MSelectionList()
	MSel.add(node)
	MDagPath = MSel.getDagPath(0)
	return MDagPath

def convert_MPointArray_to_list(MPointArray):
	'''
	convert MPointArray to python list
	'''
	pointList = []
	for i in range(len(MPointArray)):
		pointList.append([MPointArray[i].x,
						  MPointArray[i].y,
						  MPointArray[i].z])
	return pointList

def convert_MDoubleArray_to_list(MDoubleArray):
	'''
	convert MDoubleArray (or similiar array) to python list
	'''
	arrayList = []
	for i in range(len(MDoubleArray)):
		arrayList.append(MDoubleArray[i])
	return arrayList

def compose_matrix(**kwargs):
	'''
	compose matrix

	Kwargs:
		translate(list)
		rotate(list)
		scale(list)
		rotateOrder(int)
	'''
	# vars
	translate = variables.kwargs('translate', [0,0,0], kwargs, shortName='t')
	rotate = variables.kwargs('rotate', [0,0,0], kwargs, shortName='r')
	scale = variables.kwargs('scale', [1,1,1], kwargs, shortName='s')
	rotateOrder = variables.kwargs('rotateOrder', 0, kwargs, shortName='ro')
	# create MMatrix object
	MTransformationMatrix = OpenMaya.MTransformationMatrix()

	# create MVector for translation
	MVector = OpenMaya.MVector(translate[0], translate[1], translate[2])

	# create MDoubleArray for rotation
	MRotate = OpenMaya.MEulerRotation(math.radians(rotate[0]),
								   	  math.radians(rotate[1]),
								   	  math.radians(rotate[2]),
								   	  rotateOrder)

	# set MMatrix
	MTransformationMatrix.setTranslation(MVector, OpenMaya.MSpace.kWorld)
	MTransformationMatrix.setRotation(MRotate)
	MTransformationMatrix.setScale(scale, OpenMaya.MSpace.kWorld)
	
	# get MMatrix
	MMatrix = MTransformationMatrix.asMatrix()

	matrix = convert_MMatrix_to_list(MMatrix)

	return matrix

def decompose_matrix(matrix, **kwargs):
	'''
	decompose matrix

	Args:
		matrix(list)
	Kwargs:
		rotateOrder(int)
	'''
	# vars
	rotateOrder = variables.kwargs('rotateOrder', 0, kwargs, shortName='ro')

	MMatrix = OpenMaya.MMatrix(matrix)
	MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)
	
	MTranslate = MTransformationMatrix.translation(OpenMaya.MSpace.kWorld)
	MRotate = MTransformationMatrix.rotation(asQuaternion=False)
	MRotate.reorderIt(rotateOrder)
	scale = MTransformationMatrix.scale(OpenMaya.MSpace.kWorld)

	translate = [MTranslate.x, MTranslate.y, MTranslate.z]
	rotate = [math.degrees(MRotate.x), math.degrees(MRotate.y), math.degrees(MRotate.z)]
	
	return [translate, rotate, scale]

def convert_MMatrix_to_list(MMatrix):
	'''
	convert MMatrix to list

	Args:
		MMatrix
	'''
	matrix = []
	for i in range(4):
		for j in range(4):
			matrix.append(MMatrix.getElement(i, j))
	return matrix