# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.api.OpenMaya as OpenMaya2
import math

# -- import lib

# ---- import end ----

# ---- global variable
rotateOrderList = [OpenMaya.MTransformationMatrix.kXYZ, 
				   OpenMaya.MTransformationMatrix.kYZX,
				   OpenMaya.MTransformationMatrix.kZXY,
				   OpenMaya.MTransformationMatrix.kXZY,
				   OpenMaya.MTransformationMatrix.kYXZ,
				   OpenMaya.MTransformationMatrix.kZYX,]

# MMatrix
# compose MMatrix
def composeMMatrix(translate=[0,0,0], rotate=[0,0,0], scale=[1,1,1], rotateOrder=0):
	'''
	compose MMatrix

	parameters:

	translate(list): given translation, default is [0,0,0]
	rotate(list): given rotation, default is [0,0,0]
	scale(list): given scale, default is [1,1,1]
	rotateOrder(int): given rotate order, default is 0(xyz)
	'''

	# create MMatrix object
	MTransformationMatrix = OpenMaya.MTransformationMatrix()

	# create MVector for translation
	MVector = OpenMaya.MVector(translate[0], translate[1], translate[2])

	# convert roation to radians
	rotate = __convertRotationToRadians(rotate)

	# create MDoubleArray for rotation
	MRotate = createMDoubleArray(rotate)

	# create MDoubleArray for scale
	MScale = createMDoubleArray(scale)

	# set MMatrix
	MTransformationMatrix.setTranslation(MVector, OpenMaya.MSpace.kWorld)
	MTransformationMatrix.setRotation(MRotate.asDoublePtr(), 
									  rotateOrderList[rotateOrder], 
									  OpenMaya.MSpace.kWorld)
	MTransformationMatrix.setScale(MScale.asDoublePtr(), OpenMaya.MSpace.kWorld)
	
	# get MMatrix and return
	return MTransformationMatrix.asMatrix()

# get MMatrix from node
def getMMatrixFromNode(node, space='world'):
	'''
	get MMatrix from node

	parameters:

	node(string): given node
	space(string): matrix space, world/local, default is 'world'
	'''
	if space == 'world':
		matrixList = cmds.getAttr('{}.worldMatrix[0]'.format(node))
	elif space == 'local':
		matrixList = cmds.getAttr('{}.matrix[0]'.format(node))
	MMatrix = OpenMaya.MMatrix()
	OpenMaya.MScriptUtil.createMatrixFromList(matrixList, MMatrix)
	return MMatrix

# decompose MMatrix
def decomposeMMatrix(MMatrix, space = 'world', rotateOrder = 0):
	'''
	decompose MMatrix

	parameters:

	MMatrix(MMatrix): MMatrix object
	space(string): world/local, default is 'world'
	rotateOrder(int): set rotateOrder, default is 0(xyz)	
	'''

	if space == 'world':
		MSpace = OpenMaya.MSpace.kWorld
	else:
		MSpace = OpenMaya.MSpace.kObject

	MTransformationMatrix = OpenMaya.MTransformationMatrix(MMatrix)
	
	MTranslate = MTransformationMatrix.getTranslation(MSpace)
	
	## there is a maya api bug, getRotation seems not working, 
	## have to get a quaternion then convert to euler
	MQuaternion = MTransformationMatrix.rotation()
	MQuaternionV2 = OpenMaya2.MQuaternion(MQuaternion.x, MQuaternion.y, 
										  MQuaternion.z, MQuaternion.w)

	MScale = createMDoubleArray([1,1,1])
	MScalePtr = MScale.asDoublePtr()
	MTransformationMatrix.getScale(MScalePtr, MSpace)

	translate = [MTranslate(0), 
				 MTranslate(1), 
				 MTranslate(2)]
	rotate = convertMQuaternionToEluer(MQuaternionV2, rotateOrder = rotateOrder)
	scaleX = OpenMaya.MScriptUtil.getDoubleArrayItem(MScalePtr, 0)
	scaleY = OpenMaya.MScriptUtil.getDoubleArrayItem(MScalePtr, 1)
	scaleZ = OpenMaya.MScriptUtil.getDoubleArrayItem(MScalePtr, 2)
	scale = [scaleX, scaleY, scaleZ]

	return [translate, rotate, scale]

# convert MMatrix to list
def convertMMatrixToList(MMatrix, type='MMatrix'):
	'''
	MMatrix(MMatrix/MMatrixV2)
	type(string): MMatrix/MMatrixV2
	'''
	matrix = []
	for i in range(4):
		for j in range(4):
			if type == 'MMatrix':
				matrix.append(MMatrix(i, j))
			else:
				matrix.append(MMatrix.getElement(i, j))
	return matrix

# convert list to MMatrix
def convertListToMMatrix(matrix, type='MMatrix'):
	'''
	type(string): MMatrix/MMatrixV2
	'''
	if type == 'MMatrix':
		MMatrix = OpenMaya.MMatrix()
		OpenMaya.MScriptUtil.createMatrixFromList(matrix, MMatrix)
		return MMatrix
	else:
		MMatrixV2 = OpenMaya2.MMatrix(matrix)
		return MMatrixV2

# array
# create MDoubleArray
def createMDoubleArray(list):
	MDoubleArray = OpenMaya.MScriptUtil()
	MDoubleArray.createFromList(list,3)
	return MDoubleArray

# rotation
# convert MQuaternion to Eluer
def convertMQuaternionToEluer(MQuaternionV2, rotateOrder=0):
	MQuatOrig = OpenMaya2.MQuaternion()
	MQuatSlerp = __MQuaternionSlerp(MQuatOrig, MQuaternionV2, 1)
	MEluer = MQuatSlerp.asEulerRotation()
	# reset rotate order
	MEluer.reorderIt(rotateOrder)
	# return eluer list
	return [math.degrees(MEluer.x), math.degrees(MEluer.y),
			math.degrees(MEluer.z)]

# OpenMaya object
# MObj
def setMObj(node):
	'''
	return a MObject
	'''
	MObj = OpenMaya.MObject()
	MSel = OpenMaya.MSelectionList()
	MSel.add(node)
	MSel.getDependNode(0, MObj)
	return MObj

# MDagPath
def setMDagPath(node):
	'''
	return MDagPath and MObject
	'''
	MDagPath = OpenMaya.MDagPath()
	MSel = OpenMaya.MSelectionList()
	MSel.add(node)
	MComponents = OpenMaya.MObject()
	MSel.getDagPath(0, MDagPath, MComponents)
	return MDagPath, MComponents

# MPoint
def setMPoint(pos, type='MPoint'):
	'''
	return a MPoint
	'''
	if type == 'MPoint':
		MPoint = OpenMaya.MPoint(pos[0], pos[1], pos[2])
	elif type == 'MFloatPoint':
		MPoint = OpenMaya.MFloatPoint(pos[0], pos[1], pos[2])
	return MPoint

# distance between two points
def distance(pointA, pointB):
	MPointA = setMPoint(pointA)
	MPointB = setMPoint(pointB)
	dis = MPointA.distanceTo(MPointB)
	return dis

# convert MPointArray to list
def convertMPointArrayToList(MPntArray):
	pntList = []
	for i in range(MPntArray.length()):
		pntList.append([MPntArray[i].x, MPntArray[i].y, MPntArray[i].z])
	return pntList

# convert MDoubleArray to list
def convertMArrayToList(MArray):
	array = []
	for i in range(MArray.length()):
		array.append(MArray[i])
	return array

# convert list to MPointArray
def convertListToMPointArray(array, type='MPointArray'):
	if type == 'MPointArray':
		MArray = OpenMaya.MPointArray()

	elif type == 'MFloatPointArray':
		MArray = OpenMaya.MFloatPointArray()

	pntType = type.replace('Array', '')

	for pos in array:
		MPoint = setMPoint(pos, type = pntType)
		MArray.append(MPoint)

	return MArray

# convert list to MArray
def convertListToMArray(array, type='MDoubleArray'):
	if type == 'MDoubleArray':
		MArray = OpenMaya.MDoubleArray()
	elif type == 'MIntArray':
		MArray = OpenMaya.MIntArray()
	elif type == 'MFloatArray':
		MArray = OpenMaya.MFloatArray()

	for item in array:
		MArray.append(item)

	return MArray

# sub function
# convert single degree to radian
def __convertDegreeToRadian(degree):
	return math.radians(degree)

# convert roatation to radians
def __convertRotationToRadians(rotate):
	radians = []
	for rotEach in rotate:
		radianEach = __convertDegreeToRadian(rotEach)
		radians.append(radianEach)
	return radians

# get MQuaternion from matrix in OpenMaya2
def __getMQuaternionFromMatrixV2(matrix):
	'''
	matrix(list): node's matrix
	''' 
	MMatrix = OpenMaya2.MMatrix(matrix)
	MTransform = OpenMaya2.MTransformationMatrix(MMatrix)

	return MTransform.roatation(asQuaternion = True)

# MQuaternion slerp
def __MQuaternionSlerp(MQuatA, MQuatB, weight = 0.5):
	'''
	Returns the quaternion at a given interpolation value along the shortest 
	path between two quaternions

	MQuatA weight = 1 - weight
	MQuatB weight = weight
	'''
	MQuatSlerp = OpenMaya2.MQuaternion.slerp(MQuatA, MQuatB, 1 - weight, 0)
	return MQuatSlerp



