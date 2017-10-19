## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
## libs Import
import common.apiUtils as apiUtils
import common.files as files
import namingAPI.naming as naming
import common.transforms as transforms
import common.attributes as attributes
import common.maths as maths
import controlShapeDict
reload(transforms)
reload(naming)
#### Functions
def getCtrlShape(sCtrl):
	lCtrlShapes = cmds.listRelatives(sCtrl, s = True)
	if lCtrlShapes:
		sCtrlShape = lCtrlShapes[0]
	else:
		sCtrlShape = None
	return sCtrlShape

def addCtrlShape(lCtrls, sCtrlShape, bVis = True, dCtrlShapeInfo = None):
	if dCtrlShapeInfo:
		lCtrlPnts = dCtrlShapeInfo['lCtrlPnts']
		lKnots = dCtrlShapeInfo['lKnots']
		iDegree = dCtrlShapeInfo['iDegree']
		bPeriodic = dCtrlShapeInfo['bPeriodic']
		bOverride = dCtrlShapeInfo['bOverride']
		iOverrideType = dCtrlShapeInfo['iOverrideType']
		iColor = dCtrlShapeInfo['iColor']
	else:
		lCtrlPnts = [[0,0,0], [1,0,0]]
		lKnots = [0,1]
		iDegree = 1
		bPeriodic = False
		bOverride = False
		iOverrideType = 0
		iColor = 0
	sCrv = cmds.curve(p=lCtrlPnts, k=lKnots, d=iDegree, per = bPeriodic)
	sCrvShape = getCtrlShape(sCrv)
	cmds.rename(sCrvShape, sCtrlShape)

	cmds.setAttr('%s.overrideEnabled' %sCtrlShape, bOverride)
	cmds.setAttr('%s.overrideDisplayType' %sCtrlShape, iOverrideType)
	cmds.setAttr('%s.overrideColor' %sCtrlShape, iColor)

	if not bVis:
		cmds.setAttr('%s.v' %sCtrlShape, lock = False)
		cmds.setAttr('%s.v' %sCtrlShape, 0)
		cmds.setAttr('%s.v' %sCtrlShape, lock = True)
	for sCtrl in lCtrls:
		cmds.parent(sCtrlShape, sCtrl, add = True, s = True)
	cmds.delete(sCrv)

def scaleCtrlShape(sCtrl, fScale = 1):
	lPosPivot = cmds.xform(sCtrl, q = True, t = True, ws = True)
	sCtrlShape = getCtrlShape(sCtrl)
	if sCtrlShape:
		lCtrlPnts = __getCtrlShapeControlPoints(sCtrlShape)
		for i, lCtrlPntPos in enumerate(lCtrlPnts):
			vCtrlPnt = maths.vector(lPosPivot, lCtrlPntPos)
			vCtrlPnt = maths.vectorScale(vCtrlPnt, fScale)
			lCtrlPntPosUpdate = maths.getPointFromVectorAndPoint(lPosPivot, vCtrlPnt)
			cmds.setAttr('%s.controlPoints[%d]' %(sCtrlShape, i), lCtrlPntPosUpdate[0], lCtrlPntPosUpdate[1], lCtrlPntPosUpdate[2])

#------------ create controller wrapper -----------
class oControl(naming.oName):
	"""docstring for oControl"""
	def __init__(self, *args):
		super(oControl, self).__init__(*args)
		self.args = args

	def getCtrlInfo(self, sNode):
		pass

		
		
		

#------------ create controller functions -----------
def create(sPart, sSide = 'middle', iIndex = None, bSub = False, iStacks = 1, sParent = None, sPos = None, sShape = 'cube', fSize = 1, sColor = None, lLockHideAttrs = []):
	## zero grp
	sZero = naming.oName(sType = 'zero', sSide = sSide, sPart = sPart, iIndex = iIndex).sName
	sZero = transforms.createTransformNode(sZero, sParent = sParent)

	## passer grp
	sPasser = naming.oName(sType = 'passer', sSide = sSide, sPart = sPart, iIndex = iIndex).sName
	sPasser = transforms.createTransformNode(sPasser, sParent = sZero)

	## stacks grp
	sParenStack = sPasser
	for i in range(iStacks):
		sStack = naming.oName(sType = 'stack', sSide = sSide, sPart = sPart, iIndex = iIndex, iSuffix = i + 1).sName
		sStack = transforms.createTransformNode(sStack, sParent = sParenStack)
		sParenStack = sStack

	## ctrl
	oCtrl = naming.oName(sType = 'ctrl', sSide = sSide, sPart = sPart, iIndex = iIndex)
	sCtrl = oCtrl.sName
	sCtrl = transforms.createTransformNode(sCtrl, lLockHideAttrs = lLockHideAttrs, sParent = sParenStack)

	## sub Ctrl
	if bSub:
		cmds.addAttr(sCtrl, ln = 'subCtrlVis', at = 'long', keyable = False, min = 0, max = 1, dv = 0)
		cmds.setAttr('%s.subCtrlVis' %sCtrl, channelBox = True)
		sSub = naming.oName(sType = 'ctrl', sSide = sSide, sPart = '%sSub' %sPart, iIndex = iIndex).sName
		sSub = transforms.createTransformNode(sSub, lLockHideAttrs = lLockHideAttrs, sParent = sCtrl)
		attributes.connectAttrs(['%s.subCtrlVis' %sCtrl], ['%s.v' %sSub], bForce = True)

	## add shape
	if sColor:
		if isinstance(sColor, basestring):
			iColor = controlShapeDict.dColors[sColor]
		else:
			iColor = sColor
	else:
		if 'm' in oCtrl.sSide:
			iColor = controlShapeDict.dColors['yellow']
		elif 'l' in oCtrl.sSide:
			iColor = controlShapeDict.dColors['blue']
		else:
			iColor = controlShapeDict.dColors['red']

	dCtrlShapeInfo = {
						'lCtrlPnts': controlShapeDict.dCtrlShapes[sShape]['lCtrlPnts'],
						'lKnots': controlShapeDict.dCtrlShapes[sShape]['lKnots'],
						'bPeriodic': controlShapeDict.dCtrlShapes[sShape]['bPeriodic'],
						'iDegree': controlShapeDict.dCtrlShapes[sShape]['iDegree'],
						'bOverride': True,
						'iOverrideType': 0,
						'iColor': iColor
						}

	addCtrlShape([sCtrl], '%sShape' %sCtrl, bVis = True, dCtrlShapeInfo = dCtrlShapeInfo)
	scaleCtrlShape(sCtrl, fScale = fSize)
	if bSub:
		addCtrlShape([sSub], '%sShape' %sSub, bVis = True, dCtrlShapeInfo = dCtrlShapeInfo)
		scaleCtrlShape(sSub, fScale = fSize * 0.9)

	if sPos:
		transforms.transformSnap([sPos, sZero])

	## write control info
	cmds.addAttr(sCtrl, ln = 'iStacks', at = 'long', dv = iStacks)
	cmds.addAttr(sCtrl, ln = 'sSub', dt = 'string')
	cmds.setAttr('%s.iStacks' %sCtrl, lock = True)
	if bSub:
		cmds.setAttr('%s.sSub' %sCtrl, sSub, type = 'string', lock = True)
	else:
		cmds.setAttr('%s.sSub' %sCtrl, '', type = 'string', lock = True)

#------------ create controller functions end -----------
	


#------------ save & load ctrlShape functions -----------
def getCtrlShapeInfo(sCtrl):
	sCtrlShape = getCtrlShape(sCtrl)
	
	lCtrlPnts = __getCtrlShapeControlPoints(sCtrlShape)
	lKnots = __getCtrlShapeKnots(sCtrlShape)
	bPeriodic = bool(cmds.getAttr('%s.form' %sCtrlShape))
	iDegree = cmds.getAttr('%s.degree' %sCtrlShape)
	bOverride = cmds.getAttr('%s.overrideEnabled' %sCtrlShape)
	iOverrideType = cmds.getAttr('%s.overrideDisplayType' %sCtrlShape)
	iColor = cmds.getAttr('%s.overrideColor' %sCtrlShape)

	dCtrlShapeInfo = {sCtrl:
						{
							'sCtrlShape': sCtrlShape,
							'lCtrlPnts': lCtrlPnts,
							'lKnots': lKnots,
							'bPeriodic': bPeriodic,
							'iDegree': iDegree,
							'bOverride': bOverride,
							'iOverrideType': iOverrideType,
							'iColor': iColor
						}
					 }

	return dCtrlShapeInfo

def getCtrlShapeInfoFromList(lCtrls):
	dCtrlShapeInfo = {}
	for sCtrl in lCtrls:
		dCtrlShapeInfoEach = getCtrlShapeInfo(sCtrl)
		dCtrlShapeInfo.update(dCtrlShapeInfoEach)
	return dCtrlShapeInfo

def saveCtrlShapeInfo(lCtrls, sPath):
	dCtrlShapeInfo = getCtrlShapeInfoFromList(lCtrls)
	files.writeJsonFile(sPath, dCtrlShapeInfo)

def buildCtrlShape(sCtrl, dCtrlShapeInfo, bColor = True):
	if cmds.objExists(sCtrl):
		sCtrlShape = getCtrlShape(sCtrl)
		if sCtrlShape:
			iColor = cmds.getAttr('%s.overrideColor' %sCtrlShape)
			cmds.delete(sCtrlShape)
		else:
			iColor = None
		sCtrlShape = dCtrlShapeInfo['sCtrlShape']
		addCtrlShape([sCtrl], sCtrlShape, dCtrlShapeInfo = dCtrlShapeInfo)
		if not bColor and iColor:
			cmds.setAttr('%s.overrideColor' %sCtrlShape, iColor)

def buildCtrlShapesFromCtrlShapeInfo(sPath):
	dCtrlShapeInfo = files.readJsonFile(sPath)

	for sCtrl in dCtrlShapeInfo.keys():
		buildCtrlShape(sCtrl, dCtrlShapeInfo[sCtrl], bColor = True)
#------------ save & load ctrlShape functions end -----------

#### Sub Functions
def __getCtrlShapeControlPoints(sCtrlShape):
	iCtrlPnts = cmds.getAttr('%s.controlPoints' %sCtrlShape, s = 1)
	lCtrlPnts = []
	for i in range(0, iCtrlPnts):
		lCtrlPntEach = cmds.getAttr('%s.controlPoints[%d]' %(sCtrlShape, i))[0]
		lCtrlPnts.append(lCtrlPntEach)
	return lCtrlPnts

def __getCtrlShapeKnots(sCtrlShape):
	mObj = apiUtils.setMObj(sCtrlShape)
	mfnCrv = OpenMaya.MFnNurbsCurve(mObj)
	mKnots = OpenMaya.MDoubleArray()
	mfnCrv.getKnots(mKnots)

	lKnots = []
	for i in range(mKnots.length()):
		lKnots.append(mKnots[i])
	return lKnots