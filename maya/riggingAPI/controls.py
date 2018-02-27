## External Import
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
## libs Import
import common.apiUtils as apiUtils
reload(apiUtils)
import common.files as files
import namingAPI.naming as naming
import common.transforms as transforms
reload(transforms)
import common.attributes as attributes
import common.maths as maths
import controlShapeDict
reload(transforms)
reload(naming)
#### Functions
def getCtrlShape(sCtrl):
	'''
	return the first shape node of a control
	'''
	lCtrlShapes = cmds.listRelatives(sCtrl, s = True)
	if lCtrlShapes:
		sCtrlShape = lCtrlShapes[0]
	else:
		sCtrlShape = None
	return sCtrlShape

def addCtrlShape(lCtrls, sCtrlShape, bVis = True, dCtrlShapeInfo = None, bTop = False):
	'''
	add a shape node to a list of controls

	lCtrls: a list of transform nodes need to add the shape node
	sCtrlShape: shape node name
	bVis: shape node's visibility, True/False
	dCtrlShapeInfo: a dictionary contain all the shape node's shape information
	bTop: either the shape node will be on top of other shape nodes nor not, True/False
	'''
	if not cmds.objExists(sCtrlShape):
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
	else:
		sCrv = None

	cmds.setAttr('%s.overrideEnabled' %sCtrlShape, bOverride)
	cmds.setAttr('%s.overrideDisplayType' %sCtrlShape, iOverrideType)
	cmds.setAttr('%s.overrideColor' %sCtrlShape, iColor)

	if not bVis:
		cmds.setAttr('%s.v' %sCtrlShape, lock = False)
		cmds.setAttr('%s.v' %sCtrlShape, 0)
		cmds.setAttr('%s.v' %sCtrlShape, lock = True)
	for sCtrl in lCtrls:
		cmds.parent(sCtrlShape, sCtrl, add = True, s = True)
	if bTop:
		cmds.reorder(sCtrlShape, f = True)
	if sCrv:
		cmds.delete(sCrv)

def scaleCtrlShape(sCtrl, fScale = 1):
	'''
	scale the shape node in the control's transform space
	'''
	lPosPivot = cmds.xform(sCtrl, q = True, t = True, ws = True)
	sCtrlShape = getCtrlShape(sCtrl)
	if sCtrlShape:
		lCtrlPnts = __getCtrlShapeControlPoints(sCtrlShape)
		for i, lCtrlPntPos in enumerate(lCtrlPnts):
			vCtrlPnt = maths.vector(lPosPivot, lCtrlPntPos)
			vCtrlPnt = maths.vectorScale(vCtrlPnt, fScale)
			lCtrlPntPosUpdate = maths.getPointFromVectorAndPoint(lPosPivot, vCtrlPnt)
			cmds.setAttr('%s.controlPoints[%d]' %(sCtrlShape, i), lCtrlPntPosUpdate[0], lCtrlPntPosUpdate[1], lCtrlPntPosUpdate[2])

def mirrorCtrlShape(sCtrl):
	'''
	mirror control's shape node to the other side
	'''
	oName = naming.oName(sCtrl)
	sCtrlShape = getCtrlShape(sCtrl)
	oCtrlShapeName = naming.oName(sCtrlShape)
	bMirror = True
	if 'left' in oName.sSideKey:
		oName.sSide = oName.sSideKey.replace('left', 'right')
		oCtrlShapeName.sSide = oCtrlShapeName.sSideKey.replace('left', 'right')
	elif 'right' in oName.sSideKey:
		oName.sSide = oName.sSideKey.replace('right', 'left')
		oCtrlShapeName.sSide = oCtrlShapeName.sSideKey.replace('right', 'left')
	else:
		bMirror = False
	if bMirror:
		sCtrlMirror = oName.sName				
		sCtrlShapeMirror = oCtrlShapeName.sName
		if cmds.objExists(sCtrlShapeMirror):
			iColor = cmds.getAttr('%s.overrideColor' %sCtrlShapeMirror)
		else:
			iColor = None
		dCtrlShapeInfo = getCtrlShapeInfo(sCtrl)

		lCtrlPnts = dCtrlShapeInfo[sCtrl]['lCtrlPnts']
		lCtrlPntsMirror = []
		for lCtrlPnt in lCtrlPnts:
			lCtrlPntWorld = transforms.convertPointTransformFromObjectToWorld(lCtrlPnt, sCtrl)
			lCtrlPntWorld[0] = -1 * lCtrlPntWorld[0]
			lCtrlPntMirror = transforms.convertPointTransformFromWorldToObject(lCtrlPntWorld, sCtrlMirror)
			lCtrlPntsMirror.append(lCtrlPntMirror)
		dCtrlShapeInfo[sCtrl]['lCtrlPnts'] = lCtrlPntsMirror

		dCtrlShapeInfo[sCtrl]['sCtrlShape'] = sCtrlShapeMirror
		dCtrlShapeInfo[sCtrl]['iColor'] = iColor

		buildCtrlShape(sCtrlMirror, dCtrlShapeInfo[sCtrl], bColor = True, bTop = True)




#------------ create controller wrapper -----------
class oControl(object):
	'''
	a wrapper for controller

	control's hierarchy: sZero/sPasser/sStack01/.../sName/sSub

	property:
	sName: return the control's name
	sSide: return the control's side
	sPart: return the control's part
	iIndex: return the control's index
	sZero: return the control's zero group
	sPasser: return the control's passer group
	lStacks: return the control's stack groups list
	iStacks: return how many stack groups the control have
	sSub: return the control's sub control name
	bSub: return whether the control has a sub control or not
	sOutput: return the node used to constraint with other objects
	sSideKey: return the control's side's full name

	setAttr:
	sSide: set the control's side
	sPart: set the control's part name
	iIndex: set the control's index
	iStacks: set how many stacks the control has
	bSub: set if the control has a sub control or not
	'''
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

	@property
	def sOutput(self):
		return self.__sOutput

	@property
	def sSideKey(self):
		sKey = getFullNameFromKey(self.__sSide, 'side')
		return sKey

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

		self.__sOutput = cmds.getAttr('%s.sOutput' %sCtrl)

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

		self.__sMultMatrixOutputLocal = naming.oName(sType = 'multMatrix', sSide = self.__sSide, sPart = '%sMatrixOutputLocal' %self.__sPart, iIndex = self.__iIndex).sName
		self.__sMultMatrixOutputWorld = naming.oName(sType = 'multMatrix', sSide = self.__sSide, sPart = '%sMatrixOutputWorld' %self.__sPart, iIndex = self.__iIndex).sName
		self.__sMultMatrixStacks = naming.oName(sType = 'multMatrix', sSide = self.__sSide, sPart = '%sStacksMatrixOutput' %self.__sPart, iIndex = self.__iIndex).sName
	

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

		sMultMatrixOutputLocal = naming.oName(sType = 'multMatrix', sSide = self.__sSide, sPart = '%sMatrixOutputLocal' %self.__sPart, iIndex = self.__iIndex).sName
		cmds.rename(self.__sMultMatrixOutputLocal, sMultMatrixOutputLocal)

		sMultMatrixOutputWorld = naming.oName(sType = 'multMatrix', sSide = self.__sSide, sPart = '%sMatrixOutputWorld' %self.__sPart, iIndex = self.__iIndex).sName
		cmds.rename(self.__sMultMatrixOutputWorld, sMultMatrixOutputWorld)

		sMultMatrixStacks = naming.oName(sType = 'multMatrix', sSide = self.__sSide, sPart = '%sStacksMatrixOutput' %self.__sPart, iIndex = self.__iIndex).sName
		cmds.rename(self.__sMultMatrixStacks, sMultMatrixStacks)

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

		cmds.delete(self.__sMultMatrixStacks)
		cmds.createNode('multMatrix', name = self.__sMultMatrixStacks)
		for i in range(iKey):
			iNum = iKey - i
			sStack = naming.oName(sType = 'stack', sSide = self.__sSide, sPart = self.__sPart, iIndex = self.__iIndex, iSuffix = iNum).sName
			cmds.connectAttr('%s.matrix' %sStack, '%s.matrixIn[%d]' %(self.__sMultMatrixStacks, i))
		cmds.connectAttr('%s.matrixSum' %self.__sMultMatrixStacks, '%s.matrixIn[2]' %self.__sMultMatrixOutputLocal)

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
	'''
	create control function

	return control wrapper

	sPart: control's part name
	sSide: control's side name
	iIndex: control's index
	bSub: whether the control will have sub control or not
	iStacks: how many stack groups the control will have
	sParent: where the control should be parented
	sPos: where the control would be snapped to
	iRotateOrder: set the control's rotateOrder
	sShape: control's shape
	fSize: control's shape's size
	sColor: control's shape color string/index
	lLockHideAttrs: list of attributes should be locked and hidden
	'''
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

	## output
	sOutput = naming.oName(sType = 'grp', sSide = sSide, sPart = '%sOutput' %sPart, iIndex = iIndex).sName
	sOutput = transforms.createTransformNode(sOutput, lLockHideAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'], sParent = sCtrl, iRotateOrder = iRotateOrder)

	## sub Ctrl
	if bSub:
		cmds.addAttr(sCtrl, ln = 'subCtrlVis', at = 'long', keyable = False, min = 0, max = 1, dv = 0)
		cmds.setAttr('%s.subCtrlVis' %sCtrl, channelBox = True)
		sSub = naming.oName(sType = 'ctrl', sSide = sSide, sPart = '%sSub' %sPart, iIndex = iIndex).sName
		sSub = transforms.createTransformNode(sSub, lLockHideAttrs = lLockHideAttrs, sParent = sCtrl, iRotateOrder = iRotateOrder)
		attributes.connectAttrs(['%s.subCtrlVis' %sCtrl], ['%s.v' %sSub], bForce = True)
		attributes.connectAttrs(['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], sDriver = sSub, sDriven = sOutput, bForce = True)

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
	cmds.addAttr(sCtrl, ln = 'sOutput', dt = 'string')
	cmds.addAttr(sCtrl, ln = 'iStacks', at = 'long', dv = iStacks)
	cmds.addAttr(sCtrl, ln = 'sSub', dt = 'string')
	cmds.setAttr('%s.sOutput' %sCtrl, sOutput, type = 'string', lock = True)
	cmds.setAttr('%s.iStacks' %sCtrl, lock = True)
	if bSub:
		cmds.setAttr('%s.sSub' %sCtrl, sSub, type = 'string', lock = True)
	else:
		cmds.setAttr('%s.sSub' %sCtrl, '', type = 'string', lock = True)

	##### matrix
	cmds.addAttr(sCtrl, ln = 'matrixOutputLocal', at = 'matrix')
	cmds.addAttr(sCtrl, ln = 'inverseMatrixOutputLocal', at = 'matrix')
	cmds.addAttr(sCtrl, ln = 'matrixOutputWorld', at = 'matrix')
	cmds.addAttr(sCtrl, ln = 'inverseMatrixOutputWorld', at = 'matrix')

	sInverseMatrixOutputLocal = cmds.createNode('inverseMatrix', name = naming.oName(sType = 'inverseMatrix', sSide = sSide, sPart = '%sInverseMatrixOutputLocal' %sPart, iIndex = iIndex).sName)
	cmds.connectAttr('%s.matrixOutputLocal' %sCtrl, '%s.inputMatrix' %sInverseMatrixOutputLocal)
	cmds.connectAttr('%s.outputMatrix' %sInverseMatrixOutputLocal, '%s.inverseMatrixOutputLocal' %sCtrl)

	sInverseMatrixOutputWorld = cmds.createNode('inverseMatrix', name = naming.oName(sType = 'inverseMatrix', sSide = sSide, sPart = '%sInverseMatrixOutputWorld' %sPart, iIndex = iIndex).sName)
	cmds.connectAttr('%s.matrixOutputWorld' %sCtrl, '%s.inputMatrix' %sInverseMatrixOutputWorld)
	cmds.connectAttr('%s.outputMatrix' %sInverseMatrixOutputWorld, '%s.inverseMatrixOutputWorld' %sCtrl)

	sMultMatrixLocal = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = sSide, sPart = '%sMatrixOutputLocal' %sPart, iIndex = iIndex).sName)
	sMultMatrixWorld = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = sSide, sPart = '%sMatrixOutputWorld' %sPart, iIndex = iIndex).sName)
	sMultMatrixStacks = cmds.createNode('multMatrix', name = naming.oName(sType = 'multMatrix', sSide = sSide, sPart = '%sStacksMatrixOutput' %sPart, iIndex = iIndex).sName)

	cmds.connectAttr('%s.matrix' %sOutput, '%s.matrixIn[0]' %sMultMatrixLocal)
	cmds.connectAttr('%s.matrix' %sCtrl, '%s.matrixIn[1]' %sMultMatrixLocal)
	cmds.connectAttr('%s.matrixSum' %sMultMatrixStacks, '%s.matrixIn[2]' %sMultMatrixLocal)
	cmds.connectAttr('%s.matrix' %sPasser, '%s.matrixIn[3]' %sMultMatrixLocal)
	cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixOutputLocal' %sCtrl)

	for i in range(iStacks):
		iNum = iStacks - i
		sStack = naming.oName(sType = 'stack', sSide = sSide, sPart = sPart, iIndex = iIndex, iSuffix = iNum).sName
		cmds.connectAttr('%s.matrix' %sStack, '%s.matrixIn[%d]' %(sMultMatrixStacks, i))

	cmds.connectAttr('%s.matrixSum' %sMultMatrixLocal, '%s.matrixIn[0]' %sMultMatrixWorld)
	cmds.connectAttr('%s.matrix' %sZero, '%s.matrixIn[1]' %sMultMatrixWorld)
	cmds.connectAttr('%s.matrixSum' %sMultMatrixWorld, '%s.matrixOutputWorld' %sCtrl)

	oCtrl = oControl(sCtrl)
	return oCtrl

#------------ create controller functions end -----------
	


#------------ save & load ctrlShape functions -----------
def getCtrlShapeInfo(sCtrl):
	'''
	get control shape node info
	retrun a dictionary

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
	'''
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
	'''
	return a dictionary contain shape node info for all the controls in the list
	'''
	dCtrlShapeInfo = {}
	for sCtrl in lCtrls:
		dCtrlShapeInfoEach = getCtrlShapeInfo(sCtrl)
		dCtrlShapeInfo.update(dCtrlShapeInfoEach)
	return dCtrlShapeInfo

def saveCtrlShapeInfo(lCtrls, sPath):
	'''
	save control shape info as a json file to the path
	'''
	dCtrlShapeInfo = getCtrlShapeInfoFromList(lCtrls)
	files.writeJsonFile(sPath, dCtrlShapeInfo)

def buildCtrlShape(sCtrl, dCtrlShapeInfo, bColor = True, bTop = False):
	'''
	build control shape node from given info

	sCtrl: the control's transform node, the shape node will be added to this transform
	dCtrlShapeInfo: the shape info for the shape node
	bColor: either override the color or not
	bTop: either put this shape node on top of other shape nodes or not
	'''
	if cmds.objExists(sCtrl):
		sCtrlShape = getCtrlShape(sCtrl)
		if sCtrlShape:
			iColor = cmds.getAttr('%s.overrideColor' %sCtrlShape)
			cmds.delete(sCtrlShape)
		else:
			iColor = None
		sCtrlShape = dCtrlShapeInfo['sCtrlShape']
		addCtrlShape([sCtrl], sCtrlShape, dCtrlShapeInfo = dCtrlShapeInfo, bTop = bTop)
		if not bColor and iColor:
			cmds.setAttr('%s.overrideColor' %sCtrlShape, iColor)

def buildCtrlShapesFromCtrlShapeInfo(sPath):
	'''
	build controls shapes from given json file
	'''
	dCtrlShapeInfo = files.readJsonFile(sPath)
	
	for sCtrl in dCtrlShapeInfo.keys():
		buildCtrlShape(sCtrl, dCtrlShapeInfo[sCtrl], bColor = True, bTop = True)
#------------ save & load ctrlShape functions end -----------

#### Sub Functions
def __getCtrlShapeControlPoints(sCtrlShape):
	iCtrlPnts = cmds.getAttr('%s.controlPoints' %sCtrlShape, s = 1)
	lCtrlPnts = []
	for i in range(0, iCtrlPnts):
		lCtrlPntEach = cmds.getAttr('%s.controlPoints[%d]' %(sCtrlShape, i))[0]
		lCtrlPnts.append([lCtrlPntEach[0], lCtrlPntEach[1], lCtrlPntEach[2]])
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