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
class oControl(object):
	"""docstring for oControl"""
	def __init__(self, sCtrl):
		self.__getCtrlInfo(sCtrl)

	@property
	def sName(self):
		return self.__sName

	@property
	def sSide(self):
		return self.__sSide

	@property
	def sPart(self):
		return self.__sPart

	@property
	def iIndex(self):
		return self.__iIndex

	@property
	def sZero(self):
		return self.__sZero

	@property
	def sPasser(self):
		return self.__sPasser

	@property
	def lStacks(self):
		return self.__lStacks

	@property
	def iStacks(self):
		return self.__iStacks

	@property
	def sSub(self):
		return self.__sSub

	@property
	def bSub(self):
		return self.__bSub

	@sSide.setter
	def sSide(self, sKey):
		if sKey:
			sName = naming.getKeyFromNamePart(sKey, 'side')
			self.__sSide = sName
			self.__renameCtrl()

	@sPart.setter
	def sPart(self, sKey):
		if sKey:
			self.__sPartt = sKey
			self.__renameCtrl()

	@iIndex.setter
	def iIndex(self, iKey):
		if iKey:
			self.__iIndex = iKey
			self.__renameCtrl()

	@iStacks.setter
	def iStacks(self, iKey):
		if iKey < 1:
			iKey = 1
		if self.__iStacks != iKey:
			self.__updateStacks(iKey)

	@bSub.setter
	def bSub(self, bKey):
		if self.__bSub != bool(bKey):
			self.__updateSub()

	def __getCtrlInfo(self, sCtrl):
		self.__sName = sCtrl

		oCtrlName = naming.oName(sCtrl)

		self.__sSide = oCtrlName.sSide
		self.__sPart = oCtrlName.sPart
		self.__iIndex = oCtrlName.iIndex
		self.__iSuffix = oCtrlName.iSuffix

		sSub = cmds.getAttr('%s.sSub' %sCtrl)
		if sSub:
			self.__sSub = sSub
			self.__bSub = True
		else:
			self.__sSub = None
			self.__bSub = False

		iStacks = cmds.getAttr('%s.iStacks' %sCtrl)
		self.__lStacks = []
		for i in range(iStacks):
			sStack = naming.oName(sType = 'stack', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex, iSuffix = i + 1).sName
			self.__lStacks.append(sStack)
		self.__iStacks = iStacks

		self.__sPasser = naming.oName(sType = 'passer', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex).sName
		self.__sZero = naming.oName(sType = 'zero', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex).sName

	def __renameCtrl(self):
		sZero = naming.oName(sType = 'zero', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex).sName
		cmds.rename(self.__sZero, sZero)
		sPasser = naming.oName(sType = 'passer', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex).sName
		cmds.rename(self.__sPasser, sPasser)
		lStacks = []
		for i in range(len(self.__lStacks)):
			sStack = naming.oName(sType = 'stack', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex, iSuffix = i + 1).sName
			cmds.rename(self.__lStacks[i], sStack)
			lStacks.append(sStack)
		sCtrl = naming.oName(sType = 'ctrl', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex).sName
		cmds.rename(self.__sName, sCtrl)
		if self.__sSub:
			sSub = naming.oName(sType = 'ctrl', sSide = self.__sSide, sPart = '%sSub' %self.__sPart, iIndex = self.__iIndex).sName
			cmds.rename(self.__sSub, sSub)
			cmds.setAttr('%s.sSub' %sCtrl, lock = False)
			cmds.setAttr('%s.sSub' %sCtrl, sSub, type = 'string', lock = True)
		self.__getCtrlInfo(sCtrl)

	def __updateStacks(self, iKey):
		if iKey < self.__iStacks:
			lChilds = cmds.listRelatives(self.__lStacks[-1], c = True, type = 'transform')
			cmds.parent(lChilds, self.__lStacks[iKey - 1])
			cmds.delete(self.__lStacks[iKey:])
		else:
			sParentStack = self.__lStacks[-1]
			lChilds = cmds.listRelatives(self.__lStacks[-1], c = True, type = 'transform')
			for i in range(self.__iStacks, iKey):
				sStack = naming.oName(sType = 'stack', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex, iSuffix = i + 1).sName
				sStack = transforms.createTransformNode(sStack, sParent = sParentStack)
				transforms.transformSnap([sParentStack], [sStack])
				sParentStack = sStack
			cmds.parent(lChilds, sParentStack)
		cmds.setAttr('%s.iStacks' %self.__sName, lock = False)
		cmds.setAttr('%s.iStacks' %self.__sName, iKey, lock = True)
		cmds.select(self.__sName)
		self.__getCtrlInfo(self.__sName)

	def __updateSub(self):
		cmds.setAttr('%s.sSub' %self.__sName, lock = False)
		if self.__bSub:
			lChilds = cmds.listRelatives(self.__sSub, c = True, type = 'transform')
			print lChilds
			if lChilds:
				cmds.parent(lChilds, self.__sName)
			cmds.delete(self.__sSub)
			cmds.setAttr('%s.sSub' %self.__sName, '', type = 'string', lock = True)
			cmds.deleteAttr('%s.subCtrlVis' %self.__sName)
		else:
			cmds.addAttr(self.__sName, ln = 'subCtrlVis', at = 'long', keyable = False, min = 0, max = 1, dv = 0)
			cmds.setAttr('%s.subCtrlVis' %self.__sName, channelBox = True)
			sSub = naming.oName(sType = 'ctrl', sSide = self.__sSide, sPart = '%sSub' %self.__sPart, iIndex = self.__iIndex).sName
			sSub = transforms.createTransformNode(sSub, sParent = self.__sName)
			transforms.transformSnap([self.__sName], [sSub])
			attributes.connectAttrs(['%s.subCtrlVis' %self.__sName], ['%s.v' %sSub], bForce = True)
			for sAttr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
				if cmds.getAttr('%s.%s' %(self.__sName, sAttr), lock = True):
					cmds.setAttr('%s.%s' %(sSub, sAttr), keyable = False, lock = True, channelBox = False)
			dCtrlShapeInfo = getCtrlShapeInfo(self.__sName)
			addCtrlShape([sSub], '%sShape' %sSub, bVis = True, dCtrlShapeInfo = dCtrlShapeInfo[self.__sName])
			scaleCtrlShape(sSub, fScale = 0.9)
			cmds.setAttr('%s.sSub' %self.__sName, sSub, type = 'string', lock = True)
		cmds.select(self.__sName)
		self.__getCtrlInfo(self.__sName)



		
		

#------------ create controller functions -----------
def create(sPart, sSide = 'middle', iIndex = None, bSub = False, iStacks = 1, sParent = None, sPos = None, iRotateOrder = 0, sShape = 'cube', fSize = 1, sColor = None, lLockHideAttrs = []):
	## zero grp
	sZero = naming.oName(sType = 'zero', sSide = sSide, sPart = sPart, iIndex = iIndex).sName
	sZero = transforms.createTransformNode(sZero, sParent = sParent, iRotateOrder = iRotateOrder)

	## passer grp
	sPasser = naming.oName(sType = 'passer', sSide = sSide, sPart = sPart, iIndex = iIndex).sName
	sPasser = transforms.createTransformNode(sPasser, sParent = sZero, iRotateOrder = iRotateOrder)

	## stacks grp
	sParentStack = sPasser
	for i in range(iStacks):
		sStack = naming.oName(sType = 'stack', sSide = sSide, sPart = sPart, iIndex = iIndex, iSuffix = i + 1).sName
		sStack = transforms.createTransformNode(sStack, sParent = sParentStack, iRotateOrder = iRotateOrder)
		sParentStack = sStack

	## ctrl
	oCtrl = naming.oName(sType = 'ctrl', sSide = sSide, sPart = sPart, iIndex = iIndex)
	sCtrl = oCtrl.sName
	sCtrl = transforms.createTransformNode(sCtrl, lLockHideAttrs = lLockHideAttrs, sParent = sParentStack, iRotateOrder = iRotateOrder)

	## sub Ctrl
	if bSub:
		cmds.addAttr(sCtrl, ln = 'subCtrlVis', at = 'long', keyable = False, min = 0, max = 1, dv = 0)
		cmds.setAttr('%s.subCtrlVis' %sCtrl, channelBox = True)
		sSub = naming.oName(sType = 'ctrl', sSide = sSide, sPart = '%sSub' %sPart, iIndex = iIndex).sName
		sSub = transforms.createTransformNode(sSub, lLockHideAttrs = lLockHideAttrs, sParent = sCtrl, iRotateOrder = iRotateOrder)
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

	oCtrl = oControl(sCtrl)
	return oCtrl

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