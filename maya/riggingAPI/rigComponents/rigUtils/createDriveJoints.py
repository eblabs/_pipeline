## create drive joints function

## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.apiUtils as apiUtils
import riggingAPI.joints as joints

def createDriveJoints(lBpJnts, sParent = None, sSuffix = '', sRemove = '', bBind = False, lBindNameOverride = None):
	lJnts = []
	lBindJnts = []
	sBindParent = None
	for i, sBpJnt in enumerate(lBpJnts):
		## jnt
		oJntName = naming.oName(sBpJnt)
		oJntName.sType = 'jnt'
		if sRemove:
			oJntName.sPart = oJntName.sPart.replace(sRemove, '')
		oJntName.sPart = '%s%s' %(oJntName.sPart, sSuffix)
		sJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sParent)
		sParent = sJnt
		lJnts.append(sJnt)

		## bind jnt
		if bBind:
			if lBindNameOverride:
				oJntName = naming.oName(lBindNameOverride[i])
			oJntName.sType = 'bindJoint'
			sBindJnt = joints.createJntOnExistingNode(sBpJnt, sBpJnt, oJntName.sName, sParent = sBindParent)
			sBindParent = sBindJnt
			lBindJnts.append(sBindJnt)
			## tag drv joint
			tagBindJoint(sBindJnt, sJnt)

	return lJnts, lBindJnts

def tagBindJoint(sBindJnt, sDrvJnt):
	cmds.addAttr(sBindJnt, ln = 'sConnect', dt = 'string')
	cmds.setAttr('%s.sConnect' %sBindJnt, sDrvJnt, type = 'string', lock = True)

def labelBindJoint(sBindJnt):
	oName = naming.oName(sBindJnt)
	
	if 'left' in oName.sSideKey:
		iSide = 1
		sSuffix = oName.sSideKey.replace('left', '')
	elif 'right' in oName.sSideKey:
		iSide = 2
		sSuffix = oName.sSideKey.replace('right', '')
	else:
		iSide = 0
		sSuffix = oName.sSideKey.replace('middle', '')

	sLabelName = sBindJnt.replace('%s_%s_' %(oName.sType, oName.sSide), '')
	if sSuffix:
		sLabelName = sLabelName.replace(oName.sPart, '%s%s' %(oName.sPart, sSuffix.title()))
	## label
	cmds.setAttr('%s.side' %sBindJnt, iSide)
	cmds.setAttr('%s.type' %sBindJnt, 18)
	cmds.setAttr('%s.otherType' %sBindJnt, sLabelName, type = 'string')



