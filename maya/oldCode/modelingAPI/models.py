## External Import
import maya.cmds as cmds
import maya.mel as mel

## lib import
import namingAPI.naming as naming

## functions
def writeModelInfo(sNode):
	lResGrp = cmds.listRelatives(sNode, c = True)
	sResString = ''
	for sResGrp in lResGrp:
		oGrpName = naming.oName(sResGrp)
		sRes = oGrpName.sRes
		if sRes:
			sResString += '%s,' %sRes
			cmds.addAttr(sNode, ln = sRes, dt = 'string')
			cmds.setAttr('%s.%s' %(sNode, sRes), sResGrp, type = 'string', lock = True)
	cmds.addAttr(sNode, ln = 'resolution', dt = 'string')
	cmds.setAttr('%s.resolution' %sNode, sResString[:-1], type = 'string', lock = True)

def getModelInfo(sNode):
	bRes = cmds.attributeQuery('resolution', node = sNode, exists = True)
	if bRes:
		sResString = cmds.getAttr('%s.resolution' %sNode)
		lRes = sResString.split(',')
		dModelInfo = {'resolution': lRes}
		dModelInfo.update({'modelGroups': {}})
		for sRes in lRes:
			sResGrp = cmds.getAttr('%s.%s' %(sNode, sRes))
			dModelInfo['modelGroups'].update({sRes: sResGrp})
	else:
		lResGrp = cmds.listRelatives(sNode, c = True)
		lRes = []
		dModelGrpInfo = {}
		for sResGrp in lResGrp:
			oGrpName = naming.oName(sResGrp)
			sRes = oGrpName.sRes
			if sRes:
				lRes.append(sRes)
				dModelGrpInfo.update({sRes: sResGrp})
		dModelInfo = {'resolution': lRes,
						'modelGroups': dModelGrpInfo}

	return dModelInfo


