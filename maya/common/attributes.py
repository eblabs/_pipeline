## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## lib import
import namingAPI.naming as naming

## functions
def lockHideAttrs(lAttrs, sNode = None):
	for sAttr in lAttrs:
		if '.' not in sAttr:
			sAttr = '%s.%s' %(sNode, sAttr)
		cmds.setAttr(sAttr, keyable = False, lock = True, channelBox = False)

def unlockAttrs(lAttrs, sNode = None, bKeyable = True, bChannelBox = True):
	for sAttr in lAttrs:
		if '.' not in sAttr:
			sAttr = '%s.%s' %(sNode, sAttr)
		cmds.setAttr(sAttr, lock = False, channelBox = bChannelBox)
		cmds.setAttr(sAttr, keyable = bKeyable)

def connectAttrs(lDriverAttrs, lDrivenAttrs, sDriver = None, sDriven = None, bForce = True):
	for i, sDriverAttr in enumerate(lDriverAttrs):
		if '.' not in sDriverAttr:
			sDriverAttr  = '%s.%s' %(sDriver, sDriverAttr)
		if '.' not in lDrivenAttrs[i]:
			sDrivenAttr = '%s.%s' %(sDriven, lDrivenAttrs[i])
		else:
			sDrivenAttr = lDrivenAttrs[i]
		lConnections = cmds.listConnections(sDrivenAttr, s = True, d = False, p = True, scn = True)
		bLock = cmds.getAttr(sDrivenAttr, lock = True)
		if not lConnections and not bLock:
			cmds.connectAttr(sDriverAttr, sDrivenAttr)
		elif lConnections and bLock:
			if not bForce:
				cmds.warning('%s already has connection from %s, skipped' %(sDrivenAttr, lConnections[0]))
			else:
				cmds.disconnectAttr(lConnections[0], sDrivenAttr)
				cmds.setAttr(sDrivenAttr, lock = False)
				cmds.connectAttr(sDriverAttr, sDrivenAttr, f = True)
				cmds.setAttr(sDrivenAttr, lock = True)
		elif lConnections:
			if not bForce:
				cmds.warning('%s already has connection from %s, skipped' %(sDrivenAttr, lConnections[0]))
			else:
				cmds.disconnectAttr(lConnections[0], sDrivenAttr)
				cmds.connectAttr(sDriverAttr, sDrivenAttr, f = True)
		else:
			if not bForce:
				cmds.warning('%s is locked, skipped' %sDrivenAttr)
			else:
				cmds.setAttr(sDrivenAttr, lock = False)
				cmds.connectAttr(sDriverAttr, sDrivenAttr, f = True)
				cmds.setAttr(sDrivenAttr, lock = True)

def enumToSingleAttrs(sEnumAttr, lAttrs, iEnumRange = 2, lValRange = [[0,1]], sEnumObj = None):
	if '.' not in sEnumAttr:
		sEnumAttrName = sEnumAttr
		sEnumAttr = '%s.%s' %(sEnumObj, sEnumAttr)
	else:
		sEnumObj = sEnumAttr.split('.')[0]
		sEnumAttrName = sEnumAttr.split('.')[1]

	oObjName = naming.oName(sEnumObj)
	sSide = oObjName.sSide
	if not sSide:
		sSide = 'middle'
	iIndex = oObjName.iIndex

	sConditionMain = None
	sConditionSave = None
	for i in range(iEnumRange):
		if iIndex:
			sCondition = naming.oName(sType = 'condition', sSide = sSide, sPart = '%s%s' %(sEnumObj, sEnumAttrName.title()), iIndex = iIndex, iSuffix = i).sName
		else:
			sCondition = naming.oName(sType = 'condition', sSide = sSide, sPart = '%s%s' %(sEnumObj, sEnumAttrName.title()), iIndex = i).sName
		cmds.createNode('condition', name = sCondition)
		cmds.connectAttr(sEnumAttr, '%s.firstTerm' %sCondition)
		cmds.setAttr('%s.secondTerm' %sCondition, i)
		if len(lValRange) == iEnumRange:
			lValTrue = lValRange[i][1]
			lValFalse = lValRange[i][0]
		else:
			lValTrue = lValRange[0][1]
			lValFalse = lValRange[0][0]
		cmds.setAttr('%s.colorIfTrueR' %sCondition, lValTrue)
		cmds.setAttr('%s.colorIfFalseR' %sCondition, lValFalse)
		
		if i == 0:
			sConditionMain = sCondition

		if sConditionSave:
			cmds.connectAttr('%s.outColorR' %sCondition, '%s.colorIfFalseR' %sConditionSave)
		sConditionSave = sCondition

	for sAttr in lAttrs:
		connectAttrs(['%s.outColorR' %sConditionMain], [sAttr], bForce = True)

def enumToMultiAttrs(sEnumAttr, lAttrs, iEnumRange = 2, lValRange = [[0,1]], sEnumObj = None):
	if '.' not in sEnumAttr:
		sEnumAttrName = sEnumAttr
		sEnumAttr = '%s.%s' %(sEnumObj, sEnumAttr)
	else:
		sEnumObj = sEnumAttr.split('.')[0]
		sEnumAttrName = sEnumAttr.split('.')[1]

	oObjName = naming.oName(sEnumObj)
	sSide = oObjName.sSide
	if not sSide:
		sSide = 'middle'
	iIndex = oObjName.iIndex

	for i in range(iEnumRange):
		sCondition = naming.oName(sType = 'condition', sSide = sSide, sPart = '%s%s' %(sEnumObj, sEnumAttrName.title()), iIndex = iIndex, iSuffix = i).sName
		cmds.createNode('condition', name = sCondition)
		cmds.connectAttr(sEnumAttr, '%s.firstTerm' %sCondition)
		cmds.setAttr('%s.secondTerm' %sCondition, i)
		if len(lValRange) == iEnumRange:
			lValTrue = lValRange[i][1]
			lValFalse = lValRange[i][0]
		else:
			lValTrue = lValRange[0][1]
			lValFalse = lValRange[0][0]
		cmds.setAttr('%s.colorIfTrueR' %sCondition, lValTrue)
		cmds.setAttr('%s.colorIfFalseR' %sCondition, lValFalse)
		
		if lAttrs[i]:
			connectAttrs(['%s.outColorR' %sCondition], [lAttrs[i]], bForce = True)
