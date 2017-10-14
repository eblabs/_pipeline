## External Import
import maya.cmds as cmds
import maya.mel as mel

# rig build class
class baseCore(object):
	"""docstring for baseCore"""
	def __init__(self):
		super(baseCore, self).__init__()
		
		self.dFunctions_pre = {}
		self.dFunctions_build = {}
		self.dFunctions_post = {}
		
	def registerFunction(self, **kwargs):
		mFunction = kwargs.get('mFunction', None)
		sName = kwargs.get('sName', None)
		sParent = kwargs.get('sParent', None)
		sAfter = kwargs.get('sAfter', None)
		sSection = kwargs.get('sSection', 'Build')
		lColor = kwargs.get('lColor', None)

		if not mFunction or not sName:
			raise RuntimeError('No function to be registered')
		dFuncUpdate = {sName: 
								{
									'mFunction': mFunction,
									'sParent': sParent,
									'lColor': lColor,
									'iIndex': 0,
								}
							}
		
		if sSection == 'Pre Build':
			dFuncAll = self.dFunctions_pre
		elif sSection == 'Build':
			dFuncAll = self.dFunctions_build
		else:
			dFuncAll = self.dFunctions_post

		## reorder index
		lFunctions = dFuncAll.keys()
		iFunNum = len(lFunctions)
		if not sAfter:
			dFuncUpdate[sName]['iIndex'] = iFunNum
		elif: isinstance(sAfter, str):
			iAfter = dFuncAll[sAfter]['iIndex']
			dFuncUpdate[sName]['iIndex'] = iAfter + 1
			for sFunc in lFunctions:
				iIndexFunc = dFuncAll[sFunc]['iIndex']
				if iIndexFunc > iAfter:
					dFuncAll[sFunc]['iIndex'] += 2
		elif: isinstance(sAfter, int):
			if sAfter == 0:
				dFuncUpdate[sName]['iIndex'] = 0
				for sFunc in lFunctions:
					dFuncAll[sFunc]['iIndex'] += 1
			elif sAfter >= iFunNum:
				dFuncUpdate[sName]['iIndex'] = iFunNum
			else:
				for sFunc in lFunctions:
					iIndexFunc = dFuncAll[sFunc]['iIndex']
					if iIndexFunc >= sAfter:
						dFuncAll[sFunc]['iIndex'] += 2
				dFuncUpdate[sName]['iIndex'] = sAfter

		## add func to dic
		dFuncAll.update(dFuncUpdate)

	def importFunctions(self):
		pass


