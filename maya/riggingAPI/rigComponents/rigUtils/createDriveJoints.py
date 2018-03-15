## create drive joints function

## import
import maya.cmds as cmds
## import libs
import namingAPI.naming as naming
import common.apiUtils as apiUtils
import riggingAPI.joints as joints

def createDriveJoints(lBpJnts, sParent = None, sSuffix = '', sRemove = '', bBind = False, sBindParent = None, lBindNameOverride = None):
	lJnts = []
	lBindJnts = []
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
			cmds.parentConstraint(sJnt, sBindJnt, mo = False)
			for sAxis in ['X', 'Y', 'Z']:
				cmds.connectAttr('%s.scale%s' %(sJnt, sAxis), '%s.scale%s' %(sBindJnt, sAxis))

	return lJnts, lBindJnts

