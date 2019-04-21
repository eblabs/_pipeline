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
import lib.rigging.joints as joints
import lib.modeling.geometries as geometries
# ---- import end ----

# -- import file format
import lib.common.files.files as files
fileFormat = files.readJsonFile(files.path_fileFormat)

class AnimationRig(builder.Builder):
	"""docstring for AnimationRig"""
	def __init__(self, *args, **kwargs):
		super(AnimationRig, self).__init__(*args, **kwargs)
		self._rigType = 'animationRig'

	def registertion(self):
		super(AnimationRig, self).registertion()

		# prebuild

		self.registerTask({'name': 'Import Blueprint',
						   'task': self._importBlueprint,
						   'section': 'preBuild',
						   'after': 0})

	def _baseHierarchy(self):
		super(AnimationRig, self)._baseHierarchy()

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

		cmds.connectAttr('{}.worldMatrix[0]'.format(self._ControlLocal.output), '{}.worldPosMatrix'.format(self._controlsGrp))
	
	def _importBlueprint(self):
		bpGrp = '_blueprint_'
		if not cmds.objExists(bpGrp):
			cmds.group(empty = True, name = bpGrp)
		pathBlueprints = self._rigData['blueprints']
		for pathBp in pathBlueprints:
			if pathBp.endswith(fileFormat['joint']):
				joints.loadJointsInfo(pathBp, vis = True)
			elif pathBp.endswith(fileFormat['geometry']):
				geometries.loadGeoInfo(pathBp, vis = True)
		logger.info('import blueprints successfully')