import maya.cmds as cmds

class baseLimbRig(object):
	"""docstring for ClassName"""
	def __init__(self):
		super(baseLimbRig, self).__init__()

		self._sModuleType = None
		self._sConnectInJnt = None
		self._sConnectInCtrl = None
		self._sConnectOutJnt = None
		self._sConnectOutCtrl = None
		self._sSide = None
		self._sSideKey = None
		self._sPart = None
		self._iIndex = None
		self._lJnts = None
		self._lCtrls = None
		self._sGrpCtrl = None
		
	@property
	def sModuleType(self):
		return self._sModuleType

	@property
	def sConnectInJnt(self):
		return self._sConnectInJnt

	@property
	def sConnectInCtrl(self):
		return self._sConnectInCtrl

	@property
	def sConnectOutJnt(self):
		return self._sConnectOutJnt

	@property
	def sConnectOutCtrl(self):
		return self._sConnectOutCtrl

	@property
	def lJnts(self):
		return self._lJnts

	@property
	def lCtrls(self):
		return self._lCtrls

	@property
	def sGrpCtrl(self):
		return self._sGrpCtrl

	@property
	def sModuleNode(self):
		return self._sModuleNode

	def _writeRigInfo(self, sModuleNode, lRigInfo, lAttrs):
		for i,sAttr in enumerate(lAttrs):
			if cmds.attributeQuery(sAttr, node = sModuleNode, ex = True):
				cmds.setAttr('%s.%s' %(sModuleNode, sAttr), lock = False)
			else:
				cmds.addAttr(sModuleNode, ln = sAttr, dt = 'string')
			cmds.setAttr('%s.%s' %(sModuleNode, sAttr), lRigInfo[i], type = 'string', lock = True)
	
	def _getRigInfo(self, sModuleNode):
		self._sModuleType = cmds.getAttr('%s.sModuleType' %sModuleNode)
		self._sConnectInJnt = cmds.getAttr('%s.sConnectInJnt' %sModuleNode)
		self._sConnectInCtrl = cmds.getAttr('%s.sConnectInCtrl' %sModuleNode)
		self._sConnectOutJnt = cmds.getAttr('%s.sConnectOutJnt' %sModuleNode)
		self._sConnectOutCtrl = cmds.getAttr('%s.sConnectOutCtrl' %sModuleNode)
		sJnts = cmds.getAttr('%s.lJnts' %sModuleNode)
		sCtrls = cmds.getAttr('%s.lCtrls' %sModuleNode)
		self._lJnts = sJnts.split(',')
		self._lCtrls = sCtrls.split(',')
		self._sGrpCtrl = cmds.getAttr('%s.sGrpCtrl' %sModuleNode)
		self._sModuleNode = cmds.getAttr('%s.sModuleNode' %sModuleNode)

	def _convertListToString(self, lList):
		sString = ''
		for sItem in lList:
			sString += '%s,' %sItem
		return sString[:-1]
