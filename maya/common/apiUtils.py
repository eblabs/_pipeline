## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

#### Functions
def setMObj(sNode):
	'''
	return a mObject
	'''
	mObj = OpenMaya.MObject()
	mSel = OpenMaya.MSelectionList()
	mSel.add(sNode)
	mSel.getDependNode(0, mObj)
	return mObj

def setDagPath(sNode):
	'''
	return mDagPath and mObject
	'''
	mDagPath = OpenMaya.MDagPath()
	mSel = OpenMaya.MSelectionList()
	mSel.add(sNode)
	mComponents = OpenMaya.MObject()
	mSel.getDagPath(0, mDagPath, mComponents)
	return mDagPath, mComponents

def setMPoint(lPos):
	'''
	return a mPoint
	'''
	mPoint = OpenMaya.MPoint(lPos[0], lPos[1], lPos[2])
	return mPoint

def convertMPointArrayToList(mPntArray):
	lPntList = []
	for i in range(mPntArray.length()):
		lPntList.append([mPntArray[i].x, mPntArray[i].y, mPntArray[i].z])
	return lPntList

def convertMDoubleArrayToList(mDoubleArray):
	lList = []
	for i in range(mDoubleArray.length()):
		lList.append(mDoubleArray[i])
	return lList

def createMDoubleArray(lList):
	mDoubleArray = OpenMaya.MScriptUtil()
	mDoubleArray.createFromList(lList,3)
	return mDoubleArray

# ----------------- mMatrix ----------------------
def createMMatrixFromTransformInfo(lTranslate = [0,0,0], lRotate = [0,0,0], lScale = [1,1,1], lShear = [0,0,0], iRotateOrder = 0):
	lRotateOrder = [OpenMaya.MTransformationMatrix.kXYZ, 
					OpenMaya.MTransformationMatrix.kYZX,
					OpenMaya.MTransformationMatrix.kZXY,
					OpenMaya.MTransformationMatrix.kXZY,
					OpenMaya.MTransformationMatrix.kYXZ,
					OpenMaya.MTransformationMatrix.kZYX,]

	mTransformationMatrix = OpenMaya.MTransformationMatrix()

	mVectorTranslate = OpenMaya.MVector(lTranslate[0], lTranslate[1], lTranslate[2])
	mDoubleArrayRotate = createMDoubleArray(lRotate)
	mDoubleArrayScale = createMDoubleArray(lScale)
	mDoubleArrayShear = createMDoubleArray(lShear)

	mTransformationMatrix.setTranslation(mVectorTranslate, OpenMaya.MSpace.kWorld)
	mTransformationMatrix.setRotation(mDoubleArrayRotate.asDoublePtr(), lRotateOrder[iRotateOrder], OpenMaya.MSpace.kWorld)
	mTransformationMatrix.setScale(mDoubleArrayScale.asDoublePtr(), OpenMaya.MSpace.kWorld)
	mTransformationMatrix.setShear(mDoubleArrayShear.asDoublePtr(), OpenMaya.MSpace.kWorld)

	mMatrix = mTransformationMatrix.asMatrix()

	return mMatrix

def createMMatrixFromTransformNode(sNode, sSpace = 'world'):
	if sSpace == 'world':
		lMatrix = cmds.getAttr('%s.worldMatrix[0]' %sNode)
	elif sSpace == 'object':
		lMatrix = cmds.getAttr('%s.matrix[0]' %sNode)
	mMatrix = OpenMaya.MMatrix()
	OpenMaya.MScriptUtil.createMatrixFromList(lMatrix, mMatrix)
	return mMatrix

def convertMMatrixToList(mMatrix):
	lMatrix = []
	for i in range(4):
		for j in range(4):
			lMatrix.append(mMatrix(i, j))
	return lMatrix

def convertListToMMatrix(lMatrix):
	mMatrix = OpenMaya.MMatrix()
	OpenMaya.MScriptUtil.createMatrixFromList(lMatrix, mMatrix)
	return mMatrix

def getLocalMatrixInNode(sNode, sParent, sNodeAttr = 'worldMatrix[0]', sParentAttr = 'worldMatrix[0]'):
	lMatrix_node = cmds.getAttr('%s.%s' %(sNode, sNodeAttr))
	lMatrix_parent = cmds.getAttr('%s.%s' %(sParent, sParentAttr))
	mMatrix_node = convertListToMMatrix(lMatrix_node)
	mMatrix_parent = convertListToMMatrix(lMatrix_parent)
	mMatrixInverse_parent = mMatrix_parent.inverse()
	mMatrix_local = mMatrix_node * mMatrixInverse_parent
	lMatrixLocal = convertMMatrixToList(mMatrix_local)
	return lMatrixLocal

def decomposeMMatrix(mMatrix, sSpace = 'world', iRotateOrder = 0):
	if sSpace == 'world':
		mSpace = OpenMaya.MSpace.kWorld
	else:
		mSpace = OpenMaya.MSpace.kObject
	mTransformationMatrix = OpenMaya.MTransformationMatrix(mMatrix)
	
	mDoubleArrayTranslate = mTransformationMatrix.getTranslation(mSpace)
	
	## there is a maya api bug, getRotation seems not work, have to get a quaternion then convert to euler
	mQuaternion = mTransformationMatrix.rotation()
	mRotation = mQuaternion.asEulerRotation()
	mRotation.reorderIt(iRotateOrder)

	mDoubleArrayScale = createMDoubleArray([1,1,1])
	mDoubleArrayScalePtr = mDoubleArrayScale.asDoublePtr()
	mTransformationMatrix.getScale(mDoubleArrayScalePtr, mSpace)

	lTranslate = [mDoubleArrayTranslate(0), mDoubleArrayTranslate(1), mDoubleArrayTranslate(2)]
	lRotate = [mRotation.x, mRotation.y, mRotation.z]
	fScaleX = OpenMaya.MScriptUtil.getDoubleArrayItem(mDoubleArrayScalePtr, 0)
	fScaleY = OpenMaya.MScriptUtil.getDoubleArrayItem(mDoubleArrayScalePtr, 1)
	fScaleZ = OpenMaya.MScriptUtil.getDoubleArrayItem(mDoubleArrayScalePtr, 2)
	lScale = [fScaleX, fScaleY, fScaleZ]

	return [lTranslate, lRotate, lScale]

def decomposeMatrix(lMatrix, iRotateOrder = 0):
	mMatrix = OpenMaya.MMatrix()
	OpenMaya.MScriptUtil.createMatrixFromList(lMatrix, mMatrix)
	lTransformInfo = decomposeMMatrix(mMatrix, iRotateOrder = iRotateOrder)
	return lTransformInfo


