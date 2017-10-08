## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

## libs Import
import common.files as files
import common.transforms as transforms
import joints

#### Functions
def saveBlueprintJnts(sPath):
	if cmds.objExists(files.sBlueprintGrp):
		lJnts = cmds.listRelatives(files.sBlueprintGrp, c = True, ad = True, type = 'joint')
		joints.saveJointInfo(lJnts, sPath)
	else:
		cmds.warning('%s does not exist, skipped' %files.sBlueprintGrp)

def buildBlueprintJnts(sPath):
	if os.path.exists(sPath):
		joints.buildJointsFromJointsInfo(sPath, sGrp = files.sBlueprintGrp)
	else:
		cmds.warning('blueprint file does not exist, cannot build the joints')




#### Sub Functions
