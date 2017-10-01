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