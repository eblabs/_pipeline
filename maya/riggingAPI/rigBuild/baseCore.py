## External Import
import maya.cmds as cmds
import maya.mel as mel

# rig build class
class baseCore(object):
	"""docstring for baseCore"""
	def __init__(self):
		super(baseCore, self).__init__()
		
		self.dFunctions = {'lFunctionsOrder': [], 'lFunctions': []}
		self.dRigData = {}
		self.sProject = None
		self.sAsset = None
		
	def registerFunction(self, **kwargs):
		mFunction = kwargs.get('mFunction', None)
		sName = kwargs.get('sName', None)
		sParent = kwargs.get('sParent', None)
		sAfter = kwargs.get('sAfter', None)
		sSection = kwargs.get('sSection', 'Build')
		lColor = kwargs.get('lColor', None)

		if not mFunction or not sName or not sParent:
			raise RuntimeError('No function to be registered')
		dFuncUpdate = {sName: 
								{
									'mFunction': mFunction,
									'sParent': sParent,
									'lColor': lColor,
									'sAfter': sAfter
								}
							}

		## add func to dic
		self.dFunctions['lFunctions'].append(dFuncUpdate)
		self.dFunctions['lFunctionsOrder'].append(sName)

	def importFunctions(self):
		pass

	def rigData(self):
		pass


