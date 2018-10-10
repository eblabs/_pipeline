# -- import for debug
import logging
debugLevel = logging.WARNING # debug level
logging.basicConfig(level=debugLevel)
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

# -- import maya lib
import maya.cmds as cmds

# -- import lib
import lib.common.naming.naming as naming
import lib.common.transforms as transforms
import lib.common.attributes as attributes
import lib.rigging.controls.controls as controls
# ---- import end ----

class MasterNode(object):
	"""
	MasterNode Hierarchy

	master
	-- deformationRig
		-- geometry
		-- skeleton
		-- rigNodes
	-- animationRig
		-- control
		-- components
	"""
	def __init__(self, *args,**kwargs):
		super(MasterNode, self).__init__()


	def create(self):
		# create groups
		attrDict = {}
		for grp in ['master', 'deformationRig', 'animationRig', 'geometryGrp',
					'skeletonGrp', 'rigNodesGrp', 'controlsGrp', 'componentsGrp']:
			NamingGrp = naming.Naming(type = grp)
			transformNode = transforms.createTransformNode(NamingGrp.name, 
														   lockHide = ['tx', 'ty', 'tz',
																	  'rx', 'ry', 'rz',
																	  'sx', 'sy', 'sz',
																	  'v'])
			attrDict.update({'_{}'.format(grp): transformNode})

		self._addAttributeFromDict(attrDict)

		# parent
		cmds.parent(self._deformationRig, self._animationRig, self._master)
		cmds.parent(self._geometryGrp, self._skeletonGrp, self._rigNodesGrp, self._deformationRig)
		cmds.parent(self._controlsGrp, self._componentsGrp, self._animationRig)

		# add attr
		# deformation rig
		attributes.addAttrs(self._deformationRig, ['geometryVis', 'skeletonVis', 'rigNodesVis'], attributeType = 'long', 
					minValue = 0, maxValue = 1, defaultValue = [1,0,0], keyable = False, channelBox = True)
		attributes.addAttrs(self._deformationRig, 'geometryType', attributeType = 'enum', 
					keyable = False, channelBox = True, enumName = 'normal:template:reference')
		
		# animation rig
		attributes.addAttrs(self._animationRig, ['controlsVis', 'jointsVis', 'rigNodesVis', 'localize'], attributeType = 'long', 
					minValue = 0, maxValue = 1, defaultValue = [1,0,0,1], keyable = False, channelBox = True)
		
		# connect attrs
		cmds.setAttr('{}.overrideEnabled'.format(self._geometryGrp), 1)
		attributes.connectAttrs(['geometryVis', 'skeletonVis', 'rigNodesVis', 'geometryType'],
								['{}.v'.format(self._geometryGrp), '{}.v'.format(self._skeletonGrp),
								 '{}.v'.format(self._rigNodesGrp), '{}.overrideDisplayTyp'.format(self._geometryGrp)],
								 driver = self._deformationRig, force = True)

		# add master control
		ControlWorld = controls.create('world', side = 'middle', parent = self._controlsGrp, lockHide = ['sx', 'sy', 'sz'],
										shape = 'crossArrowCircle')
		attributes.addAttrs(ControlWorld.name, 'rigScale', attributeType = 'float', 
					minValue = 0, defaultValue = 1, keyable = True, channelBox = True)
		attributes.addAttrs(ControlWorld.sub, 'rigScale', attributeType = 'float', 
					minValue = 0, defaultValue = 1, keyable = True, channelBox = True)
		attributes.connectAttrs('rigScale', ['sx', 'sy', 'sz'], driver = ControlWorld.name, 
								driven = ControlWorld.name, force = True)
		attributes.connectAttrs('rigScale', ['sx', 'sy', 'sz'], driver = ControlWorld.sub, 
								driven = ControlWorld.sub, force = True)

	def _addAttributeFromDict(self, attrDict):
		for key, value in attrDict.items():
			setattr(self, key, value)
		
		
