## External Import
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import time

#### Functions
def getAvgValueFromList(lList):
	fValue = 0
	iList = len(lList)
	for v in lList:
		fValue += v / float(iList)
	return fValue