## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

#### Functions
def setMObj(sNode):
	mObj = OpenMaya.MObject()
	mSel = OpenMaya.MSelectionList()
	mSel.add(sNode)
	mSel.getDependNode(0, mObj)
	return mObj

def setDagPath(sNode):
	mDagPath = OpenMaya.MDagPath()
	mSel = OpenMaya.MSelectionList()
	mSel.add(sNode)
	mComponents = OpenMaya.MObject()
	mSel.getDagPath(0, mDagPath, mComponents)
	return mDagPath, mComponents

def createUintPtr():
	mUtil = OpenMaya.MScriptUtil()
	mUtil.createFromInt(0)
	uIntPtr = mUtil.asUintPtr()
	return uIntPtr

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