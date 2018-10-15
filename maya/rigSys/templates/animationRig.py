# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import builder
reload(builder)
import lib.common.naming.naming as naming
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.rigging.controls.controls as controls
import lib.rigging.constraints as constraints
# ---- import end ----

class AnimationRig(builder.Builder):
	"""docstring for AnimationRig"""
	def __init__(self):
		super(AnimationRig, self).__init__()

	def registertion(self):
		super(AnimationRig, self).registertion()

		# prebuild
		# self.registerTask({'name': 'Create New Scene',
		# 				   'task': self._createNewScene,
		# 				   'section': 'preBuild'})

		# self.registerTask({'name': 'Import Blueprint',
		# 				   'task': self._importBlueprint,
		# 				   'section': 'preBuild'})

		# self.registerTask({'name': 'Import Misc',
		# 				   'task': self._importMisc,
		# 				   'section': 'preBuild'})

		self.registerTask({'name': 'Base Hierarchy',
						   'task': self._baseHierarchy,
						   'section': 'preBuild'})

		# build

		self.registerTask({'name': 'Create Components',
						   'task': self._createComponents,
						   'section': 'build'})

		self.registerTask({'name': 'Connect Components',
						   'task': self._connectComponents,
						   'section': 'build'})

		# self.registerTask({'name': 'Space Switch',
		# 				   'task': self._spaceSwitch,
		# 				   'section': 'build'})

		# self.registerTask({'name': 'Set Default Attributes',
		# 				   'task': self._setDefaultAttributes,
		# 				   'section': 'build'})

		# postBuild

		# self.registerTask({'name': 'Load ControlShapes',
		# 				   'task': self._loadControlShapes,
		# 				   'section': 'postBuild'})

		# self.registerTask({'name': 'Hide History',
		# 				   'task': self._hideHistory,
		# 				   'section': 'postBuild'})

	def _baseHierarchy(self):
		hierarchyInfo = {'animationRig': {'name': naming.Naming(type = 'animationRig').name},
						 'controlsGrp': {'name': naming.Naming(type = 'controlsGroup', 
						 									  side = 'middle', 
						 									  part = 'animationRig').name,
						 				'parent': 'animationRig'},
						 'componentsGrp': {'name': naming.Naming(type = 'componentsGrp', 
						 									  	 side = 'middle', 
						 									  	 part = 'animationRig').name,
						 				   'parent': 'animationRig'},
						 'rigNodesGrp': {'name': naming.Naming(type = 'rigNodesGrp', 
						 									   side = 'middle', 
						 									   part = 'animationRig').name,
						 				 'parent': 'animationRig',
						 				 'vis': False},
						 'rigLocal': {'name': naming.Naming(type = 'rigLocal', 
						 									side = 'middle', 
						 									part = 'animationRig').name,
						 			  'parent': 'rigNodesGrp'},
						 'rigWorld': {'name': naming.Naming(type = 'rigWorld', 
						 									side = 'middle', 
						 									part = 'animationRig').name,
						 			  'parent': 'rigNodesGrp'},
						 }
		self._buildGroupHierarchy(hierarchyInfo)

		# create world control
		self._ControlWorld = controls.create('world', side = 'middle', parent = self._controlsGrp, lockHide = ['sx', 'sy', 'sz'],
										shape = 'crossArrowCircle', size = 12)
		self._ControlLayout = controls.create('layout', side = 'middle', parent = self._controlsGrp, lockHide = ['sx', 'sy', 'sz'],
										shape = 'circle', size = 7)
		self._ControlLocal = controls.create('local', side = 'middle', parent = self._controlsGrp, lockHide = ['sx', 'sy', 'sz'],
										shape = 'circle', size = 6)

		constraints.matrixConnect(self._ControlWorld.name, self._ControlWorld.matrixWorldAttr, self._ControlLayout.zero)
		constraints.matrixConnect(self._ControlLayout.name, self._ControlLayout.matrixWorldAttr, self._ControlLocal.zero)

		for Ctrl in [self._ControlWorld, self._ControlLayout, self._ControlLocal]:
			cmds.addAttr(Ctrl.name, ln = 'rigSize', min = 0, dv = 1, keyable = True)
			attributes.connectAttrs('rigSize', ['sx', 'sy', 'sz'], driver = Ctrl.name, driven = Ctrl.name)
		
		attributes.addAttrs(self._ControlWorld.name, ['layoutControlVis', 'localControlVis'], attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = 0, keyable = False, channelBox = True)
		attributes.connectAttrs(['layoutControlVis', 'localControlVis'], ['{}.v'.format(self._ControlLayout.zero), '{}.v'.format(self._ControlLocal.zero)], 
								driver = self._ControlWorld.name)

		cmds.addAttr(self._controlsGrp, ln = 'worldPosMatrix', at = 'matrix')
		cmds.connectAttr('{}.worldMatrix[0]'.format(self._ControlLocal.output), '{}.worldPosMatrix'.format(self._controlsGrp))
		self._worldPosMatrixPlug = '{}.worldPosMatrix'.format(self._controlsGrp)

		constraints.matrixConnect(self._controlsGrp, 'worldPosMatrix', [self._componentsGrp, self._rigLocal], force = True)

		# vis attrs
		attributes.addAttrs(self._animationRig, ['jointsVis', 'controlsVis', 'rigNodesVis', 'localization'], attributeType = 'long', minValue = 0, maxValue = 1, 
							defaultValue = [0, 1, 0, 1], keyable = False, channelBox = True)
		attributes.connectAttrs('rigNodesVis', 'v', driver = self._animationRig, driven = self._rigNodesGrp)